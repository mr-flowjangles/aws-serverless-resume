# AWS Serverless Resume

A serverless resume application built on AWS, demonstrating API-driven content, managed cloud services, and infrastructure as code.

## Architecture

```
Browser
   ↓
Nginx (web)
   • Serves static files
   • Proxies /api/* requests
   ↓
FastAPI (api)
   • Private service
   • Reads from DynamoDB
   ↓
DynamoDB (LocalStack)
   • Stores resume data
```

## Project Structure

```
.
├── app/                    # Static website
│   ├── index.html         # Main HTML file
│   └── assets/            # Static assets (PDFs, images)
├── api/                    # FastAPI service
│   ├── main.py            # Application entry point
│   ├── resume.py          # Resume API endpoints
│   ├── seed.py            # Auto-seed database on startup
│   ├── health.py          # Health check endpoints
│   ├── chat.py            # Chat endpoints
│   └── Dockerfile         # API container configuration
├── scripts/                # Utility scripts
│   ├── resume-data-template.xlsx  # Excel template for resume data
│   ├── load_resume.py     # Script to load data from Excel
│   └── init-dynamodb.sh   # DynamoDB table initialization
├── nginx/                  # Nginx reverse proxy
│   └── default.conf       # Nginx configuration
├── docker/                 # Docker configuration
│   └── Dockerfile         # Web container configuration
├── docker-compose.yml      # Local infrastructure setup
├── Makefile               # Common commands
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Initial Setup

1. **Start all services:**

   ```bash
   make up
   ```

   Or using Docker Compose directly:

   ```bash
   docker compose up --build
   ```

2. **Access the application:**
   - Frontend: http://localhost:8080
   - API Documentation (Swagger): http://localhost:8080/api/docs
   - API Health Check: http://localhost:8080/api/hello

The database will automatically seed with data from `scripts/resume-data-template.xlsx` on first startup.

## Managing Your Resume Data

All resume data is managed through an Excel template: `scripts/resume-data-template.xlsx`

The template includes an Instructions sheet with detailed guidance on filling out each section.

### Editing Your Resume

**Option 1: Edit Locally in Excel**

1. Open `scripts/resume-data-template.xlsx` in Microsoft Excel
2. Update your information following the instructions in the template
3. Save the file
4. Reload data (see below)

**Option 2: Edit in Google Sheets**

1. Upload `scripts/resume-data-template.xlsx` to Google Drive
2. Edit in your browser
3. Download as Excel (.xlsx)
4. Save to `scripts/resume-data-template.xlsx`
5. Reload data (see below)

### Reloading Data

After editing the template, reload your data into DynamoDB:

```bash
docker exec -it resume-api-1 python /app/scripts/load_resume.py /app/scripts/resume-data-template.xlsx
```

**What this does:**

- Clears all existing data from DynamoDB
- Loads fresh data from your Excel template
- No container restart needed - changes appear immediately

### Auto-Seed on Startup

When you run `make up` or `docker compose up`, the API container automatically:

1. Checks if DynamoDB is empty
2. If empty, loads data from `scripts/resume-data-template.xlsx`
3. Starts serving your resume

This means you always start with your latest template data.

## Development

### Docker Commands

**Using Make (recommended):**

```bash
make up          # Start all services
make down        # Stop all services
make build       # Build Docker images
make logs        # View container logs
make restart     # Restart all services
```

**Using Docker Compose directly:**

```bash
docker compose up --build           # Build and start
docker compose down                 # Stop and remove containers
docker compose logs -f              # Follow logs
docker compose logs api             # View API logs
docker compose ps                   # List running containers
```

### Adding Static Assets

**Resume PDF:**

1. Place your resume PDF in `app/assets/resume.pdf`
2. Update the Profile sheet in your template with the path: `/assets/resume.pdf`
3. Rebuild: `make down && make up`

**Profile Photo:**

1. Place your photo in `app/assets/profile.jpg`
2. Update the Profile sheet with the path: `/assets/profile.jpg`
3. Rebuild: `make down && make up`

### API Endpoints

**Profile:**

- `GET /api/resume/profile` - Returns profile information

**Work Experience:**

- `GET /api/resume/work-experience` - Returns work history (sorted by date, current first)

**Education:**

- `GET /api/resume/education` - Returns education history (sorted by date, newest first)

**Skills:**

- `GET /api/resume/skills` - Returns skills by category (sorted by sort_order)

## AWS Deployment (Future)

### Local vs AWS Mapping

| Local Component         | AWS Service                      |
| ----------------------- | -------------------------------- |
| Nginx                   | CloudFront + S3                  |
| FastAPI                 | Lambda + API Gateway             |
| LocalStack DynamoDB     | DynamoDB                         |
| Docker network          | VPC                              |
| Excel template + script | Lambda function triggered by S3  |
| docker-compose.yml      | Terraform / CloudFormation / CDK |

### Production Data Updates

In AWS, updating your resume would work like this:

1. **Edit template** - Update Excel file locally or in Google Sheets
2. **Upload to S3** - Upload template to designated S3 bucket
3. **Trigger Lambda** - Lambda function processes Excel file
4. **Update DynamoDB** - Lambda writes data to DynamoDB
5. **Live immediately** - Website reflects changes (no deployment needed)

This separates content updates from code deployments.

## Troubleshooting

**Database is empty after restart:**

- Check that `scripts/resume-data-template.xlsx` exists
- View logs: `docker compose logs api | grep -i seed`
- Manually reload: `docker exec -it resume-api-1 python /app/scripts/load_resume.py /app/scripts/resume-data-template.xlsx`

**Changes not appearing:**

- Hard refresh browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Check you reloaded data after editing template
- Verify API returns updated data: http://localhost:8080/api/resume/profile

**Container won't start:**

- Check logs: `docker compose logs`
- Ensure ports 8080 and 4566 are available
- Try: `make down && make up`

## License

© 2026 Rob Rose. All rights reserved.

This project is provided for personal and educational purposes. If reused or forked, please retain this notice and provide attribution.

## Contributing

This is a personal project, but feedback and suggestions are welcome. Feel free to open an issue for discussion.

---

**Tech Stack:** Python • FastAPI • Docker • Nginx • DynamoDB • AWS • Excel
