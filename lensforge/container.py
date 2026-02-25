"""Dependency injection container with dynamic extension loading."""

import importlib

from dependency_injector import containers, providers

from lensforge.config import Settings
from lensforge.loaders.image_loader import ImageLoader
from lensforge.pipeline.analysis_pipeline import AnalysisPipeline


def import_class(dotted_path: str) -> type:
    """Import a class from a dotted module path."""
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def _create_quality(quality_class: str, blur_threshold: float):
    cls = import_class(quality_class)
    return cls(blur_threshold=blur_threshold)


def _create_nsfw(nsfw_class: str, threshold: float):
    cls = import_class(nsfw_class)
    return cls(threshold=threshold)


def _create_classifier(classifier_class: str, model_name: str, device: str):
    cls = import_class(classifier_class)
    return cls(model_name=model_name, device=device)


class Container(containers.DeclarativeContainer):
    """DI container wiring all LensForge components via dynamic extension loading."""

    config = providers.Configuration()

    settings = providers.Singleton(Settings)

    image_loader = providers.Singleton(
        ImageLoader,
        max_size=config.max_image_size.as_int(),
    )

    quality_checker = providers.Singleton(
        _create_quality,
        quality_class=config.quality_class,
        blur_threshold=config.quality_blur_threshold.as_float(),
    )

    nsfw_detector = providers.Singleton(
        _create_nsfw,
        nsfw_class=config.nsfw_class,
        threshold=config.nsfw_threshold.as_float(),
    )

    domain_classifier = providers.Singleton(
        _create_classifier,
        classifier_class=config.classifier_class,
        model_name=config.classifier_model_name,
        device=config.device,
    )

    analysis_pipeline = providers.Factory(
        AnalysisPipeline,
        quality=quality_checker,
        safety=nsfw_detector,
        classifier=domain_classifier,
    )
