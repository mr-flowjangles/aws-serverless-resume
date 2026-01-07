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

### Running Locally

1. **Start all services:**
   ```bash
   make up
   ```

2. **Access the application:**
   - Frontend: http://localhost:8080
   - API Documentation (Swagger): http://localhost:8080/api/docs

### Available Commands

```bash
make up          # Start all services
make down        # Stop all services
make build       # Build Docker images
make logs        # View container logs
```

## 🛠️ Development

### Initial Setup

Build the Docker image:
```bash
docker build -t aws-serverless-resume -f docker/Dockerfile .
```

Run with Docker Compose:
```bash
docker compose up --build
```

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
