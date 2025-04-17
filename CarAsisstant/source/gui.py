from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QSize, QUrl, QTimer, QTime, QDateTime
import sys
import speech_recognition as sr
import google.generativeai as genai
from googleapiclient.discovery import build
import requests
from datetime import datetime

# API KEY cấu hình
GEMINI_API_KEY = "AIzaSyDfoZmVlF5PfdzWFRs2mlR2ccP62_2xOCc"
YOUTUBE_API_KEY = "AIzaSyAcYjwazHeg8QnvF52SfMgEW-v6P_akTUU"
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast?latitude=10.762622&longitude=106.660172&current_weather=true"

# Cấu hình Gemini
genai.configure(api_key=GEMINI_API_KEY)

def search_youtube_video(query):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(q=query, part='snippet', type='video', maxResults=1)
    response = request.execute()
    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        return video_id
    return None

class CarAssistantUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Car Assistant Python - Real-time GPS + Thời tiết + Giờ")
        self.setGeometry(100, 100, 1300, 750)
        self.setStyleSheet("background-color: black; color: white;")

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left panel
        left_panel = QVBoxLayout()

        # Notification area
        notif_frame = QFrame()
        notif_frame.setStyleSheet("background-color: #333333; border-radius: 10px;")
        notif_frame.setFixedHeight(120)
        notif_layout = QVBoxLayout()
        self.notif_label = QLabel("Chào mừng!\nNhấn 🎙️ để ra lệnh")
        self.notif_label.setStyleSheet("font-size: 18px;")
        notif_layout.addWidget(self.notif_label)
        notif_frame.setLayout(notif_layout)
        left_panel.addWidget(notif_frame)

        # Music area
        music_frame = QFrame()
        music_frame.setStyleSheet("background-color: #333333; border-radius: 10px;")
        music_frame.setFixedHeight(300)
        music_layout = QVBoxLayout()
        self.music_player_view = QWebEngineView()
        self.music_player_view.setFixedHeight(250)
        music_layout.addWidget(self.music_player_view)
        music_frame.setLayout(music_layout)
        left_panel.addWidget(music_frame)

        # Clock & Weather
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #333333; border-radius: 10px;")
        info_frame.setFixedHeight(100)
        info_layout = QVBoxLayout()

        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("font-size: 24px;")
        info_layout.addWidget(self.clock_label)

        self.weather_label = QLabel("Thời tiết: --")
        self.weather_label.setStyleSheet("font-size: 18px;")
        info_layout.addWidget(self.weather_label)

        info_frame.setLayout(info_layout)
        left_panel.addWidget(info_frame)

        left_panel.addStretch()

        # Bottom control bar
        bottom_controls = QHBoxLayout()
        for icon in ["🏠", "🔔"]:
            btn = QPushButton(icon)
            btn.setFixedSize(60, 60)
            bottom_controls.addWidget(btn)

        mic_button = QPushButton("🎙️")
        mic_button.setFixedSize(60, 60)
        mic_button.clicked.connect(self.handle_voice_command)
        bottom_controls.addWidget(mic_button)

        left_panel.addLayout(bottom_controls)

        # Map view
        self.map_view = QWebEngineView()
        self.map_view.load(QUrl.fromLocalFile(r'C:\Users\GIGABYTE\Desktop\CarAsisstant\source\map.html'))

        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.map_view, 2)

        # Timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(600000)  # update mỗi 10 phút
        self.update_weather()

    def listen_command(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.notif_label.setText("🎙️ Đang nghe...")
            QApplication.processEvents()
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio, language="vi-VN")
                return text
            except:
                return ""

    def process_command_with_gemini(self, command):
        try:
            model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
            response = model.generate_content(f"Tôi là trợ lý lái xe, hãy trả lời ngắn gọn bằng tiếng Việt: {command}")
            return response.text
        except Exception as e:
            print(e)
            return "⚠️ Không kết nối được AI."

    def handle_music_command(self, song_name):
        video_id = search_youtube_video(song_name)
        if video_id:
            html = f"""
            <html>
            <body style="margin:0; background:black;">
                <iframe width="100%" height="100%" 
                src="https://www.youtube-nocookie.com/embed/{video_id}?autoplay=1"
                frameborder="0"
                allow="autoplay; encrypted-media"
                allowfullscreen>
                </iframe>
            </body>
            </html>
            """
            self.music_player_view.setHtml(html)
            self.notif_label.setText(f"AI: Đang phát \"{song_name}\".")
        else:
            self.notif_label.setText("Không tìm thấy bài.")

    def handle_voice_command(self):
        command = self.listen_command()
        if command:
            if "phát bài" in command.lower():
                song_name = command.lower().replace("phát bài", "").strip()
                self.handle_music_command(song_name)
            elif "mấy giờ" in command.lower():
                current_time = QTime.currentTime().toString("HH:mm:ss")
                self.notif_label.setText(f"Bây giờ là {current_time}")
            elif "thời tiết" in command.lower():
                self.update_weather()
                self.notif_label.setText(f"{self.weather_label.text()}")
            else:
                result = self.process_command_with_gemini(command)
                self.notif_label.setText(f"AI: {result}")

    def update_clock(self):
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.clock_label.setText(f"🕒 {current_time}")

    def update_weather(self):
        try:
            response = requests.get(WEATHER_API_URL)
            data = response.json()
            temp = data['current_weather']['temperature']
            weather = data['current_weather']['weathercode']
            self.weather_label.setText(f"Thời tiết: {temp}°C, code: {weather}")
        except:
            self.weather_label.setText("Không lấy được thời tiết.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarAssistantUI()
    window.show()
    sys.exit(app.exec_())
