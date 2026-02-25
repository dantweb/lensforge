"""Falconsai ViT NSFW detector."""

from typing import Any

from PIL import Image

from lensforge.interfaces.nsfw_detector import NsfwResult


def _load_pipeline() -> Any:
    """Lazy-load transformers pipeline."""
    from transformers import pipeline

    return pipeline("image-classification", model="Falconsai/nsfw_image_detection")


class FalconsaiNsfwDetector:
    """NSFW detector using Falconsai/nsfw_image_detection (Apache 2.0)."""

    def __init__(self, threshold: float = 0.7, _pipeline: Any = None) -> None:
        self._threshold = threshold
        self._pipe = _pipeline

    def _get_pipe(self) -> Any:
        if self._pipe is None:
            self._pipe = _load_pipeline()
        return self._pipe

    @property
    def version(self) -> str:
        return "falconsai-nsfw-vit-1.0"

    def detect(self, image: Image.Image) -> NsfwResult:
        results = self._get_pipe()(image)
        scores = {r["label"]: r["score"] for r in results}
        nsfw_score = scores.get("nsfw", 0.0)
        is_safe = nsfw_score < self._threshold

        return NsfwResult(
            is_safe=is_safe,
            nsfw_score=round(nsfw_score, 4),
            reason=f"NSFW score {nsfw_score:.2f}" if not is_safe else None,
        )
