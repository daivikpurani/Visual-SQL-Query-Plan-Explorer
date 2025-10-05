.PHONY: up down test fmt lint load-demo clean

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Run tests
test:
	cd backend && python -m pytest
	cd frontend && npm run lint

# Format code
fmt:
	cd backend && ruff format . && black .
	cd frontend && npm run lint -- --fix

# Lint code
lint:
	cd backend && ruff check . && black --check .
	cd frontend && npm run lint

# Load demo data
load-demo:
	docker-compose exec postgres psql -U dev -d plans -f /docker-entrypoint-initdb.d/seed.sql

# Clean up
clean:
	docker-compose down -v
	docker system prune -f
