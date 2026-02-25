"""AnalysisPipeline tests (all models mocked)."""

from PIL import Image

from lensforge.pipeline.analysis_pipeline import DISCLAIMER, AnalysisPipeline


class TestPipelineRejection:
    def test_rejects_low_quality(self, mock_quality_bad, mock_nsfw_safe, mock_classifier):
        pipe = AnalysisPipeline(mock_quality_bad, mock_nsfw_safe, mock_classifier)
        result = pipe.analyze(Image.new("RGB", (224, 224)))

        assert result.status == "rejected_quality"
        assert result.reason == "Too blurry"
        mock_nsfw_safe.detect.assert_not_called()
        mock_classifier.classify.assert_not_called()

    def test_rejects_nsfw(self, mock_quality_ok, mock_nsfw_unsafe, mock_classifier):
        pipe = AnalysisPipeline(mock_quality_ok, mock_nsfw_unsafe, mock_classifier)
        result = pipe.analyze(Image.new("RGB", (224, 224)))

        assert result.status == "rejected_nsfw"
        assert "NSFW" in (result.reason or "")
        mock_classifier.classify.assert_not_called()


class TestPipelineSuccess:
    def test_full_pipeline(self, mock_quality_ok, mock_nsfw_safe, mock_classifier):
        pipe = AnalysisPipeline(mock_quality_ok, mock_nsfw_safe, mock_classifier)
        result = pipe.analyze(Image.new("RGB", (224, 224)))

        assert result.status == "success"
        assert result.lesion_detected is True
        assert len(result.predictions) == 2
        assert result.predictions[0].label == "nv"

    def test_includes_disclaimer(self, mock_quality_ok, mock_nsfw_safe, mock_classifier):
        pipe = AnalysisPipeline(mock_quality_ok, mock_nsfw_safe, mock_classifier)
        result = pipe.analyze(Image.new("RGB", (224, 224)))

        assert result.disclaimer == DISCLAIMER
        assert "NOT a medical diagnosis" in result.disclaimer

    def test_includes_model_versions(self, mock_quality_ok, mock_nsfw_safe, mock_classifier):
        pipe = AnalysisPipeline(mock_quality_ok, mock_nsfw_safe, mock_classifier)
        result = pipe.analyze(Image.new("RGB", (224, 224)))

        assert "nn1_quality" in result.model_versions
        assert "nn1_safety" in result.model_versions
        assert "nn2" in result.model_versions

    def test_measures_inference_time(self, mock_quality_ok, mock_nsfw_safe, mock_classifier):
        pipe = AnalysisPipeline(mock_quality_ok, mock_nsfw_safe, mock_classifier)
        result = pipe.analyze(Image.new("RGB", (224, 224)))

        assert result.inference_time_ms >= 0

    def test_melanoma_high_urgency(self, mock_quality_ok, mock_nsfw_safe, mock_classifier_melanoma):
        pipe = AnalysisPipeline(mock_quality_ok, mock_nsfw_safe, mock_classifier_melanoma)
        result = pipe.analyze(Image.new("RGB", (224, 224)))

        assert result.status == "success"
        assert result.predictions[0].risk_level == "high"
        assert "days" in (result.urgency or "").lower()
