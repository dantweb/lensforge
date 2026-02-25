"""FalconsaiNsfwDetector tests (pipeline mocked)."""

from unittest.mock import MagicMock

from PIL import Image

from custom.extensions.dermatology.falconsai_nsfw import FalconsaiNsfwDetector


class TestFalconsaiNsfw:
    def test_safe_image(self):
        mock_pipe = MagicMock()
        mock_pipe.return_value = [
            {"label": "normal", "score": 0.97},
            {"label": "nsfw", "score": 0.03},
        ]

        detector = FalconsaiNsfwDetector(threshold=0.7, _pipeline=mock_pipe)
        result = detector.detect(Image.new("RGB", (224, 224)))

        assert result.is_safe is True
        assert result.nsfw_score < 0.7
        assert result.reason is None

    def test_nsfw_image(self):
        mock_pipe = MagicMock()
        mock_pipe.return_value = [
            {"label": "nsfw", "score": 0.92},
            {"label": "normal", "score": 0.08},
        ]

        detector = FalconsaiNsfwDetector(threshold=0.7, _pipeline=mock_pipe)
        result = detector.detect(Image.new("RGB", (224, 224)))

        assert result.is_safe is False
        assert result.nsfw_score >= 0.7
        assert result.reason is not None
        assert "0.92" in result.reason

    def test_threshold_configurable(self):
        mock_pipe = MagicMock()
        mock_pipe.return_value = [
            {"label": "nsfw", "score": 0.50},
            {"label": "normal", "score": 0.50},
        ]

        # Low threshold rejects
        detector_strict = FalconsaiNsfwDetector(threshold=0.3, _pipeline=mock_pipe)
        assert detector_strict.detect(Image.new("RGB", (224, 224))).is_safe is False

        # High threshold accepts
        detector_lax = FalconsaiNsfwDetector(threshold=0.8, _pipeline=mock_pipe)
        assert detector_lax.detect(Image.new("RGB", (224, 224))).is_safe is True

    def test_version(self):
        detector = FalconsaiNsfwDetector(threshold=0.7, _pipeline=MagicMock())
        assert "falconsai" in detector.version
