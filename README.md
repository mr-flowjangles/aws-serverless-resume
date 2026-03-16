# AWS Serverless Resume

A serverless resume website that runs the **same FastAPI code** locally (Docker) and in production (AWS Lambda). Includes a floating AI chat widget powered by [Bot Factory](https://github.com/mr-flowjangles/bot-factory). Update your resume via Excel, deploy with Terraform.

**Live:** [robrose.info](https://robrose.info)

---

## Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/mr-flowjangles/aws-serverless-resume.git
cd aws-serverless-resume
cp .env.example .env
mkdir -p _scratch
```

Edit `.env` with your reCAPTCHA secret key and SES email addresses. See [Configuration](#configuration) below for details.

### 2. Add Your Resume Data

Open `scripts/resume-data-template.xlsx` in Excel or Google Sheets and fill in your profile, work experience, education, and skills.

### 3. Run Locally

```bash
make up
```

Open http://localhost:8080. API docs at http://localhost:8080/api/docs.

### 4. Deploy to AWS

See **[README_DEPLOY.md](README_DEPLOY.md)** for complete deployment instructions.

---

## How It Works

### Local Development (Docker)

```
Browser → Nginx → FastAPI (uvicorn) → LocalStack DynamoDB
```

### Production (AWS)

```
Browser → CloudFront → Lambda Function URL (FastAPI + Mangum) → DynamoDB
       → Chat Widget → Bot Factory Lambda (SSE streaming) → Bedrock Claude
```

Same Python code, different wrapper. Mangum adapts FastAPI to Lambda's event format. The RobbAI chat widget connects client-side directly to Bot Factory's streaming endpoint.

---

## Project Structure

```
aws-serverless-resume/
├── api/                        # Backend (runs in Lambda)
│   ├── handlers/               # Business logic (environment-agnostic)
│   │   ├── contact.py          # Contact form + reCAPTCHA + SES
│   │   ├── db.py               # DynamoDB connection
│   │   ├── health.py           # Health check
│   │   └── resume_all.py       # Resume data (cached)
│   ├── routers/                # FastAPI route definitions
│   ├── tests/                  # pytest suite
│   ├── main.py                 # FastAPI app setup
│   ├── lambda_handler.py       # Mangum wrapper (Lambda entry point)
│   ├── seed.py                 # Auto-seeds DynamoDB locally
│   ├── requirements.txt        # Full dependencies (local dev)
│   ├── requirements-lambda.txt # Slim dependencies (Lambda only)
│   ├── Dockerfile              # Local dev container
│   └── Dockerfile.lambda       # Lambda build container
├── app/                        # Frontend (served by CloudFront)
│   ├── index.html              # Single-page app (Welcome, About, Projects, etc.)
│   ├── scripts/
│   │   ├── api.js              # API client
│   │   ├── navigation.js       # Tab navigation and section loading
│   │   ├── architecture.js     # Architecture diagrams
│   │   ├── projects.config.js  # Project card definitions
│   │   ├── loaders.js          # Section data loaders
│   │   ├── contact.js          # Contact form handler
│   │   └── chat-widget.js      # RobbAI floating chat (connects to Bot Factory)
│   └── assets/
│       ├── main.css            # Core styles
│       ├── mobile.css          # Mobile responsive styles
│       ├── architecture.css    # Architecture section styles
│       └── chat-widget.css     # Chat widget styles
├── scripts/
│   ├── resume-data-template.xlsx  # Resume data (single source of truth)
│   ├── load_resume.py          # Excel → DynamoDB loader
│   ├── build-lambda.sh         # Lambda package builder
│   └── init-dynamodb.sh        # LocalStack table setup
├── terraform/                  # Infrastructure as Code
├── docker-compose.yml          # Local development setup
├── Makefile                    # Convenience commands
└── README_DEPLOY.md            # Deployment guide
```

---

## Configuration

### Google reCAPTCHA (Required for Contact Form)

1. Get keys at https://www.google.com/recaptcha/admin (v2, "I'm not a robot")
2. Add domains: `localhost` (dev) and your production domain
3. Put the secret key in `.env` as `RECAPTCHA_SECRET_KEY`
4. Put the site key in `app/index.html` in the `data-sitekey` attribute

### AWS SES (Required for Email Delivery)

```bash
aws ses verify-email-identity --email-address your@email.com --region us-east-1
```

Add to `.env`:
```bash
SES_FROM_EMAIL=your@email.com
SES_TO_EMAIL=your@email.com
```

### AWS Credentials

```bash
aws configure
```

### Domain Name (Optional)

Register in Route 53 and update `terraform/variables.tf`. Terraform handles SSL and DNS.

---

## Update Resume Data

```bash
# Local
docker compose exec api python /app/scripts/load_resume.py /app/scripts/resume-data-template.xlsx

# Production
AWS_ENDPOINT_URL="" AWS_REGION="us-east-1" python3 scripts/load_resume.py path/to/your-resume-data.xlsx
```

---

## Tech Stack

**Backend:** Python 3.12, FastAPI, Mangum, boto3
**Database:** DynamoDB (LocalStack locally, AWS in production)
**Frontend:** HTML, CSS, vanilla JavaScript
**AI Chat:** RobbAI widget powered by [Bot Factory](https://github.com/mr-flowjangles/bot-factory) (SSE streaming)
**Email:** AWS SES
**Security:** Google reCAPTCHA v2
**Local Dev:** Docker, Docker Compose, Nginx, LocalStack
**AWS:** Lambda (Function URL + streaming), API Gateway, S3, CloudFront, Route 53, ACM, DynamoDB, SES
**Infrastructure:** Terraform (100% IaC)
**Testing:** pytest, pre-commit hooks

---

## Running Tests

```bash
docker compose exec api pytest tests/ -v
```

Pre-commit hooks run tests automatically before every commit:
```bash
pre-commit install
```

---

## Cost Breakdown

For a personal resume site (<1,000 visitors/month): **~$3-10/month**. Route 53 ($0.50), CloudFront ($1-2), Lambda/API Gateway/DynamoDB/SES (free tier), S3 ($0.50), ACM (free).

---

## License

© 2026 Rob Rose. All rights reserved.

This project is provided for personal and educational use. If you fork or reuse, please provide attribution and link back to the original repository.

---

Built with [FastAPI](https://fastapi.tiangolo.com/), [Mangum](https://mangum.io/), [Terraform](https://www.terraform.io/), [LocalStack](https://localstack.cloud/), and [Claude](https://claude.ai) as a development partner.
