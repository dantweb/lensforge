"""Shared test fixtures for LensForge."""

from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image

from lensforge.interfaces.domain_classifier import ClassificationResult, Prediction
from lensforge.interfaces.nsfw_detector import NsfwResult
from lensforge.interfaces.quality_checker import QualityResult


@pytest.fixture
def sample_image() -> Image.Image:
    return Image.new("RGB", (224, 224), color=(180, 130, 100))


@pytest.fixture
def sharp_image() -> Image.Image:
    """Image with structure so Laplacian detects edges."""
    from PIL import ImageDraw

    img = Image.new("RGB", (224, 224), color=(180, 130, 100))
    draw = ImageDraw.Draw(img)
    for i in range(0, 224, 8):
        draw.line([(i, 0), (i, 224)], fill="black", width=2)
        draw.line([(0, i), (224, i)], fill="black", width=1)
    return img


# --- Mock fixtures for pipeline tests ---


@pytest.fixture
def mock_quality_ok() -> MagicMock:
    m = MagicMock()
    m.check.return_value = QualityResult(score=0.9, is_acceptable=True)
    m.version = "mock-quality-1.0"
    return m


@pytest.fixture
def mock_quality_bad() -> MagicMock:
    m = MagicMock()
    m.check.return_value = QualityResult(score=0.1, is_acceptable=False, reason="Too blurry")
    m.version = "mock-quality-1.0"
    return m


@pytest.fixture
def mock_nsfw_safe() -> MagicMock:
    m = MagicMock()
    m.detect.return_value = NsfwResult(is_safe=True, nsfw_score=0.05)
    m.version = "mock-nsfw-1.0"
    return m


@pytest.fixture
def mock_nsfw_unsafe() -> MagicMock:
    m = MagicMock()
    m.detect.return_value = NsfwResult(is_safe=False, nsfw_score=0.92, reason="NSFW content")
    m.version = "mock-nsfw-1.0"
    return m


@pytest.fixture
def mock_classifier() -> MagicMock:
    m = MagicMock()
    m.classify.return_value = ClassificationResult(
        detected=True,
        predictions=[
            Prediction(label="nv", probability=0.87, risk_level="low"),
            Prediction(label="mel", probability=0.08, risk_level="high"),
        ],
        description="Top prediction: nv (87.0%)",
        urgency="Monitor, no immediate urgency",
    )
    m.version = "mock-skin-1.0"
    return m


@pytest.fixture
def mock_classifier_melanoma() -> MagicMock:
    m = MagicMock()
    m.classify.return_value = ClassificationResult(
        detected=True,
        predictions=[
            Prediction(label="mel", probability=0.78, risk_level="high"),
            Prediction(label="nv", probability=0.15, risk_level="low"),
        ],
        description="Top prediction: mel (78.0%)",
        urgency="Consult dermatologist within days",
    )
    m.version = "mock-skin-1.0"
    return m


# --- App client fixture ---


@pytest.fixture
async def client(
    mock_quality_ok: MagicMock,
    mock_nsfw_safe: MagicMock,
    mock_classifier: MagicMock,
) -> AsyncClient:
    """Create test client with mocked pipeline via app.state.container."""
    from fastapi import FastAPI

    from lensforge.loaders.image_loader import ImageLoader
    from lensforge.pipeline.analysis_pipeline import AnalysisPipeline
    from lensforge.routes.analyze import router as analyze_router

    app = FastAPI()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(analyze_router)

    pipeline = AnalysisPipeline(
        quality=mock_quality_ok,
        safety=mock_nsfw_safe,
        classifier=mock_classifier,
    )
    loader = ImageLoader(max_size=1024)

    # Mock container that returns our mocked pipeline and loader
    mock_container = MagicMock()
    mock_container.analysis_pipeline.return_value = pipeline
    mock_container.image_loader.return_value = loader

    app.state.container = mock_container

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
