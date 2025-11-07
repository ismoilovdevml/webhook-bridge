.PHONY: help build up down logs restart test clean dev-backend dev-frontend install

help:
	@echo "Webhook Bridge - Available commands:"
	@echo ""
	@echo "  Production:"
	@echo "    make build     - Build Docker images"
	@echo "    make up        - Start all services"
	@echo "    make down      - Stop all services"
	@echo "    make logs      - View logs"
	@echo "    make restart   - Restart services"
	@echo "    make clean     - Clean up containers and volumes"
	@echo ""
	@echo "  Development:"
	@echo "    make install       - Install dependencies"
	@echo "    make dev-backend   - Run backend in dev mode"
	@echo "    make dev-frontend  - Run frontend in dev mode"
	@echo ""
	@echo "  Testing:"
	@echo "    make test      - Test webhook service"
	@echo "    make health    - Check service health"

# Production commands
build:
	docker-compose build --no-cache

up:
	docker-compose up -d
	@echo ""
	@echo "Services started successfully!"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "Run 'make logs' to view logs"
	@echo "Run 'make health' to check status"

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

restart:
	docker-compose restart

restart-backend:
	docker-compose restart backend

restart-frontend:
	docker-compose restart frontend

clean:
	docker-compose down -v
	rm -rf data/*.db
	@echo "Cleaned up containers, volumes, and database"

# Development commands
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Dependencies installed!"

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

# Testing commands
test:
	@echo "Testing webhook service..."
	@curl -s http://localhost:8000/api/webhook/test | python -m json.tool

health:
	@echo "Checking service health..."
	@echo ""
	@echo "Backend:"
	@curl -s http://localhost:8000/health | python -m json.tool || echo "Backend not responding"
	@echo ""
	@echo "Frontend:"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3000 || echo "Frontend not responding"

# Database commands
db-backup:
	@mkdir -p backups
	@cp data/webhook_bridge.db backups/webhook_bridge_$(shell date +%Y%m%d_%H%M%S).db
	@echo "Database backed up to backups/"

db-reset:
	docker-compose down
	rm -f data/webhook_bridge.db
	docker-compose up -d
	@echo "Database reset complete"
