from flask import Flask, request, jsonify
import base64
import numpy as np
import cv2
from detector import detect_digits

app = Flask(__name__)

# ===== HEALTH CHECK (UNTUK RAILWAY) =====
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# ===== DETECT ENDPOINT =====
@app.route("/detect", methods=["POST"])
def detect():
    try:
        data = request.json.get("image")
        if not data:
            return jsonify({"error": "No image provided"}), 400

        # Decode base64 → OpenCV image
        img_bytes = base64.b64decode(data.split(",")[1])
        img_array = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"error": "Invalid image"}), 400

        results = detect_digits(frame)
        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
