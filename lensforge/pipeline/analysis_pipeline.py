"""Two-stage analysis pipeline: NN1 (safety) → NN2 (domain classification)."""

import time

from PIL import Image

from lensforge.interfaces.domain_classifier import IDomainClassifier
from lensforge.interfaces.nsfw_detector import INsfwDetector
from lensforge.interfaces.quality_checker import IQualityChecker
from lensforge.schemas.response import AnalyzeResponse, PredictionSchema

DISCLAIMER = "This is NOT a medical diagnosis. See a qualified specialist. AI output only."


class AnalysisPipeline:
    """Orchestrates NN1 safety filter → NN2 domain classification."""

    def __init__(
        self,
        quality: IQualityChecker,
        safety: INsfwDetector,
        classifier: IDomainClassifier,
    ) -> None:
        self._quality = quality
        self._safety = safety
        self._classifier = classifier

    def analyze(self, image: Image.Image) -> AnalyzeResponse:
        """Run full pipeline: quality → safety → classify."""
        start = time.monotonic()
        versions = {
            "nn1_quality": self._quality.version,
            "nn1_safety": self._safety.version,
            "nn2": self._classifier.version,
        }

        # NN1: Quality check
        quality_result = self._quality.check(image)
        if not quality_result.is_acceptable:
            return AnalyzeResponse(
                status="rejected_quality",
                reason=quality_result.reason,
                inference_time_ms=self._elapsed(start),
                disclaimer=DISCLAIMER,
                model_versions=versions,
            )

        # NN1: NSFW safety check
        nsfw_result = self._safety.detect(image)
        if not nsfw_result.is_safe:
            return AnalyzeResponse(
                status="rejected_nsfw",
                reason=nsfw_result.reason,
                inference_time_ms=self._elapsed(start),
                disclaimer=DISCLAIMER,
                model_versions=versions,
            )

        # NN2: Domain classification
        classification = self._classifier.classify(image)

        predictions = [
            PredictionSchema(
                label=p.label,
                probability=p.probability,
                risk_level=p.risk_level,
            )
            for p in classification.predictions
        ]

        return AnalyzeResponse(
            status="success",
            lesion_detected=classification.detected,
            main_description=classification.description,
            predictions=predictions,
            urgency=classification.urgency,
            inference_time_ms=self._elapsed(start),
            disclaimer=DISCLAIMER,
            model_versions=versions,
        )

    @staticmethod
    def _elapsed(start: float) -> int:
        return int((time.monotonic() - start) * 1000)
