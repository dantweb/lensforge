"""ImageLoader tests."""

import base64
from io import BytesIO

import pytest
from PIL import Image

from lensforge.loaders.image_loader import ImageLoader


class TestLoadBase64:
    def test_loads_jpeg(self):
        img = Image.new("RGB", (100, 100), color="red")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        loader = ImageLoader(max_size=1024)
        result = loader.load_base64(b64)
        assert result.size == (100, 100)
        assert result.mode == "RGB"

    def test_loads_png(self):
        img = Image.new("RGB", (50, 50), color="blue")
        buf = BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        loader = ImageLoader(max_size=1024)
        result = loader.load_base64(b64)
        assert result.size == (50, 50)

    def test_rejects_invalid_data(self):
        loader = ImageLoader(max_size=1024)
        with pytest.raises(ValueError, match="Unsupported image format"):
            loader.load_base64(base64.b64encode(b"not an image").decode())

    def test_rejects_bad_base64(self):
        loader = ImageLoader(max_size=1024)
        with pytest.raises(ValueError, match="Invalid base64"):
            loader.load_base64("!!!not-base64!!!")


class TestResize:
    def test_resizes_large_image(self):
        img = Image.new("RGB", (2048, 1536), color="green")
        buf = BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        loader = ImageLoader(max_size=1024)
        result = loader.load_base64(b64)
        assert max(result.size) <= 1024

    def test_preserves_aspect_ratio(self):
        img = Image.new("RGB", (2000, 1000), color="green")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        loader = ImageLoader(max_size=1024)
        result = loader.load_base64(b64)
        ratio = result.size[0] / result.size[1]
        assert abs(ratio - 2.0) < 0.02

    def test_no_resize_if_small(self):
        img = Image.new("RGB", (100, 80), color="red")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        loader = ImageLoader(max_size=1024)
        result = loader.load_base64(b64)
        assert result.size == (100, 80)


class TestColorMode:
    def test_converts_grayscale_to_rgb(self):
        img = Image.new("L", (100, 100))
        buf = BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        loader = ImageLoader(max_size=1024)
        result = loader.load_base64(b64)
        assert result.mode == "RGB"

    def test_converts_rgba_to_rgb(self):
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        buf = BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        loader = ImageLoader(max_size=1024)
        result = loader.load_base64(b64)
        assert result.mode == "RGB"
