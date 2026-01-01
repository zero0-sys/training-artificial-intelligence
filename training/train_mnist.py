import tensorflow as tf
from tensorflow.keras import layers, models

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

x_train = x_train[:10000] / 255.0
y_train = y_train[:10000]
x_test  = x_test[:2000] / 255.0
y_test  = y_test[:2000]

x_train = x_train.reshape(-1,28,28,1)
x_test  = x_test.reshape(-1,28,28,1)

model = models.Sequential([
    layers.Conv2D(16,(3,3),activation='relu',input_shape=(28,28,1)),
    layers.MaxPooling2D(2,2),
    layers.Flatten(),
    layers.Dense(32,activation='relu'),
    layers.Dense(10,activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(x_train,y_train,epochs=2,validation_data=(x_test,y_test))
model.save("mnist_cnn.keras")

print("MNIST TRAINING SELESAI")
