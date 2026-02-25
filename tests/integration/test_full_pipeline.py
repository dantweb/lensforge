"""Integration test with real CPU models. Slow — skipped in fast CI."""

import os

import pytest
from PIL import Image, ImageDraw

skip_in_ci = pytest.mark.skipif(
    os.getenv("CI_FAST") == "true",
    reason="Skips model download in fast CI",
)


@skip_in_ci
def test_full_dermatology_pipeline():
    """Loads real models on CPU. ~10-15s first run (model download)."""
    from custom.extensions.dermatology.brisque_checker import BrisqueChecker
    from custom.extensions.dermatology.falconsai_nsfw import FalconsaiNsfwDetector
    from custom.extensions.dermatology.vit_skin import VitSkinClassifier
    from lensforge.pipeline.analysis_pipeline import AnalysisPipeline

    pipeline = AnalysisPipeline(
        quality=BrisqueChecker(blur_threshold=50.0),
        safety=FalconsaiNsfwDetector(threshold=0.7),
        classifier=VitSkinClassifier(device="cpu"),
    )

    img = Image.new("RGB", (224, 224), color=(180, 130, 100))
    draw = ImageDraw.Draw(img)
    for i in range(0, 224, 8):
        draw.line([(i, 0), (i, 224)], fill=(150, 100, 80), width=2)
        draw.line([(0, i), (224, i)], fill=(120, 90, 70), width=1)

    result = pipeline.analyze(img)

    assert result.status in ("success", "rejected_quality")
    assert result.disclaimer != ""
    assert result.inference_time_ms > 0
    assert "nn1_quality" in result.model_versions

    if result.status == "success":
        assert len(result.predictions) > 0
