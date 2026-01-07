# aws-serverless-resume

A serverless resume application built on AWS, demonstrating API-driven content, managed cloud services, and infrastructure as code.

### Adding Your Resume Data

**Important:** Your personal resume data should NOT be committed to Git.

1. Copy the example seed file:

```bash
   cp config/seed-data.example.json config/seed-data.json
```

2. Edit `config/seed-data.json` with your actual experience, skills, education, and projects

3. The file is gitignored and will not be committed

4. On startup, the application will automatically seed DynamoDB with your data

**Data Structure:**

Each experience item should include:

- `id`: Unique identifier (e.g., "experience-1")
- `type`: Always "experience"
- `company`: Company name
- `title`: Your job title
- `startDate`: Format as "YYYY-MM"
- `endDate`: Use "present" for current role or "YYYY-MM"
- `description`: Overview paragraph
- `highlights`: Array of bullet points (your accomplishments)
- `skills`: Array of relevant technologies/skills

## Project Structure

```
.
├── app/                    # Frontend (static HTML/CSS/JS)
│   └── index.html         # Main website
├── api/                    # Backend API (FastAPI)
│   ├── main.py            # Main FastAPI app
│   ├── health.py          # Health check endpoints
│   ├── resume.py          # Resume data endpoints
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # API container image
├── config/                 # Configuration files
│   └── general-data.json  # Profile configuration (EDIT THIS!)
├── docker/                 # Docker configurations
│   └── Dockerfile         # Web server image
├── nginx/                  # Nginx reverse proxy config
│   └── default.conf       # Routing configuration
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── docker-compose.yml     # Local development setup
├── Makefile               # Common commands
└── README.md              # This file
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Configuration

**Edit your profile information:**

1. Open `config/general-data.json`
2. Update the following fields with your information:

```json
{
  "profile": {
    "name": "Your Name",
    "title": "Your Professional Title",
    "email": "your.email@example.com",
    "location": "Your City, State",
    "photo": "/assets/profile.jpg",
    "summary": "Your professional summary here.",
    "links": {
      "github": "https://github.com/yourusername",
      "linkedin": "https://linkedin.com/in/yourusername",
      "resume_pdf": "/assets/resume.pdf"
    }
  }
}
```

3. Save the file

### Local Development

**Start the application:**

```bash
make up
```

**View the site:**

Open [http://localhost:8080](http://localhost:8080)

**View API documentation:**

Open [http://localhost:8080/api/docs](http://localhost:8080/api/docs)

**Stop the application:**

```bash
make down
```

**Rebuild after changes:**

```bash
make down
docker compose build --no-cache
make up
```

## Architecture

### Local Development

**Start the application:**

```bash
make up
```

The DynamoDB table will be created automatically on startup.

**View the site:**

Open [http://localhost:8080](http://localhost:8080)

**View API documentation:**

Open [http://localhost:8080/api/docs](http://localhost:8080/api/docs)

**View logs:**

```bash
make logs
```

Press Ctrl+C to exit logs.

**Stop the application:**

```bash
make down
```

**Rebuild after code changes:**

```bash
make build
make up
```

**Available commands:**

```bash
make help    # Show all available commands
make up      # Start all services
make down    # Stop all services
make build   # Rebuild all images
make logs    # View service logs
```

```
Browser
  ↓
Nginx (web) - Port 8080
  ↓ (serves static files)
  ↓ (proxies /api/* requests)
  ↓
FastAPI (api) - Port 8000
  ↓
LocalStack (S3, DynamoDB) - Port 4566
```

### AWS Deployment (Future)

```
CloudFront
  ↓
S3 (static files)

API Gateway
  ↓
Lambda Functions
  ↓
DynamoDB
```

## API Endpoints

- `GET /api/health` - Service health check
- `GET /api/resume/profile` - Get profile information

## Technologies

- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Backend**: Python FastAPI
- **Local AWS**: LocalStack (S3, DynamoDB)
- **Containers**: Docker, Docker Compose
- **Reverse Proxy**: Nginx

## DynamoDB Commands (Local Development)

### List all tables

```bash
docker exec -it resume-api-1 aws --endpoint-url=http://localstack:4566 dynamodb list-tables
```

### Describe table structure

```bash
docker exec -it resume-api-1 aws --endpoint-url=http://localstack:4566 dynamodb describe-table --table-name ResumeData
```

### Scan all items in table

```bash
docker exec -it resume-api-1 aws --endpoint-url=http://localstack:4566 dynamodb scan --table-name ResumeData
```

### Get specific item by ID

```bash
docker exec -it resume-api-1 aws --endpoint-url=http://localstack:4566 dynamodb get-item \
    --table-name ResumeData \
    --key '{"id":{"S":"experience-1"}}'
```

### Put an item

```bash
docker exec -it resume-api-1 aws --endpoint-url=http://localstack:4566 dynamodb put-item \
    --table-name ResumeData \
    --item '{"id":{"S":"test-id"},"type":{"S":"experience"},"data":{"S":"test data"}}'
```

### Query items by type (using GSI)

```bash
docker exec -it resume-api-1 aws --endpoint-url=http://localstack:4566 dynamodb query \
    --table-name ResumeData \
    --index-name TypeIndex \
    --key-condition-expression "#t = :type" \
    --expression-attribute-names '{"#t":"type"}' \
    --expression-attribute-values '{":type":{"S":"experience"}}'
```

### Delete table

```bash
docker exec -it resume-api-1 aws --endpoint-url=http://localstack:4566 dynamodb delete-table --table-name ResumeData
```

## Future Enhancements

- Terraform for AWS deployment
- Experience, Skills, Education endpoints with DynamoDB
- Contact form with email integration
- CI/CD pipeline
- Angular frontend (optional)

## License

© 2026 Rob Rose. All rights reserved.

This project is provided for personal and educational purposes. If reused or forked, please retain this notice and provide attribution.

## Acknowledgments

- Frontend design assisted by AI
- Built to demonstrate serverless architecture patterns on AWS
