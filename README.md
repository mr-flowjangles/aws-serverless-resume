# aws-serverless-resume

A serverless resume application built on AWS, demonstrating API-driven content, managed cloud services, and infrastructure as code.

## Docker Commands

### Initial Setup

- _Create Image_: `docker build -t aws-serverless-resume -f docker/Dockerfile .`

### Run Container

- _Run Container_: `docker compose up --build`

## Architecture

Browser
  ↓
Nginx (web)
  - Serves static files
  - Proxies `/api/*` requests
  ↓
FastAPI (api)
  - Private service
  - No public port exposure

## Project Structure

.
├── app/                # Static website (index.html)
├── api/                # FastAPI service
│   ├── main.py
│   └── Dockerfile
├── nginx/              # Nginx reverse proxy config
│   └── default.conf
├── docker-compose.yml  # Local infrastructure
├── Makefile            # Common commands
└── README.md

## Running Locally

Prerequisites:
- Docker
- Docker Compose

Start everything:
`make up`
