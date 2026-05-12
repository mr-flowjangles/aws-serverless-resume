# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Serverless resume website running the **same FastAPI codebase** locally (Docker + Nginx + LocalStack) and in production (AWS Lambda via Mangum + API Gateway + CloudFront + DynamoDB).

The AI chatbot module (`ai/`) has been extracted to a separate bot-factory repository.

### Frontend / Backend split

The frontend in `app/` is a single-page site (`index.html` + `styles.css` + `brand-tokens.css` + `script.js` + `fonts/`). Editorial content (hero copy, Journey chapters, Architecture SVG, contact form) is hardcoded. The **Experience, Skills, and Education** sections are loaded at runtime from `/api/resume` by `script.js` — yes, this is overkill for a resume site, and that is intentional. The Architecture section explains why.

API endpoints in use:
- `/api/resume` — full resume payload (profile + work_experience + education + skills); consumed by `script.js` on page load
- `/api/contact` — contact-form submissions via SES (with reCAPTCHA)
- `/api/health` — DynamoDB connectivity check

## Common Commands

### Local Development
```bash
make up          # Start all services (docker compose up --build -d)
make down        # Stop all services
make logs        # Tail service logs
make build       # Rebuild images (no cache)
```

### Running Tests
```bash
docker compose exec api pytest tests/ -v               # Run all tests
docker compose exec api pytest tests/test_health.py -v  # Run single test file
docker compose exec -T api pytest tests/ -v             # Non-interactive (used by pre-commit)
```

### Loading Resume Data
```bash
docker compose exec api python /app/scripts/load_resume.py /app/_scratch/your-resume.xlsx
```

### Building Lambda Package
```bash
./scripts/build-lambda.sh   # Outputs terraform/builds/fastapi-app.zip
```

### Infrastructure
```bash
cd terraform && terraform plan    # Preview changes
cd terraform && terraform apply   # Deploy to AWS
```

## Architecture

### Dual-Environment Pattern
The core design principle: one FastAPI app, two runtimes.
- **Local**: `docker-compose.yml` runs Nginx (port 8080) → FastAPI (uvicorn on :8000) → LocalStack DynamoDB
- **Lambda**: `lambda_handler.py` wraps the FastAPI app with Mangum. CloudFront routes `/api/*` to Lambda Function URL (streaming enabled).
- Route prefix logic in `api/main.py`: Lambda adds `/api` prefix; locally, Nginx handles the prefix via proxy.

### Router → Handler Separation
- **Routers** (`api/routers/`): FastAPI endpoint definitions, request/response formatting
- **Handlers** (`api/handlers/`): Environment-agnostic business logic with no FastAPI imports — testable independently and callable from either runtime

### Data Flow
Excel template (`scripts/resume-data-template.xlsx`) → `scripts/load_resume.py` → DynamoDB `ResumeData` table (partitioned by `type`: profile, work_experience, education, skills) → `handlers/resume_all.py` (module-level cache for Lambda warm starts) → `/api/resume` → `script.js` renders into the page's `#exp-list`, `#skills-grid`, `#edu-list` containers. The chat widget posts directly to a separate bot-factory Lambda Function URL (apiKey hardcoded in `app/script.js`).

### DynamoDB Tables
- **ResumeData**: Resume content (TypeIndex GSI for querying by type)

## Key Entry Points
- `api/main.py` — FastAPI app initialization, lifespan manager, router registration
- `api/lambda_handler.py` — Mangum wrapper (Lambda entry point)
- `api/seed.py` — Auto-seeds DynamoDB on local startup if table is empty

## Pre-commit Hooks
pytest runs automatically before every commit via `.pre-commit-config.yaml`. Tests execute inside the Docker container, so services must be running (`make up`) before committing.

## Infrastructure (Terraform)
100% IaC in `terraform/`. Key resources: Lambda (512MB, 30s timeout, streaming), API Gateway (50 req/s throttle), CloudFront, S3 (static assets, OAC), DynamoDB (on-demand), Route 53, ACM, SES, IAM. Sensitive values managed via Terraform variables (not hardcoded).
