"""BrisqueChecker tests."""

from PIL import Image, ImageFilter

from custom.extensions.dermatology.brisque_checker import BrisqueChecker


class TestBrisqueChecker:
    def test_accepts_sharp_image(self, sharp_image):
        checker = BrisqueChecker(blur_threshold=50.0)
        result = checker.check(sharp_image)
        assert result.is_acceptable is True
        assert result.score > 0

    def test_rejects_blurry_image(self):
        img = Image.new("RGB", (224, 224), color=(180, 130, 100))
        blurred = img.filter(ImageFilter.GaussianBlur(radius=20))

        checker = BrisqueChecker(blur_threshold=50.0)
        result = checker.check(blurred)
        assert result.is_acceptable is False
        assert "blurry" in result.reason.lower()

    def test_rejects_solid_color(self):
        img = Image.new("RGB", (224, 224), color=(128, 128, 128))

        checker = BrisqueChecker(blur_threshold=50.0)
        result = checker.check(img)
        assert result.is_acceptable is False

    def test_threshold_configurable(self, sharp_image):
        # Very high threshold should reject even sharp images
        checker = BrisqueChecker(blur_threshold=999999.0)
        result = checker.check(sharp_image)
        assert result.is_acceptable is False

    def test_version(self):
        checker = BrisqueChecker()
        assert checker.version == "brisque-laplacian-1.0"
