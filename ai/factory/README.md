# Bot Factory

A reusable RAG chatbot framework. Write a config, run one command, get a working chatbot with semantic search, Claude-powered responses, and a themed frontend.

## How It Works

Each bot is a folder under `bots/` containing three things: a config file, a system prompt, and knowledge data. The factory's core modules handle everything else — chunking data into text, generating embeddings via AWS Bedrock, storing them in DynamoDB, retrieving relevant context via cosine similarity, and generating Claude responses via Bedrock.

The backend auto-discovers any bot with `enabled: true` in its config and registers API endpoints automatically. No code changes needed.

```
User question
  → Bedrock Titan V2 embedding (convert question to vector)
  → DynamoDB cosine search (find relevant knowledge)
  → Bedrock Claude Sonnet (generate response with context)
  → User gets answer
```

For a detailed trace of every file and function called during a chat request, see [CHAT_FLOW.md](CHAT_FLOW.md).

## Prerequisites

Dependencies (PyYAML, numpy, boto3, etc.) are installed inside the Docker container automatically. You don't need to install them on your host machine.

You'll need:

- **Docker** — for local development (`docker compose up -d`)
- **AWS CLI** — configured with credentials for DynamoDB, S3, and Bedrock

**AWS Bedrock access** — after your first call to Bedrock you may be prompted to request model access:

- Go to the AWS Console → Bedrock → Model catalog (or Model access)
- There should be a prompt to submit use case details at the top of the page
- Fill it out simply ("AI chatbot for personal portfolio website")
- You need access to both `amazon.titan-embed-text-v2:0` (embeddings) and `claude-sonnet-4` (responses)

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
    provider: "bedrock"
    name: "us.anthropic.claude-sonnet-4-20250514-v1:0"
    max_tokens: 1000

  rag:
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

### Step 3: Write prompt.yml

This is the system prompt sent to Claude with every request. It defines personality, rules, and response formatting. The `prompt` field supports `{current_date}` as a placeholder that gets injected at runtime.

```
ai/factory/bots/{bot_id}/prompt.yml
```

Example:

```yaml
prompt: |
  You are ChefBot, a friendly cooking assistant.

  Today's date is {current_date}.

  Rules:
  - Keep responses to 2-3 sentences
  - Always mention food safety when relevant
  - If asked about something outside cooking, politely redirect
```

### Step 4: Add knowledge data

Create YAML files in the `data/` folder using the universal data format, then upload them to S3. The embedding pipeline reads from S3, not the local filesystem.

```
s3://bot-factory-data/bots/{bot_id}/data/
```

Two entry types are supported:

**String entries** — content is already readable, embedded as-is:

```yaml
- id: knife_basics
  format: string
  category: "Techniques"
  heading: "Knife Skills"
  content: "The three essential cuts are dice, julienne, and chiffonade..."
```

**Object entries** — a template applied to each item:

```yaml
- id: cooking_temps
  format: object
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

The chunker flattens object entries using the template, so each item becomes a standalone text chunk for embedding.

**Upload your data files to S3:**

```bash
# Local (LocalStack)
aws --endpoint-url=http://localhost:4566 s3 sync bots/{bot_id}/data/ s3://bot-factory-data/bots/{bot_id}/data/

# Production
aws s3 sync bots/{bot_id}/data/ s3://bot-factory-data/bots/{bot_id}/data/
```

### Step 5: Generate embeddings

Run inside the Docker container so it hits LocalStack's DynamoDB and Bedrock:

```bash
docker compose exec api python -m ai.factory.core.generate_embeddings {bot_id}
```

This runs the full pipeline: the chunker reads your YAML files from S3, Bedrock Titan V2 converts each chunk to a 1024-dimension vector, and the vectors are stored in the `ChatbotRAG` DynamoDB table tagged with your bot ID.

To regenerate after data changes:

```bash
docker compose exec api python -m ai.factory.core.generate_embeddings {bot_id} --force
```

The `--force` flag does a kill-and-fill scoped to your bot ID. Other bots' embeddings are untouched.

> **Note:** Do not run the embeddings command directly on your host machine. The dependencies and AWS connections are configured inside the container.

### Step 5b: Push embeddings to prod

Embeddings are generated against LocalStack locally. To push them to prod DynamoDB, use the export/import scripts in `ai/scripts/`. Both scripts take a `bot_id` argument to scope the operation.

```bash
# Export one bot from LocalStack to _scratch/ (run inside container)
docker compose exec api python /app/ai/scripts/export_embeddings.py guitar

# Import one bot to prod DynamoDB (run from host)
python3 ai/scripts/import_embeddings.py guitar
```

The export saves to `_scratch/{bot_id}-embeddings-export.json` (already in `.gitignore`). The import deletes existing rows for that bot in prod, then writes the new ones. Other bots are untouched.

To export/import all bots at once:

```bash
docker compose exec api python /app/ai/scripts/export_embeddings.py --all
python3 ai/scripts/import_embeddings.py --all
```

> **Note:** Make sure `_scratch/` exists before exporting (`mkdir -p _scratch`). Run the import from your host machine where your AWS credentials are configured.

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
docker compose up -d
```

Visit `http://localhost:8080/{bot_id}.html` and start chatting.

> **Tip:** If you update backend code (router, chatbot, retrieval), rebuild with `docker compose up --build -d`. Frontend file changes (HTML, JS, CSS) require a hard refresh (Ctrl+Shift+R) if cached.

### Step 8: Deploy

```bash
# 1. Push embeddings to prod (if data changed — see Step 5b)
docker compose exec api python /app/ai/scripts/export_embeddings.py {bot_id}
python3 ai/scripts/import_embeddings.py {bot_id}

# 2. Backend (Lambda)
./build-lambda.sh
aws s3 cp terraform/builds/fastapi-app.zip s3://aws-serverless-resume-prod/lambda/fastapi-app.zip
aws lambda update-function-code --function-name aws-serverless-resume-api --s3-bucket aws-serverless-resume-prod --s3-key lambda/fastapi-app.zip

# 3. Frontend (S3 + CloudFront)
aws s3 cp app/{bot_id}.html s3://aws-serverless-resume-prod/{bot_id}.html --cache-control "no-cache"
aws s3 cp app/bot_scripts/{bot_id}/ s3://aws-serverless-resume-prod/bot_scripts/{bot_id}/ --recursive --cache-control "no-cache"
aws s3 cp app/assets/{bot_id}/ s3://aws-serverless-resume-prod/assets/{bot_id}/ --recursive --cache-control "no-cache"
aws cloudfront create-invalidation --distribution-id <your_id> --paths "/*"
```

Skip step 1 if you only changed code or frontend files. Skip steps 2-3 if you only changed knowledge data.

## Project Structure

```
ai/factory/
├── README.md                  ← you are here
├── CHAT_FLOW.md               ← full trace of the chat request pipeline
├── __init__.py                ← register_bots() auto-discovery
├── scaffold_bot.py            ← frontend scaffolder
│
├── core/                      ← shared engine (never edit per-bot)
│   ├── chunker.py             ← S3 YAML → text chunks
│   ├── generate_embeddings.py ← chunks → Bedrock Titan V2 → DynamoDB
│   ├── retrieval.py           ← question → Bedrock embedding → cosine search
│   ├── chatbot.py             ← context + question → Bedrock Claude → response
│   └── router.py              ← creates FastAPI endpoints per bot
│
└── bots/                      ← one folder per bot
    └── guitar/
        ├── config.yml         ← bot configuration
        ├── prompt.yml         ← system prompt for Claude
        └── data/              ← source files (sync to S3 before embedding)
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

| Field         | Type    | Description                                                |
| ------------- | ------- | ---------------------------------------------------------- |
| `id`          | string  | Bot identifier. Drives folder names, endpoints, filenames. |
| `enabled`     | boolean | Set `false` to disable without deleting.                   |
| `name`        | string  | Display name (shown in header, chat labels).               |
| `personality` | string  | Personality hint for prompt context.                       |

### bot.response_style

| Field         | Type    | Description                                   |
| ------------- | ------- | --------------------------------------------- |
| `tone`        | string  | `"conversational"`, `"formal"`, `"technical"` |
| `length`      | string  | `"concise"`, `"detailed"`                     |
| `suggestions` | boolean | Show suggestion chips in the UI.              |

### bot.model

| Field        | Type    | Description                                                         |
| ------------ | ------- | ------------------------------------------------------------------- |
| `provider`   | string  | `"bedrock"`                                                         |
| `name`       | string  | Bedrock model ID, e.g., `"us.anthropic.claude-sonnet-4-20250514-v1:0"` |
| `max_tokens` | integer | Max response length.                                                |

### bot.rag

| Field                  | Type    | Description                                                             |
| ---------------------- | ------- | ----------------------------------------------------------------------- |
| `top_k`                | integer | Number of chunks to retrieve. Use 10+ if data has many similar entries. |
| `similarity_threshold` | float   | Minimum cosine similarity (0.0–1.0).                                    |

### bot.boundaries

Free-form key-value pairs. The keys are used in the system prompt to define what the bot will and won't discuss. Name them whatever makes sense for your bot.

### suggestions (required)

List of starter questions shown as chips in the chat UI.

### frontend (required for scaffold)

| Field         | Type   | Description                                                   |
| ------------- | ------ | ------------------------------------------------------------- |
| `subtitle`    | string | Shown below the bot name in the header.                       |
| `welcome`     | string | First message displayed in the chat.                          |
| `placeholder` | string | Input field hint text.                                        |
| `badge`       | string | Header badge text (e.g., "Beta", "v1").                       |
| `nav`         | list   | Left sidebar links. Each item has `icon`, `label`, `section`. |

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
<script>
  window.BOT_CONFIG = { ... };
</script>
<script src="bot_scripts/{bot_id}/formatter.js"></script>
<script src="bot_scripts/chat.js"></script>
```

If no formatter is registered, `chat.js` uses its default plain text renderer.

## Auto-Discovery

The factory uses auto-discovery in `__init__.py`. At startup, it scans every folder in `bots/`, reads each `config.yml`, and registers API routes for any bot with `enabled: true`. Adding a new bot never requires editing `main.py`.

Each bot gets these endpoints:

- `POST /api/{bot_id}/chat` — send a message, get a response
- `POST /api/{bot_id}/chat/stream` — send a message, get a streamed response
- `GET  /api/{bot_id}/config` — frontend configuration
- `GET  /api/{bot_id}/suggestions` — starter questions
- `GET  /api/{bot_id}/warmup` — pre-load embedding cache

## Existing Bots

| Bot                | ID       | Endpoint           | Description                                                                  |
| ------------------ | -------- | ------------------ | ---------------------------------------------------------------------------- |
| RobbAI             | —        | `/api/ai/chat`     | Resume assistant. Runs on legacy code in `ai/`, not yet migrated to factory. |
| The Fret Detective | `guitar` | `/api/guitar/chat` | Electric guitar instruction. First factory bot.                              |

## Embedding Notes

All bot embeddings share one DynamoDB table (`ChatbotRAG`), partitioned by bot ID. Each record's primary key is `{bot_id}_{entry_id}` and includes a `bot_id` field for filtering.

Embeddings are generated using **Bedrock Titan Text Embeddings V2** (`amazon.titan-embed-text-v2:0`) at 1024 dimensions. Knowledge data files live in S3 (`s3://bot-factory-data/bots/{bot_id}/data/`) — the chunker reads from S3 at embedding time, keeping data files out of the Lambda package.

The kill-and-fill approach on `--force` only deletes rows matching the target bot ID. Running embeddings for one bot never affects another.

If your bot has many similar entries (like The Fret Detective's 48 triad voicings), increase `top_k` in your config to 10 or higher so the right result isn't crowded out by near-duplicates.
