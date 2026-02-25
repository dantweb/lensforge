.PHONY: build test test-unit test-integration lint format run down smoke-test pre-commit

build:
	docker compose build

test:
	docker compose run --rm test tests/ -v

test-unit:
	docker compose run --rm test tests/unit/ -v

test-integration:
	docker compose run --rm test tests/integration/ -v --timeout=120

lint:
	docker compose run --rm --entrypoint ruff test check lensforge/ custom/ tests/ && \
	docker compose run --rm --entrypoint ruff test format --check lensforge/ custom/ tests/

format:
	docker compose run --rm --entrypoint ruff test check --fix lensforge/ custom/ tests/ && \
	docker compose run --rm --entrypoint ruff test format lensforge/ custom/ tests/

run:
	docker compose up lensforge

down:
	docker compose down

smoke-test:
	docker compose run --rm test tests/smoke_test.sh

pre-commit:
	./bin/pre-commit-check.sh
