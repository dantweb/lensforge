"""Analyze endpoint tests (models mocked via conftest client fixture)."""

import base64
from io import BytesIO

import pytest
from PIL import Image


def _make_b64_image(w: int = 224, h: int = 224, color: str = "red") -> str:
    img = Image.new("RGB", (w, h), color=color)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()


class TestAnalyzeEndpoint:
    @pytest.mark.asyncio
    async def test_analyze_base64(self, client):
        b64 = _make_b64_image()
        resp = await client.post("/analyze", json={"image_base64": b64})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "disclaimer" in data

    @pytest.mark.asyncio
    async def test_analyze_no_image(self, client):
        resp = await client.post("/analyze", json={})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_analyze_invalid_base64(self, client):
        resp = await client.post("/analyze", json={"image_base64": "!!!invalid!!!"})
        assert resp.status_code == 400


class TestBatchEndpoint:
    @pytest.mark.asyncio
    async def test_batch_analyze(self, client):
        b64 = _make_b64_image()
        resp = await client.post(
            "/batch-analyze",
            json={"images": [{"image_base64": b64}, {"image_base64": b64}]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["results"]) == 2
        assert all(r["status"] == "success" for r in data["results"])

    @pytest.mark.asyncio
    async def test_batch_max_50(self, client):
        resp = await client.post(
            "/batch-analyze",
            json={"images": [{"image_base64": "x"}] * 51},
        )
        assert resp.status_code == 422
