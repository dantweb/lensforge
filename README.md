# LensForge

Pluggable Python AI vision microservice SDK. Context-agnostic framework — all model implementations live in `/custom/extensions/`.

## Quick Start

```bash
cp custom/.env.example custom/.env
make build
make run
```

Service starts at `http://localhost:8000`.

## Usage

```bash
# Health check
curl http://localhost:8000/health

# Analyze image
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "<base64-encoded-image>"}'
```

## Project Structure

```
lensforge/              # SDK framework (context-agnostic)
├── interfaces/         # Protocols: IQualityChecker, INsfwDetector, IDomainClassifier
├── pipeline/           # Two-stage orchestration: NN1 (safety) → NN2 (classification)
├── loaders/            # Image loading (base64, URL)
├── routes/             # POST /analyze, POST /batch-analyze, GET /health
├── schemas/            # Pydantic request/response models
├── container.py        # DI container with dynamic extension loading
└── config.py           # Settings from custom/.env

custom/                 # Customer configuration
├── .env                # Config, API keys, extension class paths
└── extensions/         # Context-specific model implementations
    └── dermatology/    # Example: skin lesion screening
```

## How It Works

```
Image → ImageLoader → NN1: Quality → NN1: NSFW → NN2: Classifier → Response
                         ✗ reject      ✗ reject      ✓ predictions
```

Extensions are loaded dynamically via dotted class paths in `custom/.env`:

```env
QUALITY_CLASS=custom.extensions.dermatology.brisque_checker.BrisqueChecker
NSFW_CLASS=custom.extensions.dermatology.falconsai_nsfw.FalconsaiNsfwDetector
CLASSIFIER_CLASS=custom.extensions.dermatology.vit_skin.VitSkinClassifier
```

To add a new context (plant disease, pet health, art style), create `custom/extensions/<context>/` with classes implementing the SDK interfaces and update `custom/.env`. No SDK changes needed.

## Development

```bash
make build          # Build Docker images
make test-unit      # Run unit tests
make lint           # Ruff check + format check
make format         # Auto-fix lint + format
make pre-commit     # Full pre-commit check (lint + tests)
make run            # Start service
make down           # Stop containers
```

## Documentation

- [Developer Guide](docs/developer-guide.md) — architecture, interfaces, extension guide, API reference, configuration

## License

CC0 1.0 Universal (Public Domain)
