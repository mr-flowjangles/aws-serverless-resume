.PHONY: up down build logs help

up:
	@echo "Starting services..."
	@docker compose up --build -d
	@echo ""
	@echo "All services are running"
	@echo "Site: http://localhost:8080"
	@echo "API Docs: http://localhost:8080/api/docs"
	@echo "Health Check: http://localhost:8080/api/health"
	@echo ""
	@echo "View logs: make logs"
	@echo "Stop services: make down"

down:
	@echo "Stopping services..."
	@docker compose down
	@echo "Services stopped"

build:
	@echo "Building images..."
	@docker compose build --no-cache
	@echo "Build complete"

logs:
	@docker compose logs -f

help:
	@echo "Available commands:"
	@echo "  make up     - Start all services"
	@echo "  make down   - Stop all services"
	@echo "  make build  - Rebuild all images"
	@echo "  make logs   - View service logs"
	@echo "  make help   - Show this help message"