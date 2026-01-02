.PHONY: help up down build logs ps clean

help:
	@echo ""
	@echo "Available commands:"
	@echo "  make up      - Build and start all services"
	@echo "  make down    - Stop all services"
	@echo "  make build   - Build images only"
	@echo "  make logs    - Follow container logs"
	@echo "  make ps      - Show running containers"
	@echo "  make clean   - Remove containers, networks, volumes"
	@echo ""

up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

ps:
	docker compose ps

clean:
	docker compose down --volumes --remove-orphans
