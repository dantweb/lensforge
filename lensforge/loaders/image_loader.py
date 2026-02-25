"""Image loading, validation, and preprocessing."""

import base64
from io import BytesIO

import requests
from PIL import Image

SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}


class ImageLoader:
    """Loads images from base64 or URL, validates format, resizes."""

    def __init__(self, max_size: int = 1024) -> None:
        self._max_size = max_size

    def load_base64(self, data: str) -> Image.Image:
        """Decode base64 string to PIL Image."""
        try:
            raw = base64.b64decode(data)
        except Exception as exc:
            raise ValueError(f"Invalid base64 data: {exc}") from exc
        return self._process(BytesIO(raw))

    def load_url(self, url: str) -> Image.Image:
        """Fetch image from URL."""
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return self._process(BytesIO(resp.content))

    def _process(self, buf: BytesIO) -> Image.Image:
        """Validate format, convert to RGB, resize if needed."""
        try:
            img = Image.open(buf)
        except Exception as exc:
            raise ValueError(f"Unsupported image format: {exc}") from exc

        if img.format and img.format.upper() not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported image format: {img.format}")

        if img.mode != "RGB":
            img = img.convert("RGB")

        return self._resize(img)

    def _resize(self, img: Image.Image) -> Image.Image:
        """Resize to max dimension preserving aspect ratio."""
        w, h = img.size
        if max(w, h) <= self._max_size:
            return img
        scale = self._max_size / max(w, h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return img.resize((new_w, new_h), Image.LANCZOS)
