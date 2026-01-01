import cv2
import numpy as np
from tensorflow.keras.models import load_model

model = load_model("mnist_cnn.keras")

url = "http://192.168.1.5:8080/video"
cap = cv2.VideoCapture(url)

# 🔽 SOLUSI 2: atur ukuran WINDOW (bukan frame)
cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Camera", 640, 480)

cv2.namedWindow("Threshold", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Threshold", 640, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame gagal")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    thresh = cv2.threshold(
        blur, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if contours:
        cnt = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(cnt)

        if w > 30 and h > 30:
            roi = thresh[y:y+h, x:x+w]

            # padding biar mirip MNIST
            pad = 20
            roi = cv2.copyMakeBorder(
                roi, pad, pad, pad, pad,
                cv2.BORDER_CONSTANT, value=0
            )

            roi = cv2.resize(roi, (28,28))
            roi = roi.astype("float32") / 255.0
            roi = roi.reshape(1,28,28,1)

            pred = model.predict(roi, verbose=0)
            digit = np.argmax(pred)
            conf = np.max(pred)

            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(
                frame,
                f"{digit} ({conf:.2f})",
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                2
            )

    cv2.imshow("Camera", frame)
    cv2.imshow("Threshold", thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
