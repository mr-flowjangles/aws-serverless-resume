# AWS Serverless Resume

A serverless resume application built on AWS, demonstrating API-driven content, managed cloud services, and infrastructure as code.

## 🏗️ Architecture

```
Browser
   ↓
Nginx (web)
   • Serves static files
   • Proxies /api/* requests
   ↓
FastAPI (api)
   • Private service
   • No public port exposure
```

## 📁 Project Structure

```
.
├── app/                # Static website (index.html)
├── api/                # FastAPI service
│   ├── main.py
│   └── Dockerfile
├── nginx/              # Nginx reverse proxy config
│   └── default.conf
├── docker/             # Docker configuration files
├── docker-compose.yml  # Local infrastructure
├── Makefile            # Common commands
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Docker
- Docker Compose

### Initial Setup

1. **Create the Docker image:**
   ```bash
   docker build -t aws-serverless-resume -f docker/Dockerfile .
   ```

2. **Start all services:**
   ```bash
   docker compose up --build
   ```
   
   Or use the Makefile:
   ```bash
   make up
   ```

3. **Access the application:**
   - Frontend: http://localhost:8080
   - API Documentation (Swagger): http://localhost:8080/api/docs

## 🛠️ Development

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
docker compose ps                   # List running containers
```

**Manual Docker commands:**
```bash
# Build image
docker build -t aws-serverless-resume -f docker/Dockerfile .

# Run container
docker run -p 8080:80 aws-serverless-resume
```

### Configuration

**Set up your profile information:**

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

**Set up your resume data:**

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


## ☁️ AWS Mapping (Conceptual)

| Local Component        | AWS Equivalent                      |
|------------------------|-------------------------------------|
| Nginx                  | CloudFront / Application Load Balancer |
| FastAPI                | Lambda or ECS Fargate               |
| Docker network         | VPC                                 |
| /api/* routing         | CloudFront behaviors                |
| docker-compose.yml     | Infrastructure as Code (Terraform/CDK) |

## 📋 Features

- Static website served via Nginx
- RESTful API with FastAPI
- Reverse proxy configuration
- Docker containerization
- Local development environment with Docker Compose

## 📄 License

© 2026 Rob Rose. All rights reserved.

This project is provided for personal and educational purposes. If reused or forked, please retain this notice and provide attribution.

## 🤝 Contributing

This is a personal project, but feedback and suggestions are welcome. Feel free to open an issue for discussion.

---

**Tech Stack:** Python • FastAPI • Docker • Nginx • AWS
