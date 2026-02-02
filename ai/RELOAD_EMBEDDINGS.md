# Reload Embeddings - Quick Reference

## When to run this

- After updating `personal-info.yml`
- After updating resume data (Excel)
- After changing chunk generation logic in `generate_embeddings.py`

## Steps

### 1. Clear existing embeddings

```bash
docker compose exec api python -c "
import boto3
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localstack:4566', region_name='us-east-1', aws_access_key_id='test', aws_secret_access_key='test')
table = dynamodb.Table('ChatbotRAG')
response = table.scan()
for item in response['Items']:
    table.delete_item(Key={'id': item['id']})
print('Embeddings cleared')
"
```

### 2. Regenerate embeddings

```bash
docker compose exec api python /app/ai/scripts/generate_embeddings.py
```

### 3. Verify (optional)

```bash
docker compose exec api python -c "
import boto3
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localstack:4566', region_name='us-east-1', aws_access_key_id='test', aws_secret_access_key='test')
table = dynamodb.Table('ChatbotRAG')
response = table.scan()
print(f'Total embeddings: {len(response[\"Items\"])}')
for item in response['Items']:
    print(f\"  {item['id']}: {item['type']}\")
"
```

### 4. Test

```bash
curl -X POST http://localhost:8080/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Rob'\''s current job?"}'
```

## Export to AWS

We store our embeddings locally even after the container is shutdown so we don't have to call OpenAI all the time. After you are set with your embeddings locally, export them for AWS deployment:

### Export (from LocalStack)

```bash
docker compose exec api python /app/ai/scripts/export_embeddings.py
```

### Import (to AWS production)

```bash
AWS_ENDPOINT_URL="" python3 ai/scripts/import_embeddings.py
```
