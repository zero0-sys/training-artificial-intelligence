import cv2
import numpy as np
from tensorflow.keras.models import load_model

# ===== LOAD MODEL (HASIL FINE-TUNE) =====
model = load_model("mnist_cnn_me.keras")

# ===== KONFIGURASI =====
MIN_SIZE = 30          # ukuran minimum angka
CONF_THRESHOLD = 0.6   # confidence minimum
MAX_CONTOURS = 10      # biar noise ga kebanyakan


def detect_digits(frame):
    """
    Menerima frame (BGR image)
    Mengembalikan list digit + confidence
    """

    # SAFETY CHECK
    if frame is None:
        return []

    # ===== PREPROCESS =====
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.threshold(
        blur, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    # ===== FIND CONTOURS =====
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return []

    # ===== SORT KIRI → KANAN (PENTING UNTUK MULTI DIGIT) =====
    contours = sorted(
        contours,
        key=lambda c: cv2.boundingRect(c)[0]
    )

    results = []

    for cnt in contours[:MAX_CONTOURS]:
        x, y, w, h = cv2.boundingRect(cnt)

        if w < MIN_SIZE or h < MIN_SIZE:
            continue

        # ===== ROI =====
        roi = thresh[y:y+h, x:x+w]

        # ===== BUAT PERSEGI (CENTERING) =====
        size = max(w, h)
        square = np.zeros((size, size), dtype=np.uint8)

        y_off = (size - h) // 2
        x_off = (size - w) // 2
        square[y_off:y_off+h, x_off:x_off+w] = roi

        # ===== RESIZE KE MNIST =====
        square = cv2.resize(square, (28, 28))
        square = square.astype("float32") / 255.0
        square = square.reshape(1, 28, 28, 1)

        # ===== PREDICT =====
        pred = model.predict(square, verbose=0)
        digit = int(np.argmax(pred))
        conf = float(np.max(pred))

        if conf < CONF_THRESHOLD:
            continue

        results.append({
            "digit": digit,
            "confidence": round(conf, 2),
            "box": {
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h)
            }
        })

    return results
