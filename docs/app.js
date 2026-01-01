const video = document.getElementById("video");
const result = document.getElementById("result");

let recording = false;
let recorder, chunks = [];

navigator.mediaDevices.getUserMedia({ video: true })
.then(stream => {
  video.srcObject = stream;
  recorder = new MediaRecorder(stream);

  recorder.ondataavailable = e => chunks.push(e.data);
  recorder.onstop = () => {
    const blob = new Blob(chunks, { type: "video/webm" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "record.webm";
    a.click();
    chunks = [];
  };
});

function toggleRecord() {
  recording = !recording;
  if (recording) recorder.start();
  else recorder.stop();
}

function sendFrame() {
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);

  fetch("/detect", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: canvas.toDataURL() })
  })
  .then(res => res.json())
  .then(data => {
    if (data.length > 0) {
      result.innerText = data.map(d => d.digit).join(" ");
    }
  });
}

setInterval(sendFrame, 800);
