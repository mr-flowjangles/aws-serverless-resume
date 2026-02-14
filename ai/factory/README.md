# Bot Factory

A reusable RAG chatbot framework. Write a config, run one command, get a working chatbot with semantic search, Claude-powered responses, and a themed frontend.

## How It Works

Each bot is a folder under `bots/` containing three things: a config file, a system prompt, and knowledge data. The factory's core modules handle everything else — chunking data into text, generating OpenAI embeddings, storing them in DynamoDB, retrieving relevant context via cosine similarity, and generating Claude responses.

The backend auto-discovers any bot with `enabled: true` in its config and registers API endpoints automatically. No code changes needed.

```
User question
  → OpenAI embedding (convert question to vector)
  → DynamoDB cosine search (find relevant knowledge)
  → Claude Sonnet (generate response with context)
  → User gets answer
```

## Prerequisites

Install the factory dependencies from the project root:

```bash
pip install -r ai/factory/requirements.txt
```

You'll also need:
- **Docker** — for local development (`docker compose up`)
- **AWS CLI** — configured with credentials for DynamoDB and S3
- **OpenAI API key** — set as `OPENAI_API_KEY` environment variable (for embeddings)
- **Anthropic API key** — set as `ANTHROPIC_API_KEY` environment variable (for Claude responses)

## Creating a New Bot

### Step 1: Create the bot folder

Pick a bot ID. This ID drives everything — folder names, API endpoints, HTML filenames.

```
ai/factory/bots/{bot_id}/
```

Example:
```bash
mkdir -p ai/factory/bots/cooking
```

### Step 2: Write config.yml

This is the single source of truth for your bot. It configures the backend (model, RAG settings, boundaries) and the frontend (page title, nav, suggestions).

```yaml
bot:
  id: "cooking"
  enabled: true
  name: "ChefBot"
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
    top_k: 5
    similarity_threshold: 0.3

  boundaries:
    discuss_cooking: true
    discuss_unrelated: false

suggestions:
  - "How do I make pasta from scratch?"
  - "What temp for a medium-rare steak?"
  - "Best way to dice an onion?"

frontend:
  subtitle: "Your Kitchen Assistant"
  welcome: "Hey! Ask me anything about cooking."
  placeholder: "Ask about cooking..."
  badge: "Beta"
  nav:
    - icon: "🍳"
      label: "Chat"
      section: "chat"
    - icon: "🥩"
      label: "Proteins"
      section: "proteins"
```

See [Config Reference](#config-reference) for all fields.

### Step 3: Write prompt.md

This is the system prompt sent to Claude with every request. It defines personality, rules, and response formatting.

```
ai/factory/bots/{bot_id}/prompt.md
```

Example:
```markdown
You are ChefBot, a friendly cooking assistant.

Rules:
- Keep responses to 2-3 sentences
- Always mention food safety when relevant
- If asked about something outside cooking, politely redirect
```

### Step 4: Add knowledge data

Create YAML files in the `data/` folder using the universal data format.

```
ai/factory/bots/{bot_id}/data/
```

Two entry types are supported:

**Text entries** — content is already readable, embedded as-is:
```yaml
- id: knife_basics
  format: text
  category: "Techniques"
  heading: "Knife Skills"
  content: "The three essential cuts are dice, julienne, and chiffonade..."
```

**Structured entries** — a template applied to each item:
```yaml
- id: cooking_temps
  format: structured
  category: "Temperatures"
  heading: "Protein Cooking Temperatures"
  template: "{protein} cooked to {doneness}: internal temp {temp}°F. {notes}"
  items:
    - protein: "Chicken breast"
      doneness: "done"
      temp: "165"
      notes: "No pink remaining."
    - protein: "Beef steak"
      doneness: "medium-rare"
      temp: "130"
      notes: "Warm red center."
```

The chunker flattens structured entries using the template, so each item becomes a standalone text chunk for embedding.

### Step 5: Generate embeddings

From the project root:

```bash
python -m ai.factory.core.generate_embeddings {bot_id}
```

This runs the full pipeline: chunker reads your YAML data, OpenAI converts each chunk to a 1,536-dimension vector, and the vectors are stored in the ChatbotRAG DynamoDB table tagged with your bot ID.

To regenerate after data changes:

```bash
python -m ai.factory.core.generate_embeddings {bot_id} --force
```

The `--force` flag does a kill-and-fill scoped to your bot ID. Other bots' embeddings are untouched.

### Step 6: Scaffold the frontend

From the project root:

```bash
python3 ai/factory/scaffold_bot.py {bot_id}
```

This reads your config.yml and creates:
- `app/{bot_id}.html` — the bot's page, fully wired up
- `app/bot_scripts/{bot_id}/` — for bot-specific CSS and JS
- `app/assets/{bot_id}/` — for bot-specific images (logo, etc.)

After scaffolding, add your logo and any custom styles or formatters.

### Step 7: Test locally

```bash
docker compose up
```

Visit `http://localhost:8080/{bot_id}.html` and start chatting.

### Step 8: Deploy

From the project root:

```bash
# Backend (Lambda)
./build-lambda.sh
aws s3 cp terraform/builds/fastapi-app.zip s3://aws-serverless-resume-prod/lambda/fastapi-app.zip
aws lambda update-function-code --function-name aws-serverless-resume-api --s3-bucket aws-serverless-resume-prod --s3-key lambda/fastapi-app.zip

# Frontend (S3 + CloudFront)
aws s3 cp app/{bot_id}.html s3://aws-serverless-resume-prod/{bot_id}.html --cache-control "no-cache"
aws s3 cp app/bot_scripts/{bot_id}/ s3://aws-serverless-resume-prod/bot_scripts/{bot_id}/ --recursive --cache-control "no-cache"
aws s3 cp app/assets/{bot_id}/ s3://aws-serverless-resume-prod/assets/{bot_id}/ --recursive --cache-control "no-cache"
aws cloudfront create-invalidation --distribution-id E1G5RMKV5G4GR7 --paths "/*"
```

## Project Structure

```
ai/factory/
├── README.md                  ← you are here
├── __init__.py                ← register_bots() auto-discovery
├── scaffold_bot.py            ← frontend scaffolder
│
├── core/                      ← shared engine (never edit per-bot)
│   ├── chunker.py             ← YAML → text chunks
│   ├── generate_embeddings.py ← chunks → OpenAI → DynamoDB
│   ├── retrieval.py           ← question → cosine search → matches
│   ├── chatbot.py             ← matches + question → Claude → response
│   └── router.py              ← creates FastAPI endpoints per bot
│
└── bots/                      ← one folder per bot
    └── guitar/
        ├── config.yml         ← bot configuration
        ├── prompt.md          ← system prompt for Claude
        └── data/
            └── guitar-knowledge.yml

app/                           ← frontend (generated by scaffold_bot.py)
├── guitar.html                ← bot page
├── bot_scripts/
│   ├── bot-factory.css        ← shared framework styles
│   ├── chat.js                ← shared chat module
│   ├── navigation.js          ← shared nav highlighting
│   └── guitar/                ← bot-specific
│       ├── guitar.css         ← custom styles (e.g., tab rendering)
│       └── formatter.js       ← custom message formatter (optional)
└── assets/
    └── guitar/                ← bot-specific images
        └── logo.png
```

## Config Reference

### bot (required)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Bot identifier. Drives folder names, endpoints, filenames. |
| `enabled` | boolean | Set `false` to disable without deleting. |
| `name` | string | Display name (shown in header, chat labels). |
| `personality` | string | Personality hint for prompt context. |

### bot.response_style

| Field | Type | Description |
|-------|------|-------------|
| `tone` | string | `"conversational"`, `"formal"`, `"technical"` |
| `length` | string | `"concise"`, `"detailed"` |
| `suggestions` | boolean | Show suggestion chips in the UI. |

### bot.model

| Field | Type | Description |
|-------|------|-------------|
| `provider` | string | `"anthropic"` |
| `name` | string | Model ID, e.g., `"claude-sonnet-4-20250514"` |
| `max_tokens` | integer | Max response length. |

### bot.rag

| Field | Type | Description |
|-------|------|-------------|
| `embedding_model` | string | `"openai"` (uses text-embedding-3-small) |
| `top_k` | integer | Number of chunks to retrieve. Use 10+ if data has many similar entries. |
| `similarity_threshold` | float | Minimum cosine similarity (0.0–1.0). |

### bot.boundaries

Free-form key-value pairs. The keys are used in the system prompt to define what the bot will and won't discuss. Name them whatever makes sense for your bot.

### suggestions (required)

List of starter questions shown as chips in the chat UI.

### frontend (required for scaffold)

| Field | Type | Description |
|-------|------|-------------|
| `subtitle` | string | Shown below the bot name in the header. |
| `welcome` | string | First message displayed in the chat. |
| `placeholder` | string | Input field hint text. |
| `badge` | string | Header badge text (e.g., "Beta", "v1"). |
| `nav` | list | Left sidebar links. Each item has `icon`, `label`, `section`. |

## Custom Formatters

The shared `chat.js` supports a plugin hook for bot-specific message rendering. If your bot outputs content that needs special formatting (like guitar tablature), create a `formatter.js` in your bot's `bot_scripts/{bot_id}/` folder.

The formatter registers itself on `window.BOT_CONFIG.formatMessage`:

```javascript
function myFormatMessage(text, container) {
    // custom rendering logic
}

window.BOT_CONFIG = window.BOT_CONFIG || {};
window.BOT_CONFIG.formatMessage = myFormatMessage;
```

Load it in your HTML **after** the BOT_CONFIG block and **before** chat.js:

```html
<script>window.BOT_CONFIG = { ... };</script>
<script src="bot_scripts/{bot_id}/formatter.js"></script>
<script src="bot_scripts/chat.js"></script>
```

If no formatter is registered, `chat.js` uses its default plain text renderer.

## Auto-Discovery

The factory uses auto-discovery in `__init__.py`. At startup, it scans every folder in `bots/`, reads each `config.yml`, and registers API routes for any bot with `enabled: true`. Adding a new bot never requires editing `main.py`.

Each bot gets three endpoints:
- `POST /api/{bot_id}/chat` — send a message, get a response
- `GET /api/{bot_id}/config` — frontend configuration
- `GET /api/{bot_id}/warmup` — pre-load embedding cache

## Existing Bots

| Bot | ID | Endpoint | Description |
|-----|----|----------|-------------|
| RobbAI | — | `/api/ai/chat` | Resume assistant. Runs on legacy code in `ai/`, not yet migrated to factory. |
| GuitarBot | `guitar` | `/api/guitar/chat` | Electric guitar instruction. First factory bot. |

## Embedding Notes

All bot embeddings share one DynamoDB table (`ChatbotRAG`), partitioned by bot ID. Each record's primary key is `{bot_id}_{entry_id}` and includes a `bot_id` field for filtering.

The kill-and-fill approach on `--force` only deletes rows matching the target bot ID. Running embeddings for one bot never affects another.

If your bot has many similar entries (like GuitarBot's 48 triad voicings), increase `top_k` in your config to 10 or higher so the right result isn't crowded out by near-duplicates.
