"""LensForge protocol interfaces."""

from lensforge.interfaces.domain_classifier import (
    ClassificationResult,
    IDomainClassifier,
    Prediction,
)
from lensforge.interfaces.nsfw_detector import INsfwDetector, NsfwResult
from lensforge.interfaces.quality_checker import IQualityChecker, QualityResult

__all__ = [
    "IQualityChecker",
    "QualityResult",
    "INsfwDetector",
    "NsfwResult",
    "IDomainClassifier",
    "ClassificationResult",
    "Prediction",
]
