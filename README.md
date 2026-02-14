# ISL Interpreter Web App

A full-stack FastAPI web application for Indian Sign Language (ISL) recognition using MediaPipe hand landmarks and a TensorFlow/Keras classifier.

## Supported Sign Classes
- **Letters:** A-Z
- **Numbers:** 0-9
- **Core words/phrases:**
  - Hello, Thank You, How Are You, Yes, No, Please, Sorry, I Love You, Help, Stop
  - Eat, Drink, Friend, Good, Bad, Morning, Night, Wait, Again, Finish

## Features
- Modern hero-first UI with responsive layout for desktop/tablet
- Live webcam sign recognition with confidence score + animated confidence bar
- Last 5 sign history panel with timestamps
- Upload saved videos for prediction (`/upload-video`)
- Optional speech output for the latest recognized sign
- Toast notifications when a new gesture is recognized

## API Endpoints
- `GET /test` health check
- `POST /predict-frame` frame-level prediction from base64 image
- `POST /upload-video` uploaded video prediction

## Run locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) place your trained model in:
   ```
   models/isl_model.h5
   ```
3. Start the app:
   ```bash
   python app.py
   ```
4. Open:
   ```
   http://127.0.0.1:8000
   ```

## Notes
- The app checks for `ffmpeg` in `PATH` on startup.
- If `models/isl_model.h5` is missing, a fallback model is created so UI/API flows still run.
