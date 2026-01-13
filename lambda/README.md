# Lambda Functions

This directory contains AWS Lambda functions converted from your FastAPI endpoints.

## Structure

```
lambda/
├── profile/              # GET /resume/profile
│   └── lambda_function.py
├── work_experience/      # GET /resume/work-experience
│   └── lambda_function.py
├── education/           # GET /resume/education
│   └── lambda_function.py
├── skills/              # GET /resume/skills
│   └── lambda_function.py
├── contact/             # POST /contact
│   └── lambda_function.py
└── health/              # GET /health
    └── lambda_function.py
```

## How This Works

### Local Development (Docker)
Your FastAPI app in `api/` continues to work exactly as before:
```bash
make up  # Runs FastAPI locally
```

### AWS Production (Lambda)
These Lambda functions will be deployed to AWS and called via API Gateway:
- Same logic as your FastAPI endpoints
- Returns API Gateway-formatted responses
- Deployed via Terraform

## Key Differences from FastAPI

### FastAPI (Local)
```python
@router.get("/resume/profile")
def get_profile():
    return {"name": "Rob"}
```

### Lambda (AWS)
```python
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({"name": "Rob"})
    }
```

## Environment Variables

Each Lambda function uses these environment variables (set by Terraform):
- `DYNAMODB_TABLE`: Name of the DynamoDB table (default: `ResumeData`)
- `RECAPTCHA_SECRET_KEY`: Google reCAPTCHA secret (for contact form only)

## Deployment

Terraform will:
1. Zip each Lambda function directory
2. Create Lambda functions in AWS
3. Set up IAM roles for DynamoDB access
4. Connect to API Gateway

## Testing Locally

You can test Lambda functions locally using `sam local` or just keep using your Docker setup!

Your workflow:
1. Develop locally with FastAPI in Docker
2. When ready, deploy Lambda functions to AWS
3. Both environments work independently
