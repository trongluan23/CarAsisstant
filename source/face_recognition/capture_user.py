from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt  # Import Qt để sử dụng AlignmentFlag
import sys
import os
import cv2

class CaptureUserGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chụp Khuôn Mặt Người Dùng")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #2c3e50; color: white;")

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout()

        # Title label
        title_label = QLabel("Nhập Tên Người Dùng")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ecf0f1;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Input field
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nhập tên người dùng...")
        self.name_input.setFont(QFont("Arial", 12))
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #3498db;
                border-radius: 10px;
                background-color: #34495e;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1abc9c;
            }
        """)
        layout.addWidget(self.name_input)

        # Capture button
        capture_button = QPushButton("Bắt Đầu Chụp")
        capture_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        capture_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 10px;
                background-color: #1abc9c;
                color: white;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """)
        capture_button.clicked.connect(self.start_capture)
        layout.addWidget(capture_button)

        # Set layout
        central_widget.setLayout(layout)

    def start_capture(self):
        user_name = self.name_input.text().strip()
        if not user_name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên người dùng!")
            return

        # Gọi hàm capture_images để chụp ảnh
        self.capture_images(user_name)

    def capture_images(self, user_name, count=30):
        save_path = f"train/dataset/{user_name}"
        os.makedirs(save_path, exist_ok=True)

        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        img_id = 0
        QMessageBox.information(self, "Thông báo", f"📸 Đang chụp ảnh cho {user_name}. Nhấn 'q' để thoát.")
        while True:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                img_id += 1
                face_img = gray[y:y+h, x:x+w]
                cv2.imwrite(f"{save_path}/{user_name}_{img_id}.jpg", face_img)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            cv2.imshow("Chụp khuôn mặt", frame)

            if img_id >= count or cv2.waitKey(10) == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
        QMessageBox.information(self, "Hoàn tất", "✅ Đã chụp xong.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CaptureUserGUI()
    window.show()
    sys.exit(app.exec())