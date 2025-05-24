.PHONY: up down logs shell test test-local test-docker test-ci ingest worker

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

# Run tests (default method - uses local SQLite for fast development)
test: test-local

# Run tests locally with SQLite (faster for development)
test-local:
	@echo "Running local tests with SQLite database..."
	@bash ./update_tests.sh
	PYTHONPATH=. python3 run_tests.py tests/

# Run individual test modules locally
test-local-worker:
	@echo "Running local worker tests with SQLite database..."
	@bash ./update_tests.sh
	PYTHONPATH=. python3 run_tests.py tests/test_worker.py

test-local-api:
	@echo "Running local API tests with SQLite database..."
	@bash ./update_tests.sh
	PYTHONPATH=. python3 run_tests.py tests/api/

# Run tests in Docker container with PostgreSQL (slower, but more production-like)
test-docker:
	@echo "Running tests in Docker container with PostgreSQL database..."
	docker-compose -f docker-compose.test.yml up -d
	docker-compose -f docker-compose.test.yml exec test pytest -xvs tests/
	
# Run individual test modules in Docker
test-docker-worker:
	docker-compose -f docker-compose.test.yml exec test pytest -xvs tests/test_worker.py

test-docker-api:
	docker-compose -f docker-compose.test.yml exec test pytest -xvs tests/api/

# CI tests run in Docker but with specific configuration for CI environments
test-ci:
	@echo "Running CI tests with PostgreSQL database..."
	PYTHONPATH=. pytest -xvs tests/

# Legacy test commands (kept for backward compatibility)
test-in-container: test-docker

# Run tests from app tests directory (deprecated - will be removed)
test-app:
	@echo "WARNING: The app/tests directory is deprecated and will be removed. Use 'make test' instead."
	docker-compose exec api pip install pytest pytest-mock python-slugify
	docker-compose exec api bash -c "cd /app && PYTHONPATH=/app pytest -xvs /app/tests"

# Legacy individual test targets (kept for backward compatibility)
test-worker: test-local-worker
test-api: test-local-api

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
