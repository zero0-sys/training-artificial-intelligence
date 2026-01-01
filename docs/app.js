const video = document.getElementById("video");
const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");
const output = document.getElementById("output");
const recStatus = document.getElementById("recStatus");

let stream;
let useFront = true;
let recorder;
let chunks = [];
let recording = false;

// ===== INIT =====
async function initApp() {
  await startCamera();

  document.getElementById("loader").classList.add("hidden");
  document.getElementById("app").classList.remove("hidden");
}

initApp();


// ===== CAMERA =====
async function startCamera() {
  if (stream) stream.getTracks().forEach(t => t.stop());

  stream = await navigator.mediaDevices.getUserMedia({
    video: { facingMode: useFront ? "user" : "environment" }
  });

  video.srcObject = stream;

  video.onloadedmetadata = () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
  };

  recorder = new MediaRecorder(stream, { mimeType: "video/mp4" });
  recorder.ondataavailable = e => chunks.push(e.data);
  recorder.onstop = saveVideo;
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

function saveVideo() {
  const blob = new Blob(chunks, { type: "video/mp4" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "record.mp4";
  a.click();
}

// ===== SEND FRAME TO BACKEND =====
async function sendFrame() {
  if (!video.videoWidth) return;

  // sync canvas size (PENTING!)
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const off = document.createElement("canvas");
  off.width = video.videoWidth;
  off.height = video.videoHeight;
  off.getContext("2d").drawImage(video, 0, 0);

  try {
    const res = await fetch("https://chatbot-ai-agent-production-03b2.up.railway.app/detect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: off.toDataURL("image/jpeg") })
    });

    const data = await res.json();

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (Array.isArray(data) && data.length > 0) {
      output.innerText = "Detected: " + data.map(d => d.digit).join(" ");

      ctx.strokeStyle = "#22c55e";
      ctx.fillStyle = "#22c55e";
      ctx.lineWidth = 3;
      ctx.font = "20px monospace";

      data.forEach(d => {
        const { x, y, w, h } = d.box;
        ctx.strokeRect(x, y, w, h);
        ctx.fillText(
          `${d.digit} (${d.confidence})`,
          x,
          y - 8 < 10 ? y + 20 : y - 8
        );
      });
    } else {
      output.innerText = "Detected: -";
    }
  } catch (err) {
    console.error(err);
  }
}

setInterval(sendFrame, 600);
