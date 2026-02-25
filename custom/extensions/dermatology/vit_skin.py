"""ViT skin lesion classifier (HAM10000 / ISIC)."""

from typing import Any

from PIL import Image

from lensforge.interfaces.domain_classifier import ClassificationResult, Prediction

RISK_MAP: dict[str, str] = {
    "mel": "high",  # melanoma
    "bcc": "high",  # basal cell carcinoma
    "akiec": "moderate",  # actinic keratoses
    "df": "low",  # dermatofibroma
    "nv": "low",  # melanocytic nevi (moles)
    "bkl": "low",  # benign keratosis
    "vasc": "low",  # vascular lesions
}

URGENCY_MAP: dict[str, str] = {
    "high": "Consult dermatologist within days",
    "moderate": "Consult dermatologist within weeks",
    "low": "Monitor, no immediate urgency",
}


def _load_pipeline(model_name: str, device: str) -> Any:
    """Lazy-load transformers pipeline."""
    from transformers import pipeline

    return pipeline("image-classification", model=model_name, device=device, top_k=5)


class VitSkinClassifier:
    """Skin lesion classifier using ViT fine-tuned on HAM10000."""

    def __init__(
        self,
        model_name: str = "Anwarkh1/Skin_Cancer-Image_Classification",
        device: str = "cpu",
        _pipeline: Any = None,
    ) -> None:
        self._model_name = model_name
        self._device = device
        self._pipe = _pipeline

    def _get_pipe(self) -> Any:
        if self._pipe is None:
            self._pipe = _load_pipeline(self._model_name, self._device)
        return self._pipe

    @property
    def version(self) -> str:
        return f"vit-skin-{self._model_name.split('/')[-1]}"

    def classify(self, image: Image.Image) -> ClassificationResult:
        results = self._get_pipe()(image)

        predictions = [
            Prediction(
                label=r["label"],
                probability=round(r["score"], 4),
                risk_level=RISK_MAP.get(r["label"]),
            )
            for r in results
        ]

        top = predictions[0] if predictions else None
        risk = top.risk_level if top else None

        return ClassificationResult(
            detected=True,
            predictions=predictions,
            description=(
                f"Top prediction: {top.label} ({top.probability:.1%})" if top else "No prediction"
            ),
            urgency=URGENCY_MAP.get(risk) if risk else None,
        )
