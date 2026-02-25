"""Response schemas for LensForge API."""

from pydantic import BaseModel


class PredictionSchema(BaseModel):
    """Single classification prediction."""

    label: str
    probability: float
    risk_level: str | None = None


class AnalyzeResponse(BaseModel):
    """Analysis result for a single image."""

    status: str  # success | rejected_quality | rejected_nsfw | error
    reason: str | None = None
    lesion_detected: bool | None = None
    main_description: str | None = None
    predictions: list[PredictionSchema] = []
    urgency: str | None = None
    disclaimer: str = ""
    inference_time_ms: int = 0
    model_versions: dict[str, str] = {}


class BatchAnalyzeResponse(BaseModel):
    """Batch analysis results."""

    results: list[AnalyzeResponse]
