from __future__ import annotations

import base64
import logging
import os
from pathlib import Path
from threading import Lock
from typing import Any, List, Sequence

import cv2
import mediapipe as mp
import numpy as np
from tensorflow import keras

logger = logging.getLogger(__name__)


# Supported ISL output classes: letters, numbers, and common words/phrases.
DEFAULT_LABELS: list[str] = [
    *[chr(code) for code in range(ord("A"), ord("Z") + 1)],
    *[str(num) for num in range(10)],
    "Hello",
    "Thank You",
    "How Are You",
    "Yes",
    "No",
    "Please",
    "Sorry",
    "I Love You",
    "Help",
    "Stop",
    "Eat",
    "Drink",
    "Friend",
    "Good",
    "Bad",
    "Morning",
    "Night",
    "Wait",
    "Again",
    "Finish",
]


class ISLDetector:
    """Loads and serves ISL predictions from a Mediapipe + Keras pipeline."""

    def __init__(
        self,
        model_path: str,
        labels: Sequence[str] | None = None,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        self.model_path = model_path
        self.labels = list(labels) if labels else DEFAULT_LABELS
        self._model_lock = Lock()
        self._hands_lock = Lock()

        self._model = self._load_model()
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def _load_model(self) -> keras.Model:
        """Load Keras model once; fallback to a light dummy model if not found."""
        model_file = Path(self.model_path)
        if model_file.exists():
            logger.info("Loading model from %s", model_file)
            return keras.models.load_model(model_file)

        logger.warning(
            "Model file %s not found. Creating a fallback random-initialized model.",
            model_file,
        )
        # Fallback model keeps the app fully runnable for UI/API testing.
        model = keras.Sequential(
            [
                keras.layers.Input(shape=(63,)),
                keras.layers.Dense(128, activation="relu"),
                keras.layers.Dropout(0.2),
                keras.layers.Dense(len(self.labels), activation="softmax"),
            ]
        )
        model.compile(optimizer="adam", loss="sparse_categorical_crossentropy")
        return model

    def decode_base64_frame(self, frame_b64: str) -> np.ndarray:
        """Decode a base64 image (optionally data URL) into BGR frame."""
        payload = frame_b64.split(",", 1)[1] if "," in frame_b64 else frame_b64
        binary = base64.b64decode(payload)
        nparr = np.frombuffer(binary, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Unable to decode frame.")
        return frame

    def extract_keypoints(self, frame_bgr: np.ndarray) -> np.ndarray:
        """Extract 21 hand landmarks (x, y, z) flattened to 63-dim vector."""
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        with self._hands_lock:
            results = self._hands.process(frame_rgb)

        if not results.multi_hand_landmarks:
            return np.zeros(63, dtype=np.float32)

        hand_landmarks = results.multi_hand_landmarks[0]
        keypoints: List[float] = []
        for landmark in hand_landmarks.landmark:
            keypoints.extend([landmark.x, landmark.y, landmark.z])
        return np.array(keypoints, dtype=np.float32)

    def predict_from_frame(self, frame_bgr: np.ndarray) -> dict[str, Any]:
        """Predict ISL gesture from a single BGR frame."""
        keypoints = self.extract_keypoints(frame_bgr)
        model_input = np.expand_dims(keypoints, axis=0)
        with self._model_lock:
            probs = self._model.predict(model_input, verbose=0)[0]

        best_idx = int(np.argmax(probs))
        confidence = float(probs[best_idx])
        label = self.labels[best_idx] if best_idx < len(self.labels) else "Unknown"
        return {
            "prediction": label,
            "confidence": confidence,
            "keypoints_detected": bool(np.count_nonzero(keypoints)),
        }

    def predict_video(self, video_path: str, sample_every_n_frames: int = 5) -> dict[str, Any]:
        """Predict gesture from sampled frames in a video file."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Unable to open uploaded video.")

        votes: dict[str, int] = {}
        confidences: List[float] = []
        frame_idx = 0

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_idx % sample_every_n_frames == 0:
                result = self.predict_from_frame(frame)
                pred = str(result["prediction"])
                votes[pred] = votes.get(pred, 0) + 1
                confidences.append(float(result["confidence"]))
            frame_idx += 1

        cap.release()

        if not votes:
            return {
                "prediction": "No gesture detected",
                "confidence": 0.0,
                "frames_processed": frame_idx,
            }

        best_prediction = max(votes, key=votes.get)
        avg_conf = float(np.mean(confidences)) if confidences else 0.0
        return {
            "prediction": best_prediction,
            "confidence": avg_conf,
            "frames_processed": frame_idx,
            "vote_breakdown": votes,
        }


def ensure_ffmpeg_in_path() -> bool:
    """Check if ffmpeg is available in PATH for video processing workflows."""
    return any(
        os.access(os.path.join(path, "ffmpeg"), os.X_OK)
        or os.access(os.path.join(path, "ffmpeg.exe"), os.X_OK)
        for path in os.environ.get("PATH", "").split(os.pathsep)
    )
