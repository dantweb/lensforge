"""Interface dataclass tests."""

from lensforge.interfaces.domain_classifier import ClassificationResult, Prediction
from lensforge.interfaces.nsfw_detector import NsfwResult
from lensforge.interfaces.quality_checker import QualityResult


class TestQualityResult:
    def test_acceptable(self):
        r = QualityResult(score=0.8, is_acceptable=True)
        assert r.is_acceptable is True
        assert r.reason is None

    def test_rejected(self):
        r = QualityResult(score=0.1, is_acceptable=False, reason="Blurry")
        assert r.is_acceptable is False
        assert r.reason == "Blurry"


class TestNsfwResult:
    def test_safe(self):
        r = NsfwResult(is_safe=True, nsfw_score=0.05)
        assert r.is_safe is True
        assert r.reason is None

    def test_unsafe(self):
        r = NsfwResult(is_safe=False, nsfw_score=0.95, reason="Explicit content")
        assert r.is_safe is False
        assert r.nsfw_score == 0.95


class TestClassificationResult:
    def test_with_predictions(self):
        r = ClassificationResult(
            detected=True,
            predictions=[
                Prediction(label="nv", probability=0.87, risk_level="low"),
                Prediction(label="mel", probability=0.08, risk_level="high"),
            ],
            description="Mole detected",
            urgency="No urgency",
        )
        assert len(r.predictions) == 1 + 1
        assert r.predictions[0].label == "nv"
        assert r.predictions[1].risk_level == "high"

    def test_empty_predictions(self):
        r = ClassificationResult(detected=False)
        assert r.predictions == []
        assert r.description == ""
        assert r.urgency is None
