# Bot Factory

A portable, reusable chatbot framework. Each bot gets its own knowledge base, personality, and API endpoints — powered by the same RAG pipeline underneath.

Drop it into an existing FastAPI project or run it standalone.

## How It Works

```
YAML data → Chunker → OpenAI Embeddings → DynamoDB → Retrieval → Claude → Response
```

Every bot follows this same pipeline. What changes per bot is the data, the system prompt, and the config.

## Directory Structure

```
factory/
├── __init__.py                    # Auto-discovers bots, exports factory_router
├── main.py                        # Standalone entry point (no parent app needed)
├── requirements.txt               # Dependencies
├── README.md
│
├── core/                          # Shared engine (never changes per bot)
│   ├── chunker.py                 # Reads YAML data → text chunks
│   ├── retrieval.py               # Cosine similarity search (scoped by bot_id)
│   ├── chatbot.py                 # Claude API calls (loads prompt per bot_id)
│   ├── router.py                  # Creates FastAPI endpoints for any bot
│   └── generate_embeddings.py     # Chunks → OpenAI embeddings → DynamoDB
│
└── bots/                          # One folder per bot
    └── guitar/                    # Example bot
        ├── config.yml             # Settings, suggestions, RAG tuning
        ├── prompt.yml             # System prompt (personality & rules)
        └── data/
            └── guitar-knowledge.yml   # Knowledge base in universal format
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set environment variables

```bash
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
export AWS_ENDPOINT_URL=http://localhost:4566   # for LocalStack, omit for real AWS
```

### 3. Generate embeddings for a bot

```bash
python -m factory.core.generate_embeddings guitar
```

First run generates automatically. If embeddings already exist, it prompts before regenerating. Use `--force` to skip the prompt.

### 4. Run the server

Standalone:
```bash
uvicorn factory.main:app --reload --port 8080
```

Or embedded in an existing FastAPI app (add to your main.py):
```python
from ai.factory import factory_router
app.include_router(factory_router, prefix=prefix)
```

### 5. Talk to your bot

```bash
curl -X POST http://localhost:8080/guitar/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I restring a guitar?"}'
```

## API Endpoints

Each enabled bot gets three endpoints:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/{bot_id}/chat` | Send a message, get a response |
| GET | `/{bot_id}/config` | Bot configuration for frontends |
| GET | `/{bot_id}/suggestions` | Suggested starter questions |

## Adding a New Bot

### Step 1: Create the bot folder

```
factory/bots/your_bot/
├── config.yml
├── prompt.yml
└── data/
    └── your-data.yml
```

### Step 2: Write config.yml

```yaml
bot:
  id: "your_bot"               # Must match the folder name
  enabled: true                 # Toggle on/off without redeploying
  name: "Your Bot Name"
  personality: "friendly"

  response_style:
    tone: "conversational"
    length: "concise"
    suggestions: true

  model:
    provider: "anthropic"
    name: "claude-sonnet-4-20250514"
    max_tokens: 1000

  rag:
    embedding_model: "openai"
    top_k: 5                    # Chunks retrieved per question
    similarity_threshold: 0.3   # Minimum similarity (0-1)

  boundaries:
    discuss_topic_a: true
    discuss_unrelated: false

suggestions:
  - "First suggested question?"
  - "Second suggested question?"
```

### Step 3: Write prompt.yml

The system prompt sent to Claude with every request. Uses `{current_date}` placeholder, injected at runtime.

```yaml
prompt: |
  You are [Bot Name], a [description].

  Today's date is {current_date}.

  Your Tone and Style:
  - Conversational and helpful
  - PLAIN TEXT ONLY — never use markdown

  What You Can Discuss:
  - Topic 1
  - Topic 2

  What You Should NOT Discuss:
  - Off-limits topic

  Response Rules:
  1. Answer ONLY using the context provided below
  2. If context doesn't contain the answer, say so politely
```

### Step 4: Create your data files

All `.yml` files in `data/` are read automatically. Two entry formats:

**Text** — content is already readable, embedded as-is:
```yaml
meta:
  bot_id: "your_bot"
  title: "Your Knowledge Base"

entries:
  - id: unique_id
    format: text
    category: "Topic"
    heading: "What This Is About"
    content: "Readable text that gets embedded directly."
```

**Structured** — template + items, flattened at chunking time:
```yaml
entries:
  - id: unique_id
    format: structured
    category: "Topic"
    heading: "Section Heading"
    template: "{field1} is {field2}. Details: {field3}."
    items:
      - field1: "value"
        field2: "value"
        field3: "value"
```

Rules for data files:
- Every entry needs a unique `id`
- `format` must be `text` or `structured`
- For `structured`, every `{placeholder}` in the template must exist as a key in each item
- Keep entries focused — one concept per entry

### Step 5: Generate embeddings

```bash
python -m factory.core.generate_embeddings your_bot
```

### Step 6: That's it

If the bot's `config.yml` has `enabled: true`, the factory auto-discovers and registers it on startup. No code changes needed anywhere.

## Auto-Discovery

The factory scans the `bots/` folder at startup. For each subfolder with a `config.yml`:
- `enabled: true` → bot is registered and endpoints are live
- `enabled: false` → bot is skipped

To disable a bot, flip the flag. To add a bot, add a folder. No code changes to any Python file.

## DynamoDB

All bots share one table: `ChatbotRAG`. Each row includes a `bot_id` field so retrieval and kill-and-fill are scoped per bot. No new tables or infrastructure needed when adding a bot.

Chat interactions are logged to `ChatbotLogs` with `bot_id` for filtering.

## Architecture

All imports within the factory are relative, so the entire `factory/` folder is portable. It can live inside another project or run independently.

**Embedded:** Import `factory_router` and include it in your FastAPI app.

**Standalone:** Run `factory/main.py` directly with uvicorn.

## Tech Stack

- **FastAPI** — API framework
- **OpenAI** — text-embedding-3-small for vector embeddings
- **Anthropic Claude** — Response generation (claude-sonnet-4)
- **DynamoDB** — Embedding storage and chat logging
- **PyYAML** — Configuration and data files
- **NumPy** — Cosine similarity calculations