#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

echo "=== LensForge pre-commit check ==="
echo "Project dir: $PROJECT_DIR"
echo ""

# Build test image
echo "--- Building Docker image ---"
docker compose build test
echo ""

# Lint: ruff check + format check (SDK + extensions + tests)
echo "--- Lint: ruff check ---"
docker compose run --rm --no-deps --entrypoint ruff test check lensforge/ custom/ tests/
echo ""

echo "--- Lint: ruff format --check ---"
docker compose run --rm --no-deps --entrypoint ruff test format --check lensforge/ custom/ tests/
echo ""

# Unit tests
echo "--- Unit tests ---"
docker compose run --rm --no-deps test tests/unit/ -v
echo ""

echo "=== All checks passed ==="
