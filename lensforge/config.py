"""LensForge configuration from custom/.env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    device: str = "cpu"

    # Dotted class paths to extension implementations
    quality_class: str = "custom.extensions.dermatology.brisque_checker.BrisqueChecker"
    quality_blur_threshold: float = 100.0

    nsfw_class: str = "custom.extensions.dermatology.falconsai_nsfw.FalconsaiNsfwDetector"
    nsfw_threshold: float = 0.7

    classifier_class: str = "custom.extensions.dermatology.vit_skin.VitSkinClassifier"
    classifier_model_name: str = "Anwarkh1/Skin_Cancer-Image_Classification"

    max_image_size: int = 1024
    host: str = "0.0.0.0"
    port: int = 8000
    hf_token: str | None = None

    model_config = SettingsConfigDict(env_file="custom/.env", extra="ignore")
