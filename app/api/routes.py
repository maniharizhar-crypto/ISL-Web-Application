from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.schemas import FramePredictionRequest, PredictionResponse
from app.services.isl_detector import ISLDetector

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_detector() -> ISLDetector:
    from app.main import detector

    return detector


@router.get("/test")
async def test() -> dict[str, str]:
    return {"status": "ok", "message": "ISL Web Detector API is healthy"}


@router.post("/predict-frame", response_model=PredictionResponse)
async def predict_frame(
    payload: FramePredictionRequest,
    detector: Annotated[ISLDetector, Depends(get_detector)],
) -> PredictionResponse:
    try:
        frame = detector.decode_base64_frame(payload.frame)
        result = detector.predict_from_frame(frame)
        return PredictionResponse(**result)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Frame prediction failed: {exc}",
        ) from exc


@router.post("/upload-video", response_model=PredictionResponse)
async def upload_video(
    detector: Annotated[ISLDetector, Depends(get_detector)],
    file: Annotated[UploadFile, File(...)],
) -> PredictionResponse:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    target = UPLOAD_DIR / f"{uuid4().hex}{suffix}"
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        target.write_bytes(content)

        result = detector.predict_video(str(target))
        return PredictionResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video prediction failed: {exc}",
        ) from exc
    finally:
        await file.close()
        if target.exists():
            os.remove(target)
