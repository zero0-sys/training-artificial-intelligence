import cv2, os
import numpy as np
from tensorflow.keras.models import load_model

model = load_model("mnist_cnn.keras")

X, y = [], []

for digit in range(10):
    folder = f"training/my_digits/{digit}"
    for file in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,file),0)
        img = cv2.resize(img,(28,28))
        img = img / 255.0
        X.append(img)
        y.append(digit)

X = np.array(X).reshape(-1,28,28,1)
y = np.array(y)

model.fit(X,y,epochs=5)
model.save("mnist_cnn_me.keras")

print("FINE-TUNE SELESAI (PAKAI TULISAN KAMU)")
