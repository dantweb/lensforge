"""Schema validation tests."""

import pytest

from lensforge.schemas.request import AnalyzeRequest, BatchAnalyzeRequest
from lensforge.schemas.response import AnalyzeResponse, PredictionSchema


class TestAnalyzeRequest:
    def test_requires_at_least_one_source(self):
        with pytest.raises(ValueError, match="image_base64 or image_url"):
            AnalyzeRequest()

    def test_accepts_base64(self):
        req = AnalyzeRequest(image_base64="abc123")
        assert req.image_base64 == "abc123"
        assert req.image_url is None

    def test_accepts_url(self):
        req = AnalyzeRequest(image_url="https://example.com/img.jpg")
        assert req.image_url is not None
        assert req.image_base64 is None

    def test_accepts_both(self):
        req = AnalyzeRequest(image_base64="abc", image_url="https://example.com/img.jpg")
        assert req.image_base64 == "abc"
        assert req.image_url is not None


class TestBatchAnalyzeRequest:
    def test_max_50_images(self):
        with pytest.raises(ValueError):
            BatchAnalyzeRequest(images=[AnalyzeRequest(image_base64="x")] * 51)

    def test_accepts_list(self):
        req = BatchAnalyzeRequest(
            images=[
                AnalyzeRequest(image_base64="a"),
                AnalyzeRequest(image_url="https://example.com/b.jpg"),
            ]
        )
        assert len(req.images) == 2


class TestAnalyzeResponse:
    def test_success_response(self):
        resp = AnalyzeResponse(
            status="success",
            lesion_detected=True,
            predictions=[PredictionSchema(label="nv", probability=0.87, risk_level="low")],
            disclaimer="AI only",
        )
        assert resp.status == "success"
        assert len(resp.predictions) == 1
        assert resp.predictions[0].label == "nv"

    def test_rejection_response(self):
        resp = AnalyzeResponse(
            status="rejected_nsfw",
            reason="NSFW score 0.92",
            disclaimer="AI only",
        )
        assert resp.lesion_detected is None
        assert resp.predictions == []

    def test_defaults(self):
        resp = AnalyzeResponse(status="error", disclaimer="test")
        assert resp.predictions == []
        assert resp.inference_time_ms == 0
        assert resp.model_versions == {}
