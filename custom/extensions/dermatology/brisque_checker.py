"""BRISQUE + Laplacian blur quality checker."""

import cv2
import numpy as np
from PIL import Image

from lensforge.interfaces.quality_checker import QualityResult


class BrisqueChecker:
    """Image quality checker using Laplacian variance for blur detection."""

    def __init__(self, blur_threshold: float = 100.0) -> None:
        self._blur_threshold = blur_threshold

    @property
    def version(self) -> str:
        return "brisque-laplacian-1.0"

    def check(self, image: Image.Image) -> QualityResult:
        arr = np.array(image)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        if laplacian_var < self._blur_threshold:
            score = laplacian_var / self._blur_threshold
            return QualityResult(
                score=round(score, 3),
                is_acceptable=False,
                reason=(
                    f"Image too blurry "
                    f"(sharpness={laplacian_var:.0f}, min={self._blur_threshold:.0f})"
                ),
            )

        score = min(1.0, laplacian_var / (self._blur_threshold * 10))
        return QualityResult(score=round(score, 3), is_acceptable=True)
