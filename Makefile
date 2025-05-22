.PHONY: up down logs shell test ingest worker

# Docker compose commands
up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

# Shell into the API container
shell:
	docker-compose exec api bash

# Run tests
test:
	docker-compose exec api pip install pytest pytest-mock python-slugify
	docker-compose exec api bash -c "cd / && PYTHONPATH=/app pytest -xvs /tests"

# Run tests in test environment (preferred way)
test-in-container:
	docker-compose -f docker-compose.test.yml exec test pytest -xvs tests/

# Run tests from app tests directory (deprecated - will be removed)
test-app:
	@echo "WARNING: The app/tests directory is deprecated and will be removed"
	docker-compose exec api pip install pytest pytest-mock python-slugify
	docker-compose exec api bash -c "cd /app && PYTHONPATH=/app pytest -xvs /app/tests"

# Run specific tests
test-worker:
	docker-compose exec api bash -c "cd / && PYTHONPATH=/app pytest -xvs /tests/test_worker.py"

test-api:
	docker-compose exec api bash -c "cd / && PYTHONPATH=/app pytest -xvs /tests/api"

# Ingest a URL - usage: make ingest URL=https://www.youtube.com/watch?v=example
ingest:
	@if [ -z "$(URL)" ]; then \
		echo "Error: URL parameter is required. Usage: make ingest URL=https://example.com"; \
		exit 1; \
	fi
	python ingest_test.py "$(URL)"

# Run the worker once or continuously
worker:
	python worker.py

worker-once:
	python worker.py --once
