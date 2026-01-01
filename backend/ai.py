import cv2
import numpy as np
from tensorflow.keras.models import load_model

model = load_model("mnist_cnn_me.keras")

CONF_THRESHOLD = 0.6

def predict_digit(img):
    """
    Prediksi SATU angka dari image (BGR)
    Return: (digit, confidence) atau (None, None)
    """

    if img is None:
        return None, None

    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold
    _, thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # Ambil kontur terbesar (diasumsikan 1 angka)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None, None

    cnt = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(cnt)

    if w < 20 or h < 20:
        return None, None

    roi = thresh[y:y+h, x:x+w]

    # Bikin square + center
    size = max(w, h)
    square = np.zeros((size, size), dtype=np.uint8)
    square[(size-h)//2:(size-h)//2+h,
           (size-w)//2:(size-w)//2+w] = roi

    # Resize MNIST
    square = cv2.resize(square, (28,28))
    square = square.astype("float32") / 255.0
    square = square.reshape(1,28,28,1)

    pred = model.predict(square, verbose=0)
    digit = int(np.argmax(pred))
    conf = float(np.max(pred))

    if conf < CONF_THRESHOLD:
        return None, None

    return digit, round(conf, 2)
