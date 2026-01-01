const video = document.getElementById("video");
const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");
const output = document.getElementById("output");
const recStatus = document.getElementById("recStatus");
const logs = document.getElementById("logs");
const fpsEl = document.getElementById("fps");
const latencyEl = document.getElementById("latency");

let stream;
let lastFrameTime = Date.now();
let useFront = true;
let recorder;
let chunks = [];
let recording = false;

// ===== INIT =====
async function initApp() {
  try {
    await startCamera();
    // Loader will be hidden in onloadedmetadata
  } catch (err) {
    console.error("Failed to initialize app:", err);
    const loaderH1 = document.querySelector("#loader h1");
    if (loaderH1) {
      loaderH1.innerText = "ERROR: CAMERA ACCESS DENIED";
      loaderH1.style.color = "#ff4444";
    }
  }
}

initApp();

// ===== CAMERA =====
async function startCamera() {
  if (stream) {
    stream.getTracks().forEach(t => t.stop());
  }

  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { 
        facingMode: useFront ? "user" : "environment",
        width: { ideal: 1280 },
        height: { ideal: 720 }
      }
    });

    video.srcObject = stream;

    return new Promise((resolve) => {
      video.onloadedmetadata = () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        setupRecorder();
        
        // Hide loader with a small delay for smooth transition
        setTimeout(() => {
          document.getElementById("loader").style.opacity = "0";
          setTimeout(() => {
            document.getElementById("loader").classList.add("hidden");
            document.getElementById("app").classList.remove("hidden");
            document.getElementById("app").style.opacity = "1";
          }, 500);
        }, 1000);
        
        resolve();
      };
    });
  } catch (err) {
    console.error("Error accessing camera:", err);
    throw err;
  }
}

function setupRecorder() {
  // To record with overlays, we need to capture from a canvas that combines video + drawings
  const captureCanvas = document.createElement("canvas");
  const captureCtx = captureCanvas.getContext("2d");
  captureCanvas.width = video.videoWidth;
  captureCanvas.height = video.videoHeight;

  // Function to draw everything to capture canvas
  function updateCapture() {
    if (recording) {
      captureCtx.drawImage(video, 0, 0);
      captureCtx.drawImage(canvas, 0, 0);
      requestAnimationFrame(updateCapture);
    }
  }

  const captureStream = captureCanvas.captureStream(30); // 30 FPS
  
  const mimeTypes = [
  "video/webm;codecs=vp9",
  "video/webm;codecs=vp8",
  "video/webm"
];

  let selectedMimeType = "";
  
  for (const type of mimeTypes) {
    if (MediaRecorder.isTypeSupported(type)) {
      selectedMimeType = type;
      break;
    }
  }

  if (selectedMimeType) {
    recorder = new MediaRecorder(captureStream, { mimeType: selectedMimeType });
    recorder.ondataavailable = e => {
      if (e.data.size > 0) chunks.push(e.data);
    };
    recorder.onstop = saveVideo;
    
    // Start the capture loop when recording starts
    const originalStart = recorder.start.bind(recorder);
    recorder.start = () => {
      updateCapture();
      originalStart();
    };
  } else {
    console.error("No supported video mime types found");
  }
}

// ===== SWITCH CAMERA =====
function switchCamera() {
  useFront = !useFront;
  startCamera();
}

// ===== RECORD =====
function toggleRecord() {
  if (!recorder) return;

  if (!recording) {
    chunks = [];
    recorder.start();
    recording = true;
    recStatus.innerText = "● REC";
    recStatus.className = "rec";
  } else {
    recorder.stop();
    recording = false;
    recStatus.innerText = "● IDLE";
    recStatus.className = "idle";
  }
}

function addLog(msg) {
  const entry = document.createElement("div");
  entry.className = "log-entry";
  entry.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
  logs.prepend(entry);
  if (logs.children.length > 20) logs.lastChild.remove();
}

function saveVideo() {
  if (!chunks.length) {
    addLog("Recording failed: empty file");
    return;
  }

  const blob = new Blob(chunks, { type: recorder.mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `cyber-detect-${Date.now()}.webm`;
  a.click();
  addLog("Video record saved.");
}


// ===== SEND FRAME TO BACKEND =====
async function sendFrame() {
  if (!video.videoWidth) return;

  const now = Date.now();
  const fps = Math.round(1000 / (now - lastFrameTime));
  lastFrameTime = now;
  fpsEl.innerText = fps;

  // sync canvas size
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const off = document.createElement("canvas");
  off.width = video.videoWidth;
  off.height = video.videoHeight;
  off.getContext("2d").drawImage(video, 0, 0);

  const startTime = Date.now();
  try {
    const backendUrl = "https://training-artificial-intelligence-production.up.railway.app/detect";
    
    const res = await fetch(backendUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: off.toDataURL("image/jpeg", 0.6) })
    });

    latencyEl.innerText = (Date.now() - startTime) + "ms";

    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    
    const data = await res.json();

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (Array.isArray(data) && data.length > 0) {
      const detectedStr = data.map(d => d.digit).join("");
      output.innerHTML = `<span>Detected:</span> <span class="digit-res">${detectedStr}</span>`;
      addLog(`Detected: ${detectedStr}`);

      ctx.strokeStyle = "#00f2ff";
      ctx.fillStyle = "#00f2ff";
      ctx.shadowBlur = 10;
      ctx.shadowColor = "#00f2ff";
      ctx.lineWidth = 2;
      ctx.font = "bold 18px 'Orbitron', sans-serif";

      data.forEach(d => {
        const { x, y, w, h } = d.box;
        const len = 15;
        ctx.beginPath();
        ctx.moveTo(x, y + len); ctx.lineTo(x, y); ctx.lineTo(x + len, y);
        ctx.moveTo(x + w - len, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + len);
        ctx.moveTo(x + w, y + h - len); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w - len, y + h);
        ctx.moveTo(x + len, y + h); ctx.lineTo(x, y + h); ctx.lineTo(x, y + h - len);
        ctx.stroke();
        
        ctx.fillText(`${d.digit} [${Math.round(d.confidence * 100)}%]`, x, y - 10);
      });
    } else {
      output.innerText = "SCANNING...";
    }
  } catch (err) {
    latencyEl.innerText = "ERR";
    output.innerText = "OFFLINE";
    output.style.color = "#ff4444";
  }
}

setInterval(sendFrame, 600);
