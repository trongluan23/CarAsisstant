import cv2
import os
import numpy as np

def train_face_model():
    dataset_path = f"train/dataset"
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces = []
    labels = []

    for i, name in enumerate(os.listdir(dataset_path)):
        person_path = os.path.join(dataset_path, name)
        for img_name in os.listdir(person_path):
            img_path = os.path.join(person_path, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            faces.append(img)
            labels.append(i)

    recognizer.train(faces, np.array(labels))
    recognizer.save(r"C:\Users\GIGABYTE\Desktop\CarAsisstant\train\trainer.yml")
    print("✅ Đã train xong model khuôn mặt")

if __name__ == "__main__":
    train_face_model()
