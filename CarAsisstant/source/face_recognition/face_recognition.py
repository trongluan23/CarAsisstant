import cv2
import numpy as np
import os

def train_faces():
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    faces = []
    labels = []
    label_map = {}

    dataset_path = "face_recognition/dataset"
    label_id = 0

    for user_name in os.listdir(dataset_path):
        user_folder = os.path.join(dataset_path, user_name)
        if not os.path.isdir(user_folder):
            continue

        label_map[label_id] = user_name

        for img_name in os.listdir(user_folder):
            img_path = os.path.join(user_folder, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue

            faces.append(img)
            labels.append(label_id)

        label_id += 1

    if not faces:
        print("Chưa có dữ liệu khuôn mặt.")
        return

    face_recognizer.train(faces, np.array(labels))
    face_recognizer.save("face_recognition/trainer.yml")

    with open("face_recognition/labels.txt", "w") as f:
        for k, v in label_map.items():
            f.write(f"{k}:{v}\n")

    print("Huấn luyện xong.")

def recognize_face():
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.read("face_recognition/trainer.yml")

    labels = {}
    with open("face_recognition/labels.txt") as f:
        for line in f:
            k, v = line.strip().split(":")
            labels[int(k)] = v

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            label_id, confidence = face_recognizer.predict(face_roi)
            user_name = labels.get(label_id, "Người lạ")

            color = (0, 255, 0) if confidence < 70 else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, f"{user_name} ({confidence:.0f})", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Nhận diện khuôn mặt", frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

