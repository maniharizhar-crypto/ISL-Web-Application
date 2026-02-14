const video = document.getElementById('video');
const overlay = document.getElementById('overlay');
const videoFrame = document.getElementById('videoFrame');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const speakBtn = document.getElementById('speakBtn');
const predictionText = document.getElementById('predictionText');
const confidenceText = document.getElementById('confidenceText');
const confidenceBar = document.getElementById('confidenceBar');
const predictionLog = document.getElementById('predictionLog');
const uploadForm = document.getElementById('uploadForm');
const videoUpload = document.getElementById('videoUpload');
const drawerToggle = document.getElementById('drawerToggle');
const historyCard = document.querySelector('.history-card');
const toast = document.getElementById('toast');
const canvas = document.getElementById('captureCanvas');
const ctx = canvas.getContext('2d');

let stream = null;
let predictionTimer = null;
let toastTimer = null;
let latestPrediction = '—';
const logItems = [];

/**
 * Render a short toast notification at the bottom of the screen.
 */
function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 1800);
}

/**
 * Render the latest 5 predictions with icon, text, and timestamp.
 */
function renderLog() {
  predictionLog.innerHTML = '';
  logItems.forEach((item) => {
    const li = document.createElement('li');
    li.innerHTML = `<span class="item-icon">🤟</span><span>${item.text}</span><span class="item-time">${item.time}</span>`;
    predictionLog.appendChild(li);
  });
}

/**
 * Update prediction UI, confidence bar, animations, history, and optional speech.
 */
function setPrediction(prediction, confidence) {
  latestPrediction = prediction;
  predictionText.textContent = prediction;
  predictionText.classList.remove('updated');
  void predictionText.offsetWidth;
  predictionText.classList.add('updated');

  const percentage = Math.max(0, Math.min(100, confidence * 100));
  confidenceText.textContent = `Confidence: ${percentage.toFixed(2)}%`;
  confidenceBar.style.width = `${percentage}%`;
  overlay.textContent = `Detected: ${prediction}`;

  videoFrame.classList.add('detected');
  setTimeout(() => videoFrame.classList.remove('detected'), 1000);

  logItems.unshift({ text: prediction, time: new Date().toLocaleTimeString() });
  if (logItems.length > 5) logItems.pop();
  renderLog();

  showToast(`Gesture recognized: ${prediction}`);
}

/**
 * Run speech synthesis on the most recently recognized sign.
 */
function speakCurrentPrediction() {
  if (!('speechSynthesis' in window) || latestPrediction === '—') {
    showToast('No detected gesture available for speech.');
    return;
  }
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(new SpeechSynthesisUtterance(latestPrediction));
}

/**
 * Capture a frame from webcam and request prediction from backend.
 */
async function sendFrameForPrediction() {
  if (!stream) return;

  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  const frameBase64 = canvas.toDataURL('image/jpeg', 0.8);

  try {
    const response = await fetch('/predict-frame', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ frame: frameBase64 }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Prediction failed');

    setPrediction(data.prediction, data.confidence);
  } catch (error) {
    overlay.textContent = `Prediction error: ${error.message}`;
  }
}

startBtn.addEventListener('click', async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    video.srcObject = stream;
    overlay.textContent = 'Webcam running...';
    videoFrame.classList.add('active');
    startBtn.disabled = true;
    stopBtn.disabled = false;

    predictionTimer = window.setInterval(sendFrameForPrediction, 700);
  } catch (error) {
    overlay.textContent = `Unable to start webcam: ${error.message}`;
  }
});

stopBtn.addEventListener('click', () => {
  if (predictionTimer) {
    clearInterval(predictionTimer);
    predictionTimer = null;
  }
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
    stream = null;
  }

  video.srcObject = null;
  overlay.textContent = 'Camera stopped';
  videoFrame.classList.remove('active', 'detected');
  startBtn.disabled = false;
  stopBtn.disabled = true;
});

speakBtn.addEventListener('click', speakCurrentPrediction);

uploadForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const file = videoUpload.files?.[0];
  if (!file) {
    overlay.textContent = 'Please choose a video file first.';
    return;
  }

  const formData = new FormData();
  formData.append('file', file);
  overlay.textContent = 'Uploading video for prediction...';

  try {
    const response = await fetch('/upload-video', {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Upload prediction failed');

    setPrediction(data.prediction, data.confidence);
  } catch (error) {
    overlay.textContent = `Upload error: ${error.message}`;
  } finally {
    uploadForm.reset();
  }
});

if (drawerToggle) {
  drawerToggle.addEventListener('click', () => {
    historyCard.classList.toggle('open');
  });
}
