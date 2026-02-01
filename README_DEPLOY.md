# AWS Serverless Resume - Deployment Guide

This guide covers deploying to AWS. For local development setup, see [README.md](README.md).

---

## Part 1: Deploy From Scratch

### Prerequisites

Before deploying, ensure you have:
- AWS CLI configured (`aws configure`)
- Terraform >= 1.0 installed
- Docker Desktop installed and running
- Python 3.10+ installed
- Email verified in SES (see README.md)
- reCAPTCHA keys configured (see README.md)
- Domain registered in Route 53 (optional - update `terraform/variables.tf`)

### Step 1: Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Type `yes` when prompted. This creates:
- S3 bucket for static files and Lambda code
- CloudFront distribution with HTTPS
- ACM certificate (auto-validated via DNS)
- Route 53 DNS records
- DynamoDB table (ResumeData)
- Lambda function
- API Gateway
- IAM roles and policies

**Note:** Certificate validation can take 5-30 minutes.

### Step 2: Build and Deploy Lambda

```bash
# From project root (Docker must be running)
./scripts/build-lambda.sh

# Upload Lambda package to S3
aws s3 cp terraform/builds/fastapi-app.zip s3://YOUR_BUCKET_NAME/lambda/fastapi-app.zip

# Deploy to Lambda
aws lambda update-function-code \
  --function-name YOUR_LAMBDA_FUNCTION_NAME \
  --s3-bucket YOUR_BUCKET_NAME \
  --s3-key lambda/fastapi-app.zip
```

### Step 3: Load Resume Data

```bash
AWS_ENDPOINT_URL="" AWS_REGION="us-east-1" python3 scripts/load_resume.py path/to/your-resume-data.xlsx
```

### Step 4: Deploy Frontend

```bash
aws s3 cp app/index.html s3://YOUR_BUCKET_NAME/index.html
aws s3 cp app/assets/mobile.css s3://YOUR_BUCKET_NAME/assets/mobile.css
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

### Step 5: Verify

```bash
# Check API health
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/api/health

# Check DynamoDB has data
aws dynamodb scan --table-name ResumeData --select "COUNT"
```

---

## Part 2: Updates After Initial Deploy

### Scenario A: Frontend Only (index.html, CSS, static assets)

Changed `app/index.html` or CSS files?

```bash
aws s3 cp app/index.html s3://YOUR_BUCKET_NAME/index.html
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/index.html"
```

If you changed multiple files:
```bash
aws s3 sync app/ s3://YOUR_BUCKET_NAME/ --exclude "*.xlsx"
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

### Scenario B: Lambda/API Code (Python files in /api)

Changed Python code in the `api/` folder?

```bash
# 1. Rebuild Lambda package (Docker must be running)
./scripts/build-lambda.sh

# 2. Upload to S3
aws s3 cp terraform/builds/fastapi-app.zip s3://YOUR_BUCKET_NAME/lambda/fastapi-app.zip

# 3. Update Lambda function
aws lambda update-function-code \
  --function-name YOUR_LAMBDA_FUNCTION_NAME \
  --s3-bucket YOUR_BUCKET_NAME \
  --s3-key lambda/fastapi-app.zip
```

### Scenario C: Resume Data (Excel file)

Changed your Excel resume data?

```bash
AWS_ENDPOINT_URL="" AWS_REGION="us-east-1" python3 scripts/load_resume.py path/to/your-resume-data.xlsx
```

No Lambda rebuild needed - this directly updates DynamoDB.

### Scenario D: Infrastructure (Terraform files)

Changed Terraform configuration?

```bash
cd terraform
terraform plan    # Review changes
terraform apply   # Apply changes
```

### Scenario E: Full Deploy (Everything)

Changed multiple things? Run them all:

```bash
# 1. Infrastructure (if changed)
cd terraform && terraform apply && cd ..

# 2. Lambda code
./scripts/build-lambda.sh
aws s3 cp terraform/builds/fastapi-app.zip s3://YOUR_BUCKET_NAME/lambda/fastapi-app.zip
aws lambda update-function-code \
  --function-name YOUR_LAMBDA_FUNCTION_NAME \
  --s3-bucket YOUR_BUCKET_NAME \
  --s3-key lambda/fastapi-app.zip

# 3. Resume data
AWS_ENDPOINT_URL="" AWS_REGION="us-east-1" python3 scripts/load_resume.py path/to/your-resume-data.xlsx

# 4. Frontend
aws s3 cp app/index.html s3://YOUR_BUCKET_NAME/index.html
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

---

## Finding Your Resource IDs

Don't know your bucket name or distribution ID? Here's how to find them:

### S3 Bucket Name
```bash
aws s3 ls
# Or from Terraform:
cd terraform && terraform output s3_bucket_name
```

### CloudFront Distribution ID
```bash
aws cloudfront list-distributions --query "DistributionList.Items[*].[Id,DomainName]" --output table
# Or from Terraform:
cd terraform && terraform output cloudfront_distribution_id
```

### Lambda Function Name
```bash
aws lambda list-functions --query "Functions[*].FunctionName" --output table
```

### API Gateway URL
```bash
aws apigateway get-rest-apis --query "items[*].[name,id]" --output table
# URL format: https://{api-id}.execute-api.{region}.amazonaws.com/prod/api
```

---

## Troubleshooting

### Check Lambda Logs
```bash
aws logs tail /aws/lambda/YOUR_LAMBDA_FUNCTION_NAME --since 10m
```

### Check API Health
```bash
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/api/health
```

### Check DynamoDB Item Count
```bash
aws dynamodb scan --table-name ResumeData --select "COUNT"
```

### Docker Not Running
If `build-lambda.sh` fails with "Cannot connect to Docker daemon":
1. Open Docker Desktop
2. Wait for it to fully start (green icon)
3. Run the build script again

### Python Version Issues
Use `python3` not `python`:
```bash
python3 --version  # Should be 3.10+
```

### Lambda Package Too Large
The package is 80MB+ so we use S3 (not direct upload):
```bash
./scripts/build-lambda.sh
aws s3 cp terraform/builds/fastapi-app.zip s3://YOUR_BUCKET/lambda/fastapi-app.zip
```

Make sure `terraform/lambda.tf` uses `s3_bucket` and `s3_key`, not `filename`.

---

## Deployment Checklist

Before deploying to production:

- [ ] Email verified in SES (`aws ses get-identity-verification-attributes`)
- [ ] reCAPTCHA keys configured (`.env` and `index.html`)
- [ ] Resume data in Excel template is complete
- [ ] Profile photo and resume PDF are in `app/assets/`
- [ ] Domain name in `terraform/variables.tf` (if using custom domain)
- [ ] AWS credentials configured (`aws configure`)
- [ ] Lambda package built (`./scripts/build-lambda.sh`)
- [ ] All tests passing (`docker compose exec api pytest tests/`)

---

## Notes

- Auto-seed in `main.py` only runs locally (localhost/localstack)
- Production data is loaded by running `load_resume.py` locally with `AWS_ENDPOINT_URL=""`
- CloudFront caches content - always invalidate after changes (or wait hours)
- Lambda package build requires Docker for Linux compatibility
- Use `python3` not `python` for the load script
