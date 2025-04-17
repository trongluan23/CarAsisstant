from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl, QTimer
import sys
import speech_recognition as sr
import google.generativeai as genai
from googleapiclient.discovery import build
from gtts import gTTS
import os
import uuid
import requests
from datetime import datetime
import pygame

# API KEY cấu hình
GEMINI_API_KEY = "AIzaSyDfoZmVlF5PfdzWFRs2mlR2ccP62_2xOCc"
YOUTUBE_API_KEY = "AIzaSyAcYjwazHeg8QnvF52SfMgEW-v6P_akTUU"

# Cấu hình Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Tìm video YouTube qua API
def search_youtube_video(query):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=1
    )
    response = request.execute()
    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        return video_id
    else:
        return None

# Đọc thông báo bằng giọng nói tiếng Việt
def speak(text):
    tts = gTTS(text=text, lang='vi')
    filename = f"voice_{uuid.uuid4()}.mp3"
    tts.save(filename)
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.quit()
    os.remove(filename)

# Lấy thông tin thời tiết qua Open-Meteo API
def get_weather():
    try:
        response = requests.get("https://api.open-meteo.com/v1/forecast?latitude=21.0285&longitude=105.8542&current_weather=true")
        data = response.json()
        temperature = data["current_weather"]["temperature"]
        windspeed = data["current_weather"]["windspeed"]
        weather_info = f"Nhiệt độ: {temperature}°C | Gió: {windspeed} km/h"
        return weather_info
    except:
        return "Không lấy được dữ liệu thời tiết."

class CarAssistantUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Car Assistant Python")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: black; color: white;")

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Left panel
        left_panel = QVBoxLayout()

        # Notification area
        self.notification_frame = QFrame()
        self.notification_frame.setStyleSheet("background-color: #333333; border-radius: 10px;")
        self.notification_frame.setFixedHeight(120)
        notif_layout = QVBoxLayout()
        self.notif_label = QLabel("Chào mừng!\nNhấn 🎙️ để ra lệnh")
        self.notif_label.setStyleSheet("font-size: 18px;")
        notif_layout.addWidget(self.notif_label)
        self.notification_frame.setLayout(notif_layout)
        left_panel.addWidget(self.notification_frame)

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

        # Time & weather label
        self.time_weather_label = QLabel()
        self.time_weather_label.setStyleSheet("font-size: 16px; padding: 10px;")
        left_panel.addWidget(self.time_weather_label)

        left_panel.addStretch()

        # Bottom control bar
        bottom_controls = QHBoxLayout()
        mic_button = QPushButton("🎙️")
        mic_button.setFixedSize(60, 60)
        mic_button.clicked.connect(self.handle_voice_command)
        bottom_controls.addWidget(mic_button)
        left_panel.addLayout(bottom_controls)

        # Map view (Google Maps gốc)
        self.map_view = QWebEngineView()
        self.map_view.setUrl(QUrl("https://www.google.com/maps"))

        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.map_view, 2)

        # Cập nhật thời gian & thời tiết mỗi phút
        self.update_time_weather()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time_weather)
        timer.start(60000)

    def update_time_weather(self):
        now = datetime.now().strftime("%H:%M")
        weather = get_weather()
        self.time_weather_label.setText(f"🕒 {now} | 🌤️ {weather}")

    # Nhận lệnh giọng nói
    def listen_command(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.notif_label.setText("🎙️ Đang nghe...")
            QApplication.processEvents()
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio, language="vi-VN")
                print(f"Bạn nói: {text}")
                return text
            except Exception as e:
                print(e)
                return ""

    # Gửi Gemini xử lý
    def process_command_with_gemini(self, command):
        try:
            model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
            response = model.generate_content(f"Tôi là trợ lý lái xe, hãy trả lời ngắn gọn bằng tiếng Việt: {command}")
            print("AI trả lời:", response.text)
            return response.text
        except Exception as e:
            print(e)
            return "Không kết nối được AI."

    # Xử lý phát nhạc
    def handle_music_command(self, song_name):
        video_id = search_youtube_video(song_name)
        if video_id:
            html = f"""
            <html>
            <body style="margin:0; background:black;">
                <iframe width="100%" height="100%"
                src="https://www.youtube.com/embed/{video_id}?autoplay=1"
                frameborder="0"
                allow="autoplay; encrypted-media"
                allowfullscreen>
                </iframe>
            </body>
            </html>
            """
            self.music_player_view.setHtml(html)
            self.notif_label.setText(f"Đang phát: {song_name}")
            speak(f"Đang phát bài {song_name}")
        else:
            self.notif_label.setText("Không tìm thấy bài hát.")
            speak("Không tìm thấy bài hát.")

    # Xử lý voice command
    def handle_voice_command(self):
        command = self.listen_command()
        if command:
            if "phát bài" in command.lower():
                song_name = command.lower().replace("phát bài", "").strip()
                self.handle_music_command(song_name)
            elif "mấy giờ" in command.lower():
                now = datetime.now().strftime("%H:%M")
                self.notif_label.setText(f"Bây giờ là {now}")
                speak(f"Bây giờ là {now}")
            elif "thời tiết" in command.lower():
                weather = get_weather()
                self.notif_label.setText(weather)
                speak(weather)
            else:
                result = self.process_command_with_gemini(command)
                self.notif_label.setText(f"AI: {result}")
                speak(result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarAssistantUI()
    window.show()
    sys.exit(app.exec())
