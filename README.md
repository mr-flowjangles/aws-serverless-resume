# aws-serverless-resume

A serverless resume application built on AWS, demonstrating API-driven content, managed cloud services, and infrastructure as code.

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
