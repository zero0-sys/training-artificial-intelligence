import os
import subprocess

def run(cmd):
    print(f"\n▶️ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

# 1️⃣ Train MNIST (kalau belum ada)
if not os.path.exists("mnist_cnn.keras"):
    run("python training/train_mnist.py")
else:
    print("MNIST model sudah ada, skip")

# 2️⃣ Fine-tune (kalau data ada)
if os.path.exists("training/my_digits"):
    run("python training/finetune_my_digits.py")
else:
    print("Tidak ada data tulisan, skip fine-tune")

# 3️⃣ Jalankan deteksi realtime
run("python detect_live.py")
