from pydantic import BaseModel, Field


class FramePredictionRequest(BaseModel):
    frame: str = Field(..., description="Base64 encoded image frame (optionally as data URL)")


class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    keypoints_detected: bool | None = None
    frames_processed: int | None = None
    vote_breakdown: dict[str, int] | None = None
