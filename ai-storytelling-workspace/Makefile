.PHONY: setup dev test docker db-migrate db-rollback security help

help:
	@echo "Available commands:"
	@echo "  setup       - Initial setup of the project"
	@echo "  dev         - Run development servers"
	@echo "  test        - Run tests"
	@echo "  docker      - Build and run docker containers"
	@echo "  db-migrate  - Run database migrations"
	@echo "  db-rollback - Rollback last database migration"
	@echo "  security    - Run security checks"

setup:
	@bash scripts/setup.sh

dev:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 & \
	cd web && npm start

test:
	pytest tests/

docker:
	docker-compose -f docker/docker-compose.yml up -d --build

db-migrate:
	alembic upgrade head

db-rollback:
	alembic downgrade -1

security:
	bandit -r src/ api/ workers/
