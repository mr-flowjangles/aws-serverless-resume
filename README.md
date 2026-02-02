# AWS Serverless Resume

A serverless resume website that runs the **same FastAPI code** locally (Docker) and in production (AWS Lambda). Update your resume via Excel, deploy with Terraform.

**Live Example:** [robrose.info](https://robrose.info)

---

## Before You Start: Configuration

Let's get the boring config stuff out of the way first. You'll need to set up a few things before running the site.

I have a folder called `_scratch` I use this folder for storing my information, files, AI embeddings so they aren't loaded to github. Create your own `_scratch` as some scripts may export to `_scratch`

From the root, `mkdir -p _scratch`

### 1. Google reCAPTCHA (Required for Contact Form)

The contact form uses Google reCAPTCHA v2 to prevent spam. Here's how to set it up:

**Get your keys:**

1. Go to https://www.google.com/recaptcha/admin
2. Register a new site
3. Choose **reCAPTCHA v2** ("I'm not a robot" checkbox)
4. Add domains:
   - For local development: `localhost`
   - For production: `yourdomain.com`
5. You'll get two keys:
   - **Site Key** (goes in your HTML)
   - **Secret Key** (goes in your .env file)

**Add to your project:**

1. Create a `.env` file in the project root:

   ```bash
   cp .env.example .env
   ```

2. Add your secret key:

   ```bash
   RECAPTCHA_SECRET_KEY=your_secret_key_here
   ```

3. Update `app/index.html` - find the contact form and replace:
   ```html
   <div class="g-recaptcha" data-sitekey="YOUR_SITE_KEY_HERE"></div>
   ```
   With your actual site key.

**Skip this?** You can run the site without it, but the contact form won't work.

---

### 2. AWS SES (Required for Email Delivery)

The contact form sends emails via AWS Simple Email Service (SES). Here's the setup:

**Verify your email address:**

```bash
# This sends a verification email to you
aws ses verify-email-identity --email-address your@email.com --region us-east-1

# Check verification status
aws ses get-identity-verification-attributes --identities your@email.com --region us-east-1
```

Check your email and click the verification link. Wait until status shows `"VerificationStatus": "Success"`.

**Add to your .env file:**

```bash
SES_FROM_EMAIL=your@email.com
SES_TO_EMAIL=your@email.com
```

**SES Sandbox Mode:**

- New AWS accounts start in SES sandbox
- You can only send TO verified email addresses
- Since both sender and recipient are the same verified email, this works fine
- To send to any email address, request production access in the AWS console

**Important:** Make sure your Lambda has SES permissions (already configured in `terraform/iam.tf`).

---

### 3. AWS Credentials (Required for Deployment)

You'll need AWS credentials configured on your machine:

```bash
aws configure
```

Enter your:

- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)

**Don't have AWS credentials?** You can still run locally - just skip the deployment steps.

---

### 4. Domain Name (Optional but Recommended)

If you want a custom domain like `yourname.com`:

1. Register domain in Route 53 (or transfer existing domain)
2. Update `terraform/variables.tf` with your domain
3. Terraform will handle SSL certificates and DNS automatically

**Don't have a domain?** You'll get CloudFront and API Gateway URLs instead (still works perfectly).

---

## Quick Start

Now that config is done, let's get your resume site running!

### 1. Clone and Enter

```bash
git clone https://github.com/yourusername/aws-serverless-resume.git
cd aws-serverless-resume
```

### 2. Add Your Resume Data

Open `scripts/resume-data-template.xlsx` in Excel or Google Sheets and fill in:

- **Profile Sheet:** Name, title, contact info, summary, links
- **Work Experience Sheet:** Job title, company, dates, description, accomplishments
  - Set `is_additional` to `TRUE` for older jobs you want displayed as a simple list
- **Education Sheet:** Degree, institution, dates, description
- **Skills Sheet:** Category, skills (pipe-separated)

Save when done. This is your single source of truth for all resume data.

### 3. Run It Locally

```bash
# Start everything (builds containers, starts services, seeds database)
make up
```

**Don't have `make`?** Use: `docker compose up --build`

Wait about 30 seconds. Watch for these lines:

```
Database already seeded, skipping...
Application startup complete.
```

**Then open:**

- **Your Resume:** http://localhost:8080
- **API Docs:** http://localhost:8080/api/docs
- **Health Check:** http://localhost:8080/api/health

### 4. Verify It Works

**In your browser:** Navigate around - everything should load from your Excel data.

**Test the API:**

```bash
curl http://localhost:8080/api/health
# Should return: {"status":"healthy","services":{"dynamodb":"ok"}}

curl http://localhost:8080/api/resume/profile
# Should return your profile data
```

**Test the contact form:** Fill it out and submit. If reCAPTCHA is configured, you'll see a success message.

Your resume is now live locally! 🎉

---

## Update Your Resume (Local)

Made changes to `scripts/resume-data-template.xlsx`? Reload the data:

```bash
docker exec -it resume-api-1 python /app/scripts/load_resume.py /app/scripts/resume-data-template.xlsx
```

Refresh your browser - changes appear immediately. No restart needed.

---

## Deploy to AWS

Ready to go live? See **[README_DEPLOY.md](README_DEPLOY.md)** for complete deployment instructions including:

- Part 1: Deploy from scratch
- Part 2: Updates after initial deploy (frontend, Lambda, data, infrastructure)
- Finding your resource IDs
- Troubleshooting

---

## How It Works

This project's secret sauce: **same code runs everywhere**.

### Local Development (Docker)

```
Browser → Nginx → FastAPI (uvicorn) → LocalStack DynamoDB
```

- Full FastAPI development server with hot reload
- Interactive API docs at `/api/docs`
- LocalStack simulates AWS services locally
- Fast, free, no internet required

### Production (AWS)

```
Browser → CloudFront → API Gateway → Lambda (FastAPI + Mangum) → DynamoDB
```

- Same Python code, different wrapper
- Mangum adapts FastAPI to Lambda's event format
- No servers to manage, auto-scales to zero
- Pay only for actual usage

### The Magic: Mangum

```python
# Local: uvicorn runs your FastAPI app directly
# Lambda: Mangum wraps it to handle Lambda events

from mangum import Mangum
from main import app

handler = Mangum(app)  # That's it!
```

Your business logic in `handlers/` never knows the difference.

---

## Project Structure

```
aws-serverless-resume/
├── api/                    # Backend code (runs in Lambda)
│   ├── handlers/           # Business logic (environment-agnostic)
│   ├── routers/            # FastAPI route definitions
│   ├── main.py             # FastAPI app setup
│   ├── lambda_handler.py   # Mangum wrapper for AWS Lambda
│   └── seed.py             # Database seeding logic
├── app/                    # Frontend (served by CloudFront)
│   ├── index.html          # Main page
│   └── assets/             # CSS, images, PDF resume
├── scripts/
│   ├── resume-data-template.xlsx  # Your resume data
│   ├── load_resume.py      # Excel → DynamoDB loader
│   └── build-lambda.sh     # Lambda package builder
├── terraform/              # Infrastructure as Code
│   ├── main.tf             # Provider config
│   ├── lambda.tf           # Lambda function
│   ├── api_gateway.tf      # API Gateway
│   ├── dynamodb.tf         # Database table
│   ├── s3.tf               # Static file bucket
│   ├── cloudfront.tf       # CDN distribution
│   └── ...                 # Other AWS resources
├── tests/                  # pytest test suite
├── docker-compose.yml      # Local development setup
├── Makefile                # Convenience commands
├── README.md               # This file
└── README_DEPLOY.md        # Deployment guide
```

---

## Excel Template Fields

### Profile Sheet

| Field                | Description                           |
| -------------------- | ------------------------------------- |
| name                 | Your full name                        |
| title                | Job title (e.g., "Software Engineer") |
| email                | Contact email                         |
| location             | City, State                           |
| summary              | Brief professional summary            |
| professional_summary | Detailed summary (optional)           |
| linkedin             | LinkedIn profile URL                  |
| github               | GitHub profile URL                    |
| photo                | Path to profile photo                 |
| resume_pdf           | Path to PDF resume                    |

### Work Experience Sheet

| Field           | Description                                                           |
| --------------- | --------------------------------------------------------------------- |
| job_title       | Position title                                                        |
| company_name    | Company name                                                          |
| start_date      | Start date (YYYY-MM format)                                           |
| end_date        | End date or leave blank if current                                    |
| is_current      | TRUE if current job                                                   |
| is_additional   | TRUE to display as simple list item instead of full card              |
| description     | Role description                                                      |
| accomplishments | Pipe-separated list (e.g., "Led team\|Increased sales\|Built system") |

### Education Sheet

| Field       | Description        |
| ----------- | ------------------ |
| degree      | Degree name        |
| institution | School name        |
| start_date  | Start date         |
| end_date    | End date           |
| description | Additional details |

### Skills Sheet

| Field      | Description                                            |
| ---------- | ------------------------------------------------------ |
| category   | Skill category (e.g., "Languages")                     |
| skills     | Pipe-separated skills (e.g., "Python\|JavaScript\|Go") |
| sort_order | Display order (lower numbers first)                    |

---

## Customization

### Modify Styling

Edit the `<style>` section in `app/index.html`. CSS is embedded for simplicity.

### Change Colors

Look for color definitions in `app/index.html`:

- `#0ea5e9` - Primary blue (links, accents)
- `#0f172a` - Dark background
- `#f0f4f8` - Light background

---

## Troubleshooting

### Port 8080 Already in Use

```bash
make down
# Find what's using port 8080
lsof -ti:8080 | xargs kill -9
make up
```

### Changes Not Showing Up

**For data changes:**

```bash
make reload  # Reload Excel template
```

**For code changes:**

```bash
make restart  # Restart containers
```

**For HTML/CSS changes:**

- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)

### Database Empty After Startup

Check if seeding happened:

```bash
make logs | grep seed
```

Manually reload if needed:

```bash
docker exec -it resume-api-1 python /app/scripts/load_resume.py /app/scripts/resume-data-template.xlsx
```

### Contact Form Not Working

**Check reCAPTCHA:**

1. Site key in `app/index.html`?
2. Secret key in `.env`?
3. Correct variable name: `RECAPTCHA_SECRET_KEY` (not `MY_RECAPTCHA_SECRET_KEY`)

**Check email:**

1. Is your email verified in SES?
2. Are SES env vars in `.env`?

### Container Won't Start

```bash
make down
docker system prune -a  # Clean everything
make up
```

---

## Running Tests

Run the full test suite:

```bash
docker compose exec api pytest tests/ -v
```

All tests should pass. If contact tests fail, make sure you've updated `tests/test_contact.py` to mock the SES client (not try to actually send emails).

**Pre-commit hooks:**

```bash
brew install pre-commit  # or apt-get, pip, etc.
pre-commit install
```

Now tests run automatically before every commit.

---

## Tech Stack

**Backend:** Python 3.12, FastAPI, Mangum, boto3  
**Database:** DynamoDB (LocalStack locally, AWS in production)  
**Frontend:** HTML, CSS, vanilla JavaScript (no framework needed)  
**Email:** AWS SES  
**Security:** Google reCAPTCHA v2  
**Local Dev:** Docker, Docker Compose, Nginx, LocalStack  
**AWS:** Lambda, API Gateway, S3, CloudFront, Route 53, ACM, DynamoDB, SES  
**Infrastructure:** Terraform (100% IaC)  
**Testing:** pytest, pre-commit hooks

---

## Why This Architecture?

**Most resume sites have a problem:** You write one version for local development (Django, Flask, Express) and another for production (Lambda, serverless functions). This means:

- Two codebases to maintain
- Different bugs in each environment
- Can't easily test production code locally

**This project solves that** with FastAPI + Mangum:

✅ Write once, run everywhere  
✅ Full FastAPI features locally (hot reload, Swagger docs, debugging)  
✅ Deploy to Lambda without changing application code  
✅ Business logic in `handlers/` is environment-agnostic  
✅ Only the wrapper changes (`uvicorn` vs `Mangum`)

**The result:** You develop fast with full features, then deploy the same tested code to production. No surprises, no translations, no second version.

---

## Cost Breakdown (Estimated)

For a personal resume site with low traffic (<1000 visitors/month):

| Service         | Cost        | Notes                                    |
| --------------- | ----------- | ---------------------------------------- |
| Route 53        | $0.50/month | Hosted zone                              |
| CloudFront      | $1-2/month  | CDN, first 1TB free                      |
| Lambda          | $0-1/month  | First 1M requests free                   |
| API Gateway     | $0-1/month  | First 1M requests free                   |
| DynamoDB        | $0/month    | 25GB free tier                           |
| SES             | $0/month    | 62,000 emails/month free from EC2/Lambda |
| S3              | $0.50/month | Storage and requests                     |
| ACM Certificate | FREE        | SSL certificate                          |

**Total: ~$3-10/month** depending on traffic.

**High traffic?** Costs scale proportionally but AWS free tier is generous. A site with 10,000 visitors/month might be $20-30/month.

---

## Security Notes

**Secrets Management:**

- Never commit `.env` to Git (already in `.gitignore`)
- Use environment variables for all secrets
- AWS credentials should use IAM roles, not hardcoded keys

**API Security:**

- reCAPTCHA prevents spam on contact form
- API Gateway has built-in DDoS protection
- CloudFront provides additional security layer
- Lambda runs in isolated execution environment

**Data Privacy:**

- Your resume data is in your AWS account only
- No third-party services have access
- DynamoDB data is encrypted at rest (AWS default)

---

## For Contributors

Want to improve this project? Great!

**Development workflow:**

1. Fork the repo
2. Create a feature branch
3. Install pre-commit hooks: `pre-commit install`
4. Make changes and test locally
5. Tests run automatically on commit
6. Open a PR with description of changes

**Code style:**

- Follow existing patterns (routers call handlers)
- Write tests for new features
- Keep handlers environment-agnostic
- Document any new configuration

---

## FAQ

**Q: Can I use this without AWS?**  
A: Yes! It runs great locally with Docker. You just won't have the production deployment.

**Q: Can I use my own domain?**  
A: Yes! Register it in Route 53 and update `terraform/variables.tf`. Terraform handles SSL and DNS automatically.

**Q: Does this work with GitHub Pages?**  
A: The frontend could, but you'd lose the API (contact form, dynamic data). The Lambda + API Gateway setup is what makes it powerful.

**Q: Can I add a blog?**  
A: Absolutely! Add a new handler in `handlers/blog.py`, a router in `routers/blog.py`, and update `index.html`. Store posts in DynamoDB or add a new table.

**Q: How do I add multiple pages?**  
A: The current design is single-page for simplicity. You can add more HTML files in `app/` and route to them, or build a proper React/Vue frontend.

**Q: Can I use PostgreSQL instead of DynamoDB?**  
A: You'd need to replace the handlers and add RDS to your Terraform. The architecture supports it, but you lose some serverless benefits.

**Q: Why not use Next.js or another framework?**  
A: This is intentionally simple - no build process for frontend, no framework lock-in. You get a working resume site with minimal complexity. But you could absolutely replace the frontend!

---

## What's Next?

Some ideas for extending this project:

- [ ] Add a blog with posts stored in DynamoDB
- [ ] Integrate Google Analytics
- [ ] Add a projects section with screenshots
- [ ] Build an admin panel for editing without Excel
- [ ] Add multi-language support
- [ ] Integrate with LinkedIn API for auto-sync
- [ ] Add dark mode toggle
- [ ] Create a chatbot that answers questions about your resume (using Claude API)

Fork it and make it your own!

---

## License

© 2026 Rob Rose. All rights reserved.

This project is provided for personal and educational use. If you fork or reuse, please provide attribution and link back to the original repository.

---

## Acknowledgments

Built with:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Mangum](https://mangum.io/) - ASGI adapter for AWS Lambda
- [Terraform](https://www.terraform.io/) - Infrastructure as Code
- [LocalStack](https://localstack.cloud/) - Local AWS testing

Inspired by the cloud resume challenge and the desire to have ONE codebase that works everywhere.

---

**Questions?** Open an issue on GitHub.  
**Want to use this?** Fork it, star it, and make it yours!  
**Found a bug?** PRs welcome!

---

_Made with ☕ and deployed with ☁️_
