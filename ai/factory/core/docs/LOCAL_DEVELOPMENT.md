# Local Development Guide

How to generate embeddings and test the chatbot from your local machine.

---

## Generating Embeddings

From your project root:

```bash
# 1. Make sure your stack is running
docker compose up -d

# 2. Sync your YAML data files to LocalStack S3
aws --endpoint-url=http://localhost:4566 s3 sync ai/factory/bots/{bot_id}/data/ s3://bot-factory-data/bots/{bot_id}/data/

# 3. Run the embedding generator inside the container
docker compose exec api python -m ai.factory.core.generate_embeddings {bot_id}

# Or skip the confirmation prompt
docker compose exec api python -m ai.factory.core.generate_embeddings {bot_id} --force
```

Replace `{bot_id}` with `guitar` or whatever bot you're working on.

The S3 sync in step 2 is required any time you change your YAML data files — the chunker reads from LocalStack S3, not your local filesystem.

---

## Testing the Chatbot Locally

Since LocalStack does not emulate Bedrock, the chat pipeline always hits real AWS. You just need your AWS credentials available inside the container.

```bash
# 1. Make sure your stack is running
docker compose up -d

# 2. Hit the warmup endpoint to pre-load the embedding cache
curl http://localhost:8080/api/{bot_id}/warmup

# 3. Send a test message
curl -X POST http://localhost:8080/api/{bot_id}/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "your test question here"}'

# Or test the streaming endpoint
curl -X POST http://localhost:8080/api/{bot_id}/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "your test question here"}'
```

Or just open the browser at `http://localhost:8080/{bot_id}.html` and chat directly.

---

## Troubleshooting Bedrock Credentials

If Bedrock calls are failing, the most common cause is credentials not being available inside the container. Make sure your `docker-compose.yml` has one of the following:

**Option A — Pass credentials as environment variables:**

```yaml
environment:
  - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
  - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
  - AWS_DEFAULT_REGION=us-east-1
```

**Option B — Mount your credentials file:**

```yaml
volumes:
  - ~/.aws:/root/.aws:ro
```

`chatbot.py` tries the credentials file at `/root/.aws/credentials` first, then falls back to IAM role — so the volume mount approach works out of the box.
