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
	docker-compose exec api pytest -v

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
