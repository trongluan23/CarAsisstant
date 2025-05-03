import cv2
import os

def recognize_user():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("train/trainer.yml")

    labels = {}
    for i, name in enumerate(os.listdir('train/dataset')):
        labels[i] = name
    print("Labels:", labels)  # Debugging: Print the labels dictionary

    cap = cv2.VideoCapture(0)
    recognized_name = "Tài xế "

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            id_, conf = recognizer.predict(gray[y:y+h, x:x+w])
            if conf < 70:
                recognized_name = labels.get(id_, "Tài xế")  # Avoid KeyError
                cap.release()
                return recognized_name

        cv2.imshow("Đang nhận diện khuôn mặt...", frame)
        if cv2.waitKey(10) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return recognized_name

if __name__ == "__main__":
    name = recognize_user()
    print(f"Người dùng được nhận diện: {name}")
    print("Người dùng không được nhận diện.")
