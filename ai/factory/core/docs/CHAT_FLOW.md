# Chat Endpoint Flow

A trace of every file and function called when a user sends a message to a bot.

---

## Entry Point

**`POST /api/{bot_id}/chat/stream`** (streaming) or **`POST /api/{bot_id}/chat`** (standard)

Request body:
```json
{
  "message": "What chord shapes work at fret 7?",
  "conversation_history": [...],
  "session_id": "optional"
}
```

---

## Full Call Chain

### 1. `core/router.py` — `create_bot_router()`

The router was registered at startup when `main.py` called `factory_router`, which auto-discovered all enabled bots via `__init__.py`. The request lands on either `chat_stream()` or `chat()`.

**`chat_stream(request: ChatRequest)`**

- Validates message is not empty
- Calls `load_bot_config(bot_id)` — reads `bots/{bot_id}/config.yml` from local filesystem
- Extracts `top_k` and `similarity_threshold` from `config.bot.rag`
- Calls `generate_response_stream()` from `core/chatbot.py`
- Returns a `StreamingResponse` that iterates the generator

---

### 2. `core/chatbot.py` — `generate_response_stream()`

Orchestrates the full RAG pipeline. Takes `bot_id`, `user_message`, `top_k`, `similarity_threshold`, and `conversation_history`.

**Step A — Retrieve context:**
```python
relevant_chunks = retrieve_relevant_chunks(
    bot_id, user_message, top_k, similarity_threshold
)
```
→ delegates to `core/retrieval.py` (see section 3 below)

**Step B — Format context:**
```python
context = format_context_for_llm(relevant_chunks)
```
→ also in `core/retrieval.py`. Joins chunks into a `[CATEGORY]\ntext` block separated by `---`.

**Step C — Build messages array:**
- Loops over `conversation_history`, appending each as `{"role": ..., "content": [{"text": ...}]}`
- Appends current user message with context injected:
  ```
  ## Relevant Context:
  {context}

  ## User Question:
  {user_message}
  ```

**Step D — Load system prompt:**
```python
system_prompt = load_system_prompt(bot_id)
```
- Checks `_system_prompts` cache (dict, persists on warm Lambda)
- On miss: reads `bots/{bot_id}/prompt.yml` from local filesystem
- Injects `{current_date}` into the template
- Caches result for subsequent requests

**Step E — Initialize Bedrock client:**
```python
client = get_bedrock_client()
```
- Checks `_bedrock_client` global (lazy-init, persists on warm Lambda)
- On cold start: tries credentials file at `/root/.aws/credentials`, falls back to IAM role

---

### 3. `core/retrieval.py` — `retrieve_relevant_chunks()`

Called from `chatbot.py`. Handles both embedding the query and searching stored vectors.

**Step A — Embed the query:**
```python
query_embedding = generate_query_embedding(query)
```

> 🔴 **BEDROCK CALL #1** — `client.invoke_model()`
> - Model: `amazon.titan-embed-text-v2:0`
> - Input: user's question as plain text
> - Config: `dimensions=1024`, `normalize=True`
> - Output: 1024-dimension float vector

**Step B — Load bot embeddings:**
```python
items = get_cached_embeddings(bot_id)
```
- Checks `_embeddings_cache[bot_id]` (dict keyed by bot_id, warm Lambda cache)
- On cache **HIT**: returns immediately, no DynamoDB call
- On cache **MISS**:
  - Scans `ChatbotRAG` DynamoDB table (paginated)
  - Filters results to rows where `bot_id` matches
  - Stores in `_embeddings_cache[bot_id]`

**Step C — Cosine similarity search (in memory):**
- Converts each stored embedding from `Decimal` to `float`
- Computes `cosine_similarity(query_embedding, stored_embedding)` using numpy
- Filters to items above `similarity_threshold`
- Sorts descending by score
- Returns top `top_k` results

Each result returned: `{id, category, heading, text, similarity}`

---

### 4. Back in `core/chatbot.py` — Bedrock Claude call

With context formatted and messages built:

> 🔴 **BEDROCK CALL #2** — `client.converse_stream()`
> - Model: `us.anthropic.claude-sonnet-4-20250514-v1:0`
> - System: bot's system prompt (from `prompt.yml`)
> - Messages: conversation history + current user message with injected context
> - Config: `maxTokens=1000`
> - Output: streamed `contentBlockDelta` events

The generator yields each text chunk as it arrives:
```python
for event in response["stream"]:
    if "contentBlockDelta" in event:
        yield event["contentBlockDelta"]["delta"]["text"]
```

---

### 5. Back in `core/router.py` — response delivery

The `StreamingResponse` streams each yielded chunk directly to the client as `text/plain`.

For the non-streaming `/chat` endpoint, `generate_response()` follows the same path through steps 1–4 but uses `client.converse()` instead of `converse_stream()`, and additionally calls `log_chat_interaction()` which writes the question, response, and sources to the `ChatbotLogs` DynamoDB table.

---

## Summary Diagram

```
POST /api/{bot_id}/chat/stream
        │
        ▼
router.py — chat_stream()
  │  load_bot_config()         → bots/{bot_id}/config.yml (local)
  │
  ▼
chatbot.py — generate_response_stream()
  │
  ├─► retrieval.py — retrieve_relevant_chunks()
  │     │
  │     ├─► 🔴 BEDROCK #1 — Titan V2 (embed query)
  │     │     amazon.titan-embed-text-v2:0
  │     │     → 1024-dim vector
  │     │
  │     ├─► DynamoDB — ChatbotRAG scan (cache miss only)
  │     │     filtered by bot_id
  │     │
  │     └─► cosine similarity (numpy, in memory)
  │           → top_k chunks above threshold
  │
  ├─► retrieval.py — format_context_for_llm()
  │     → formatted context string
  │
  ├─► load_system_prompt()     → bots/{bot_id}/prompt.yml (local)
  │
  └─► 🔴 BEDROCK #2 — Claude Sonnet (generate response)
        us.anthropic.claude-sonnet-4-20250514-v1:0
        system: prompt.yml contents
        messages: history + context + question
        → streamed text chunks
              │
              ▼
        StreamingResponse → client
```

---

## Bedrock Calls at a Glance

| # | Where | Function | Model | Purpose |
|---|-------|----------|-------|---------|
| 1 | `retrieval.py` | `generate_query_embedding()` | `amazon.titan-embed-text-v2:0` | Convert user question to 1024-dim vector for similarity search |
| 2 | `chatbot.py` | `generate_response_stream()` | `claude-sonnet-4-20250514` | Generate final response with RAG context injected |

---

## Warm vs Cold Lambda

On a **cold start**, both Bedrock clients initialize (credentials lookup), the DynamoDB scan runs, and the system prompt is read from disk. Everything is then cached in module-level globals.

On a **warm invocation**, all three caches are already populated — the only external calls are the two Bedrock API calls. Use `GET /api/{bot_id}/warmup` to pre-populate caches before the first real user request.
