"""Domain-specific image classification protocol."""

from dataclasses import dataclass, field
from typing import Protocol

from PIL import Image


@dataclass
class Prediction:
    """Single classification prediction."""

    label: str
    probability: float
    risk_level: str | None = None  # "low", "moderate", "high"


@dataclass
class ClassificationResult:
    """Result of domain-specific classification."""

    detected: bool
    predictions: list[Prediction] = field(default_factory=list)
    description: str = ""
    urgency: str | None = None


class IDomainClassifier(Protocol):
    """Protocol for domain-specific classifiers (skin, plant, pet, art, etc.)."""

    @property
    def version(self) -> str: ...

    def classify(self, image: Image.Image) -> ClassificationResult: ...
