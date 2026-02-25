"""VitSkinClassifier tests (pipeline mocked)."""

from unittest.mock import MagicMock

from PIL import Image

from custom.extensions.dermatology.vit_skin import VitSkinClassifier


class TestVitSkin:
    def test_classifies_image(self):
        mock_pipe = MagicMock()
        mock_pipe.return_value = [
            {"label": "nv", "score": 0.85},
            {"label": "mel", "score": 0.10},
            {"label": "bkl", "score": 0.03},
        ]

        classifier = VitSkinClassifier(_pipeline=mock_pipe)
        result = classifier.classify(Image.new("RGB", (224, 224)))

        assert result.detected is True
        assert result.predictions[0].label == "nv"
        assert result.predictions[0].risk_level == "low"
        assert len(result.predictions) == 3

    def test_melanoma_high_risk(self):
        mock_pipe = MagicMock()
        mock_pipe.return_value = [
            {"label": "mel", "score": 0.78},
            {"label": "nv", "score": 0.15},
        ]

        classifier = VitSkinClassifier(_pipeline=mock_pipe)
        result = classifier.classify(Image.new("RGB", (224, 224)))

        assert result.predictions[0].risk_level == "high"
        assert "days" in result.urgency.lower()

    def test_bcc_high_risk(self):
        mock_pipe = MagicMock()
        mock_pipe.return_value = [{"label": "bcc", "score": 0.91}]

        classifier = VitSkinClassifier(_pipeline=mock_pipe)
        result = classifier.classify(Image.new("RGB", (224, 224)))

        assert result.predictions[0].risk_level == "high"

    def test_description_format(self):
        mock_pipe = MagicMock()
        mock_pipe.return_value = [{"label": "nv", "score": 0.90}]

        classifier = VitSkinClassifier(_pipeline=mock_pipe)
        result = classifier.classify(Image.new("RGB", (224, 224)))

        assert "nv" in result.description
        assert "90" in result.description

    def test_version(self):
        classifier = VitSkinClassifier(_pipeline=MagicMock())
        assert "vit-skin" in classifier.version
