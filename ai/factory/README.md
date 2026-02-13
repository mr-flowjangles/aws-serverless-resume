# Bot Factory

Reusable chatbot framework for spinning up RAG-powered chatbots with different data sources and personalities.

## Architecture
```
ai/factory/
├── core/                          # Shared engine (same for every bot)
│   ├── chunker.py                 # Reads universal YAML → text chunks
│   ├── retrieval.py               # Cosine similarity search (by bot_id)
│   ├── chatbot.py                 # Claude API calls (loads prompt by bot_id)
│   ├── router.py                  # Creates FastAPI endpoints for any bot
│   └── generate_embeddings.py     # YAML → OpenAI embeddings → DynamoDB
│
└── bots/                          # One folder per bot
    └── guitar/                    # Example bot
        ├── config.yml             # Bot settings and suggestions
        ├── prompt.md              # System prompt (personality/rules)
        └── data/
            └── guitar-knowledge.yml  # Knowledge base in universal format
```

## Adding a New Bot

1. Create a folder: `bots/{bot_id}/`
2. Add `config.yml` (settings, suggestions)
3. Add `prompt.md` (personality, rules, boundaries)
4. Add data files in `data/` using the universal YAML format
5. Generate embeddings: `python -m ai.factory.core.generate_embeddings {bot_id}`
6. Register the router in `main.py`

## Universal Data Format

Bot data files use two entry formats:

**Text** — content is already readable, embedded as-is:
```yaml
- id: entry_id
  format: string
  category: "Topic"
  heading: "What This Is About"
  content: "Readable text that gets embedded directly."
```

**Structured** — template + items, flattened at embedding time:
```yaml
- id: entry_id
  format: object
  category: "Topic"
  heading: "Entry Heading"
  template: "{field1} in {field2}. Details: {field3}."
  items:
    - field1: "value"
      field2: "value"
      field3: "value"
```

## Existing Bots

| Bot | Endpoint | Description |
|-----|----------|-------------|
| RobbAI | `/ai/chat` | Resume assistant (runs on legacy code, not yet migrated) |
| Guitar | `/guitar/chat` | Guitar instruction assistant |