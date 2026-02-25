"""NSFW / safety detection protocol."""

from dataclasses import dataclass
from typing import Protocol

from PIL import Image


@dataclass
class NsfwResult:
    """Result of an NSFW safety check."""

    is_safe: bool
    nsfw_score: float  # 0.0-1.0 (1.0 = definitely NSFW)
    reason: str | None = None


class INsfwDetector(Protocol):
    """Protocol for NSFW detection implementations."""

    @property
    def version(self) -> str: ...

    def detect(self, image: Image.Image) -> NsfwResult: ...
