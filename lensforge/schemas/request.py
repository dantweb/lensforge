"""Request schemas for LensForge API."""

from pydantic import BaseModel, Field, model_validator


class AnalyzeRequest(BaseModel):
    """Single image analysis request."""

    image_base64: str | None = Field(None, description="Base64-encoded image")
    image_url: str | None = Field(None, description="URL to fetch image from")

    @model_validator(mode="after")
    def check_at_least_one(self) -> "AnalyzeRequest":
        if not self.image_base64 and not self.image_url:
            raise ValueError("Provide image_base64 or image_url")
        return self


class BatchAnalyzeRequest(BaseModel):
    """Batch image analysis request."""

    images: list[AnalyzeRequest] = Field(..., max_length=50)
