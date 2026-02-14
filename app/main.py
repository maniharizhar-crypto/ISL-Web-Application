from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router
from app.services.isl_detector import ISLDetector, ensure_ffmpeg_in_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = str(Path("models") / "isl_model.h5")

# Loaded once at import time so all routes reuse the same model/hands context.
detector = ISLDetector(model_path=MODEL_PATH)

templates = Jinja2Templates(directory="templates")

app = FastAPI(title="ISL Web Detector", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)


@app.on_event("startup")
async def startup_event() -> None:
    if ensure_ffmpeg_in_path():
        logger.info("ffmpeg found in PATH.")
    else:
        logger.warning("ffmpeg not found in PATH. Video workflows may fail.")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})
