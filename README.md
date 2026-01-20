# AWS Serverless Resume

## NOTE: THIS IS STILL A WORK IN PROGRESS ##
A serverless resume website that runs the **same FastAPI code** locally (Docker) and in production (AWS Lambda). Update your resume via Excel, deploy with Terraform.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/aws-serverless-resume.git
cd aws-serverless-resume
```

### 2. Add Your Resume Data

Open `scripts/resume-data-template.xlsx` in Excel or Google Sheets and fill in:

- Profile (name, title, contact info, summary)
- Work Experience
- Education
- Skills

Save the file when done.

### 3. Configure reCAPTCHA (for Contact Form)

1. **Get reCAPTCHA keys:** Visit https://www.google.com/recaptcha/admin

   - Register your site (use `localhost` for local development)
   - Choose reCAPTCHA v2 ("I'm not a robot" checkbox)
   - Get your **Site Key** and **Secret Key**

2. **Add secret key to `.env` file:**

   - rename `.env.example` to `.env`

   ```bash
   # Create .env file in project root if it doesn't exist
   echo "MY_RECAPTCHA_SECRET_KEY=your_secret_key_here" >> .env
   ```

3. **Add site key to `app/index.html`:**
   - Open `app/index.html`
   - Find the contact form section
   - Replace `data-sitekey="YOUR_SITE_KEY_HERE"` with your actual site key

_Skip this if you just want to see the site (contact form won't work)._

### 4. Available Commands

```bash
make up       # Start everything (build and run)
make down     # Stop all services
make logs     # View container logs
make restart  # Restart all services
```

_Don't have `make`? Use `docker compose up --build` instead of `make up`_

### 5. Run It

```bash
make up
```

Wait for containers to start (about 30 seconds). Watch for these lines in the logs:

```
Database already seeded, skipping...
Application startup complete.
```

Then open:

- **Website:** http://localhost:8080
- **API Docs:** http://localhost:8080/api/docs
- **Health Check:** http://localhost:8080/api/health

### 6. Verify It's Working

**Test the API directly:**

```bash
curl http://localhost:8080/api/health
# Should return: {"status":"healthy","services":{"dynamodb":"ok"}}

curl http://localhost:8080/api/resume/profile
# Should return your profile data from the Excel template
```

**In your browser:**

- Navigate to http://localhost:8080
- Your name and profile should appear
- Click through Work Experience, Education, Skills sections
- All data should come from your Excel template

Your resume is now live locally!

---

## Update Your Resume Data

After editing `scripts/resume-data-template.xlsx`:

```bash
docker exec -it resume-api-1 python /app/scripts/load_resume.py /app/scripts/resume-data-template.xlsx
```

Refresh your browser - changes appear immediately (no restart needed).

---

## Deploy to AWS

### Prerequisites

- AWS account with credentials configured
- Terraform installed
- Domain registered in Route 53 (or update `terraform/variables.tf`)

### Deploy

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

You'll get your production URLs as output.

**Estimated cost:** ~$5-10/month for low-traffic site.

---

## How It Works

### Local Development

```
Browser → Nginx → FastAPI (Docker) → LocalStack DynamoDB
```

### Production (AWS)

```
Browser → CloudFront → API Gateway → Lambda (FastAPI + Mangum) → DynamoDB
```

**Same Python code runs in both environments.** Mangum adapts FastAPI to work in Lambda.

---

## Project Structure

```
.
├── api/                          # FastAPI Backend Application
│   ├── routers/                  # API Endpoints (HTTP layer)
│   │   ├── contact.py            # POST /contact - Contact form submission
│   │   ├── health.py             # GET /health - Health check
│   │   └── resume.py             # GET /resume/* - Resume data endpoints
│   ├── handlers/                 # Business Logic (used by routers)
│   │   ├── db.py                 # DynamoDB connection helper
│   │   ├── contact.py            # Contact form logic & reCAPTCHA
│   │   ├── health.py             # Health check & DynamoDB connectivity
│   │   ├── profile.py            # Profile data retrieval
│   │   ├── work_experience.py    # Work history (sorted by date)
│   │   ├── education.py          # Education history (sorted by date)
│   │   └── skills.py             # Skills by category (sorted)
│   ├── tests/                    # Pytest Test Suite
│   │   ├── test_profile.py       # Profile handler tests
│   │   ├── test_work_experience.py
│   │   ├── test_education.py
│   │   ├── test_skills.py
│   │   ├── test_contact.py       # Contact form tests (async & sync)
│   │   └── test_health.py        # Health check tests
│   ├── main.py                   # FastAPI app (entry point)
│   ├── lambda_handler.py         # Mangum wrapper (FastAPI → Lambda)
│   ├── models.py                 # Pydantic data models
│   ├── seed.py                   # Auto-seed database on startup
│   ├── Dockerfile                # API container image
│   └── requirements.txt          # Python dependencies
│
├── app/                          # Frontend Static Site
│   ├── index.html                # Main HTML (includes all sections)
│   └── assets/                   # Static files
│       ├── profile.jpg           # Profile photo (update with yours)
│       └── resume.pdf            # Resume PDF (update with yours)
│
├── scripts/                      # Data Management
│   ├── resume-data-template.xlsx # Excel template (edit this!)
│   ├── load_resume.py            # Load Excel → DynamoDB
│   └── init-dynamodb.sh          # Initialize DynamoDB table
│
├── terraform/                    # AWS Infrastructure (IaC)
│   ├── main.tf                   # Provider configuration
│   ├── variables.tf              # Input variables (domain, region, etc.)
│   ├── outputs.tf                # Output values (URLs, ARNs)
│   ├── s3.tf                     # S3 bucket for static files
│   ├── cloudfront.tf             # CloudFront distribution
│   ├── route53.tf                # DNS records
│   ├── acm.tf                    # SSL certificate
│   ├── dynamodb.tf               # DynamoDB table
│   ├── lambda.tf                 # Lambda function (FastAPI app)
│   ├── api_gateway.tf            # API Gateway (proxy to Lambda)
│   └── iam.tf                    # IAM roles & policies
│
├── nginx/                        # Nginx Reverse Proxy (local only)
│   └── default.conf              # Routes /api/* to FastAPI
│
├── docker/                       # Docker Configuration
│   └── Dockerfile                # FastAPI container build
│
├── docker-compose.yml            # Local Development Stack
├── Makefile                      # Common commands (up, down, logs, etc.)
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (add yours)
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

### Key Architectural Patterns

**Separation of Concerns:**

- `routers/` = HTTP handling (request validation, responses, error handling)
- `handlers/` = Business logic (database queries, data transformation)
- Routers call handlers, handlers don't know about HTTP

**Single Source of Truth:**

- Business logic in `handlers/` is used by BOTH local FastAPI and AWS Lambda
- No code duplication between environments
- Same tests verify both local and production behavior

**Infrastructure as Code:**

- All AWS resources defined in Terraform
- Version controlled, reproducible deployments
- Local development mirrors production architecture

---

## Configure Contact Form

The contact form requires Google reCAPTCHA v2:

1. **Get keys:** https://www.google.com/recaptcha/admin
2. **Add secret to `.env`:**
   ```
   MY_RECAPTCHA_SECRET_KEY=your_secret_key_here
   ```
3. **Add site key to `app/index.html`** in the contact form section
4. **Restart:** `make restart`

---

## Troubleshooting

**Port 8080 already in use:**

```bash
make down
# Kill process using port 8080
make up
```

**Changes not showing:**

- Hard refresh browser: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Verify you reloaded data after editing Excel template
- Check API: `curl http://localhost:8080/api/resume/profile`

**Database empty after startup:**

```bash
make logs | grep seed
```

Manually reload if needed:

```bash
docker exec -it resume-api-1 python /app/scripts/load_resume.py /app/scripts/resume-data-template.xlsx
```

**Container won't start:**

```bash
make down
make up
```

---

## Run Tests

```bash
docker compose exec api pytest tests/ -v
```

All 13 tests should pass.

---

## Customization

**Add your photo:**

- Place image at `app/assets/profile.jpg`
- Update path in Excel template Profile sheet

**Add your resume PDF:**

- Place PDF at `app/assets/resume.pdf`
- Update path in Excel template Profile sheet

**Modify styling:**

- Edit CSS in `app/index.html`

---

## Tech Stack

**Backend:** Python, FastAPI, Mangum  
**Database:** DynamoDB (LocalStack locally, AWS in production)  
**Frontend:** HTML, CSS, JavaScript  
**Local Dev:** Docker, Nginx  
**AWS:** Lambda, API Gateway, S3, CloudFront, Route 53  
**Infrastructure:** Terraform

---

## Why This Architecture?

Most resume sites require separate code for local development and production. This project uses **FastAPI + Mangum** to run the same code everywhere:

- Develop locally with full FastAPI features (Swagger docs, hot reload, debugging)
- Deploy to AWS Lambda without changing application code
- Business logic in `handlers/` works identically in both environments
- Only the wrapper changes (`uvicorn` locally, `Mangum` in Lambda)

---

## For Contributors

Install pre-commit hooks to auto-run tests before commits:

```bash
brew install pre-commit
pre-commit install
```

Now tests run automatically, ensuring code quality.

---

## License

© 2026 Rob Rose. All rights reserved.

This project is provided for personal and educational use. If you fork or reuse, please provide attribution.

---

**Questions?** Open an issue.  
**Want to use this?** Fork it and customize!
