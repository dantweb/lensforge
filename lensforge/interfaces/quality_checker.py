"""Image quality assessment protocol."""

from dataclasses import dataclass
from typing import Protocol

from PIL import Image


@dataclass
class QualityResult:
    """Result of an image quality check."""

    score: float  # 0.0-1.0 normalized (1.0 = best)
    is_acceptable: bool
    reason: str | None = None


class IQualityChecker(Protocol):
    """Protocol for image quality assessment implementations."""

    @property
    def version(self) -> str: ...

    def check(self, image: Image.Image) -> QualityResult: ...
