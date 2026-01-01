import cv2, os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Load the improved base model
if os.path.exists("mnist_cnn.keras"):
    model = load_model("mnist_cnn.keras")
else:
    print("Base model not found. Please run train_mnist.py first.")
    exit()

X, y = [], []

# Load custom digits
base_path = "training/my_digits"
for digit in range(11): # Including folder '10' if it exists
    folder = os.path.join(base_path, str(digit))
    if not os.path.exists(folder):
        continue
        
    for file in os.listdir(folder):
        if file.endswith(('.jpg', '.jpeg', '.png')):
            img = cv2.imread(os.path.join(folder, file), 0)
            if img is None: continue
            img = cv2.resize(img, (28, 28))
            # Invert if necessary (MNIST is white on black)
            # We assume user input might be black on white, so we check mean
            if np.mean(img) > 127:
                img = 255 - img
            
            img = img / 255.0
            X.append(img)
            # If folder is '10', we might want to map it to something or ignore
            # For now, let's map 10 to 1 (as it's likely a '1' variant or just a mistake in naming)
            y.append(digit if digit < 10 else 1)

X = np.array(X).reshape(-1, 28, 28, 1)
y = np.array(y)

# Use ImageDataGenerator for small dataset fine-tuning
datagen = ImageDataGenerator(
    rotation_range=15,
    zoom_range=0.15,
    width_shift_range=0.1,
    height_shift_range=0.1
)

# Lower learning rate for fine-tuning
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print(f"FINE-TUNING ON {len(X)} CUSTOM SAMPLES...")
model.fit(datagen.flow(X, y, batch_size=len(X)), epochs=20)

model.save("mnist_cnn_me.keras")
# Also copy to backend folder
import shutil
shutil.copy("mnist_cnn_me.keras", "backend/mnist_cnn_me.keras")

print("FINE-TUNE COMPLETE. MODEL UPDATED IN BACKEND.")
