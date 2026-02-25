# LensForge Developer Guide

## Architecture

LensForge is a **context-agnostic** pluggable AI vision microservice SDK. The SDK provides the framework; all model implementations live in `/custom/extensions/`.

```
lensforge/          # SDK (framework — do not add context-specific code here)
├── interfaces/     # Protocol contracts (IQualityChecker, INsfwDetector, IDomainClassifier)
├── pipeline/       # Two-stage orchestration (NN1 → NN2)
├── loaders/        # Image loading (base64, URL)
├── routes/         # FastAPI endpoints (/analyze, /batch-analyze)
├── schemas/        # Pydantic request/response models
├── container.py    # DI container with dynamic extension loading
├── config.py       # Settings from custom/.env
└── app.py          # FastAPI factory

custom/             # Customer configuration (context-specific)
├── .env            # Environment variables, model paths, class paths
├── .env.example    # Documented config template
└── extensions/     # Context-specific implementations
    └── dermatology/
        ├── brisque_checker.py    # IQualityChecker
        ├── falconsai_nsfw.py     # INsfwDetector
        └── vit_skin.py           # IDomainClassifier
```

### Pipeline Flow

```
Request (base64/URL)
    │
    ▼
ImageLoader (validate format, resize, convert RGB)
    │
    ▼
AnalysisPipeline.analyze()
    ├── NN1: QualityChecker.check()
    │   └── ✗ → rejected_quality (early return)
    │
    ├── NN1: NsfwDetector.detect()
    │   └── ✗ → rejected_nsfw (early return)
    │
    └── NN2: DomainClassifier.classify()
        └── ✓ → success (predictions + urgency + disclaimer)
```

### Dynamic Extension Loading

The DI container loads model classes at runtime via dotted Python import paths configured in `custom/.env`:

```env
QUALITY_CLASS=custom.extensions.dermatology.brisque_checker.BrisqueChecker
NSFW_CLASS=custom.extensions.dermatology.falconsai_nsfw.FalconsaiNsfwDetector
CLASSIFIER_CLASS=custom.extensions.dermatology.vit_skin.VitSkinClassifier
```

To add a new context (e.g. plant disease), create `custom/extensions/botany/` with classes implementing the SDK interfaces, then update `custom/.env`. Zero SDK code changes required.

## Interfaces

Every extension must implement one of these protocols:

### IQualityChecker

```python
class IQualityChecker(Protocol):
    version: str
    def check(self, image: Image.Image) -> QualityResult: ...
```

Returns `QualityResult(score: float, is_acceptable: bool, reason: str | None)`.

### INsfwDetector

```python
class INsfwDetector(Protocol):
    version: str
    def detect(self, image: Image.Image) -> NsfwResult: ...
```

Returns `NsfwResult(is_safe: bool, nsfw_score: float, reason: str | None)`.

### IDomainClassifier

```python
class IDomainClassifier(Protocol):
    version: str
    def classify(self, image: Image.Image) -> ClassificationResult: ...
```

Returns `ClassificationResult(detected: bool, predictions: list[Prediction], description: str, urgency: str | None)`.

## Development

### Prerequisites

- Docker and Docker Compose

### Commands

All commands run in Docker:

```bash
make build           # Build Docker images
make test            # Run all tests
make test-unit       # Run unit tests only
make test-integration  # Run integration tests (downloads real models)
make lint            # Ruff check + format check
make format          # Auto-fix lint + format
make run             # Start the service (port 8000)
make down            # Stop containers
make pre-commit      # Full pre-commit check (lint + unit tests)
```

### Pre-commit Check

Run before every commit:

```bash
./bin/pre-commit-check.sh
```

This script:
1. Builds the Docker test image
2. Runs `ruff check` on SDK + extensions + tests
3. Runs `ruff format --check` for style verification
4. Runs all unit tests
5. Exits non-zero on any failure

### Project Structure Rules

- **`lensforge/`** — SDK framework only. No context-specific code (no skin labels, no plant names, etc.)
- **`custom/extensions/<context>/`** — All model implementations go here
- **`custom/.env`** — All configuration, API keys, class paths. Gitignored.
- **`custom/.env.example`** — Documented template. Committed.

## Writing a New Extension

### 1. Create the extension folder

```
custom/extensions/botany/
├── __init__.py
├── quality_checker.py
├── nsfw_detector.py
└── plant_classifier.py
```

### 2. Implement the interfaces

```python
# custom/extensions/botany/plant_classifier.py
from lensforge.interfaces.domain_classifier import ClassificationResult, Prediction

class PlantClassifier:
    def __init__(self, model_name: str, device: str = "cpu"):
        self._model_name = model_name
        self._device = device
        self._pipe = None

    @property
    def version(self) -> str:
        return f"plant-{self._model_name.split('/')[-1]}"

    def classify(self, image):
        # Load model lazily, run inference
        ...
        return ClassificationResult(
            detected=True,
            predictions=[Prediction(label="rust", probability=0.85, risk_level="high")],
            description="Top prediction: rust (85.0%)",
            urgency="Treat within 1 week",
        )
```

### 3. Update `custom/.env`

```env
CLASSIFIER_CLASS=custom.extensions.botany.plant_classifier.PlantClassifier
CLASSIFIER_MODEL_NAME=your-org/plant-disease-model
```

### 4. Write tests

```python
# tests/unit/test_plant_classifier.py
from unittest.mock import MagicMock
from custom.extensions.botany.plant_classifier import PlantClassifier

class TestPlantClassifier:
    def test_classifies_image(self):
        classifier = PlantClassifier(_pipeline=mock_pipe)
        result = classifier.classify(Image.new("RGB", (224, 224)))
        assert result.detected is True
```

### 5. Rebuild and test

```bash
make build && make test-unit
```

## API

### POST /analyze

Single image analysis.

**Request:**
```json
{
  "image_base64": "<base64-encoded-image>"
}
```
or
```json
{
  "image_url": "https://example.com/image.jpg"
}
```

**Response (success):**
```json
{
  "status": "success",
  "lesion_detected": true,
  "main_description": "Top prediction: nv (87.0%)",
  "predictions": [
    {"label": "nv", "probability": 0.87, "risk_level": "low"},
    {"label": "mel", "probability": 0.08, "risk_level": "high"}
  ],
  "urgency": "Monitor, no immediate urgency",
  "disclaimer": "This is NOT a medical diagnosis. See a qualified specialist. AI output only.",
  "inference_time_ms": 342,
  "model_versions": {
    "nn1_quality": "brisque-laplacian-1.0",
    "nn1_safety": "falconsai-nsfw-vit-1.0",
    "nn2": "vit-skin-Skin_Cancer-Image_Classification"
  }
}
```

**Response (rejected):**
```json
{
  "status": "rejected_quality",
  "reason": "Image too blurry (sharpness=12, min=100)",
  "disclaimer": "This is NOT a medical diagnosis. See a qualified specialist. AI output only.",
  "inference_time_ms": 5,
  "model_versions": { ... }
}
```

### POST /batch-analyze

Batch analysis (max 50 images).

**Request:**
```json
{
  "images": [
    {"image_base64": "..."},
    {"image_url": "https://..."}
  ]
}
```

**Response:**
```json
{
  "results": [
    { "status": "success", ... },
    { "status": "rejected_nsfw", ... }
  ]
}
```

### GET /health

```json
{"status": "ok"}
```

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yaml`) runs on push/PR to `main`:

| Job | What it does |
|-----|-------------|
| **lint** | `ruff check` + `ruff format --check` on SDK, extensions, tests |
| **test** | Unit tests with Python 3.12 (native runner) |
| **docker** | Docker build + unit tests inside container |

The `test` and `docker` jobs run in parallel after `lint` passes.

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DEVICE` | `cpu` | `cpu` or `cuda` |
| `QUALITY_CLASS` | `custom.extensions.dermatology.brisque_checker.BrisqueChecker` | Quality checker class path |
| `QUALITY_BLUR_THRESHOLD` | `100` | Laplacian variance threshold |
| `NSFW_CLASS` | `custom.extensions.dermatology.falconsai_nsfw.FalconsaiNsfwDetector` | NSFW detector class path |
| `NSFW_THRESHOLD` | `0.7` | NSFW score threshold (0-1) |
| `CLASSIFIER_CLASS` | `custom.extensions.dermatology.vit_skin.VitSkinClassifier` | Domain classifier class path |
| `CLASSIFIER_MODEL_NAME` | `Anwarkh1/Skin_Cancer-Image_Classification` | HuggingFace model ID |
| `MAX_IMAGE_SIZE` | `1024` | Max image dimension (px) |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
| `HF_TOKEN` | — | HuggingFace token (for gated models) |

## Testing Strategy

- **Unit tests** (`tests/unit/`) — All models mocked. Fast, no network. Run on every commit.
- **Integration tests** (`tests/integration/`) — Real models on CPU. Skipped when `CI_FAST=true`. Run manually or in nightly CI.
- **Smoke test** (`tests/smoke_test.sh`) — Curl-based health + analyze check against running container.

Mock fixtures are in `tests/conftest.py`. The `client` fixture creates a full FastAPI test client with mocked pipeline.
