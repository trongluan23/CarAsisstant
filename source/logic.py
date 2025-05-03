from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QInputDialog, QMessageBox, QSplitter
from PyQt6.QtGui import QIcon, QPixmap 
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
import json
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from pytube import YouTube
import tempfile
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
import subprocess
from face_recognition.face_recognition import recognize_user

# API KEY cấu hình
GEMINI_API_KEY = "AIzaSyDfoZmVlF5PfdzWFRs2mlR2ccP62_2xOCc"
YOUTUBE_API_KEY = "AIzaSyAcYjwazHeg8QnvF52SfMgEW-v6P_akTUU"
GOOGLE_MAPS_API_KEY = "AIzaSyDfoZmVlF5PfdzWFRs2mlR2ccP62_2xOCc"

# Cấu hình Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Tìm video YouTube qua API
def search_youtube_video(query):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=5
    )
    response = request.execute()
    return [item['id']['videoId'] for item in response['items']]

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

        self.user_name = recognize_user()  # Gọi nhận diện người dùng
        self.music_playlist = []  # Danh sách bài hát
        self.current_index = 0  # Chỉ số bài hát hiện tại
        self.current_song = None  # Bài hát hiện tại

        # Sử dụng QSplitter để chia giao diện
        splitter = QSplitter(self)
        splitter.setStyleSheet("background-color: black;")

        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Notification area
        self.notification_frame = QFrame()
        self.notification_frame.setStyleSheet("background-color: #333333; border-radius: 10px;")
        self.notification_frame.setFixedHeight(120) 
        notif_layout = QVBoxLayout()

        self.notif_label = QLabel(f"Chào mừng {self.user_name}!")
        self.notif_label.setStyleSheet("font-size: 18px; color: white;")
        self.notif_label.setWordWrap(True)  
        self.notif_label.setAlignment(Qt.AlignmentFlag.AlignTop)  
        self.notif_label.setFixedHeight(100)  
        notif_layout.addWidget(self.notif_label)

        self.notification_frame.setLayout(notif_layout)
        left_layout.addWidget(self.notification_frame)

        # Music area
        music_frame = QFrame()
        music_frame.setStyleSheet("background-color: #333333; border-radius: 10px;")
        music_frame.setFixedHeight(360)
        music_layout = QVBoxLayout()

        self.music_player_view = QWebEngineView()
        self.music_player_view.setFixedHeight(250)
        music_layout.addWidget(self.music_player_view)

        control_layout = QHBoxLayout()
        self.prev_button = QPushButton("⏮️")
        self.prev_button.clicked.connect(self.prev_song)
        self.pause_button = QPushButton("⏯️")
        self.pause_button.clicked.connect(self.pause_resume_song)
        self.next_button = QPushButton("⏭️")
        self.next_button.clicked.connect(self.next_song)
        control_layout.addWidget(self.prev_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.next_button)

        music_layout.addLayout(control_layout)
        music_frame.setLayout(music_layout)
        left_layout.addWidget(music_frame)

        # Time & weather label
        self.time_weather_label = QLabel()
        self.time_weather_label.setStyleSheet("font-size: 16px; padding: 10px;")
        left_layout.addWidget(self.time_weather_label)

        left_layout.addStretch()

        # Bottom control bar
        bottom_controls = QHBoxLayout()
        mic_button = QPushButton("🎙️")
        mic_button.setFixedSize(60, 60)
        mic_button.clicked.connect(self.handle_voice_command)
        bottom_controls.addWidget(mic_button)

        add_user_button = QPushButton("➕")
        add_user_button.setFixedSize(60, 60)
        add_user_button.clicked.connect(self.add_new_user)
        bottom_controls.addWidget(add_user_button)

        select_song_button = QPushButton("🎵")
        select_song_button.setFixedSize(60, 60)
        select_song_button.clicked.connect(self.select_song)
        bottom_controls.addWidget(select_song_button)

        show_locations_button = QPushButton("📍")
        show_locations_button.setFixedSize(60, 60)
        show_locations_button.clicked.connect(self.show_saved_locations)
        bottom_controls.addWidget(show_locations_button)

        switch_user_button = QPushButton("🔄")
        switch_user_button.setFixedSize(60, 60)
        switch_user_button.clicked.connect(self.switch_user)
        bottom_controls.addWidget(switch_user_button)

        left_layout.addLayout(bottom_controls)

        # Add left panel to splitter
        splitter.addWidget(left_panel)

        # Map view (Google Maps gốc)
        self.map_view = QWebEngineView()
        self.map_view.setUrl(QUrl("https://www.google.com/maps"))
        self.map_view.setFixedWidth(600) 
        splitter.addWidget(self.map_view)

        # Đặt tỷ lệ cố định cho splitter
        splitter.setSizes([600, 600])  
        splitter.setStretchFactor(0, 0) 
        splitter.setStretchFactor(1, 1)  

        # Đặt splitter làm layout chính
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(splitter)

        # Cập nhật thời gian & thời tiết mỗi phút
        self.update_time_weather()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time_weather)
        timer.start(60000)

        # Cập nhật dữ liệu người dùng
        self.update_user_data()

    def update_time_weather(self):
        now = datetime.now().strftime("%H:%M")
        weather = get_weather()
        self.time_weather_label.setText(f"🕒 {now} | 🌤️ {weather}")

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

    def listen_for_name(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.notif_label.setText("🎙️ Đang nghe tên người dùng...")
            QApplication.processEvents()
            try:
                audio = recognizer.listen(source, timeout=5)
                name = recognizer.recognize_google(audio, language="vi-VN")
                print(f"Tên người dùng được nhận: {name}")
                return name
            except Exception as e:
                print(f"Lỗi khi nhận diện tên: {e}")
                return ""

    def process_command_with_gemini(self, command):
        try:
            model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
            response = model.generate_content(f"Tôi là trợ lý lái xe, người dùng là {self.user_name}. Hãy trả lời ngắn gọn bằng tiếng Việt: {command}")
            print("AI trả lời:", response.text)
            return response.text
        except Exception as e:
            print(e)
            return "Không kết nối được AI."
        
    def play_song_at_index(self, index):
        if 0 <= index < len(self.music_playlist):
            video_id = self.music_playlist[index]
            html = f"""
            <html><body style="margin:0; background:black;">
            <iframe width="100%" height="100%"
            src="https://www.youtube.com/embed/{video_id}?autoplay=1"
            frameborder="0" allow="autoplay; encrypted-media" allowfullscreen>
            </iframe></body></html>
            """
            self.music_player_view.setHtml(html)

    def handle_music_command(self, song_name):
        video_ids = search_youtube_video(song_name)
        if video_ids:
            self.music_playlist = video_ids
            self.current_index = 0
            self.play_song_at_index(self.current_index)
            self.notif_label.setText(f"Đang phát: {song_name}")
            speak(f"Đang phát bài {song_name}")
            
          
            try:
                youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
                request = youtube.search().list(
                    q=song_name,
                    part='snippet',
                    type='video',
                    maxResults=1
                )
                response = request.execute()
                video_info = response['items'][0]
                title = video_info['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_info['id']['videoId']}"

                data = {"title": title, "video_url": video_url}

                # Tải JSON hiện tại
                try:
                    with open("playlist.json", "r", encoding="utf-8") as f:
                        playlist = json.load(f)
                except (FileNotFoundError, json.decoder.JSONDecodeError):
                    playlist = {} 

                # Kiểm tra nếu người dùng đã có playlist
                if self.user_name not in playlist:
                    playlist[self.user_name] = []

                # Thêm bài hát vào playlist của người dùng
                playlist[self.user_name].append(data)

                # Lưu lại playlist vào file JSON
                with open("playlist.json", "w", encoding="utf-8") as f:
                    json.dump(playlist, f, ensure_ascii=False, indent=4)

                print(f"Đã lưu bài hát '{title}' vào playlist của {self.user_name}.")

            except Exception as e:
                print("Lỗi lưu JSON:", e)


    
    def pause_resume_song(self):
        self.music_player_view.page().runJavaScript("document.querySelector('video')?.paused ? document.querySelector('video')?.play() : document.querySelector('video')?.pause();")

    def next_song(self):
        if self.current_index + 1 < len(self.music_playlist):
            self.current_index += 1
            self.play_song_at_index(self.current_index)

    def prev_song(self):
        if self.current_index - 1 >= 0:
            self.current_index -= 1
            self.play_song_at_index(self.current_index)

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
            elif "thêm người dùng" in command.lower():
                self.add_new_user()
            elif "phát danh sách nhạc" in command.lower():
                self.select_song()
            elif "đến" in command or "chỉ đường" in command or "tìm" in command:
                parts = command.split("đến")
                if len(parts) > 1:
                    destination = parts[1].strip()
                    self.save_location(destination)  
                    url = f"https://www.google.com/maps/dir/?api=1&destination={destination.replace(' ', '+')}"
                    self.map_view.setUrl(QUrl(url))
                    self.notif_label.setText(f"📍 Đang chỉ đường đến: {destination}")
                    speak(f"Đang chỉ đường đến {destination}")
            elif "danh sách địa điểm" in command.lower():
                self.show_saved_locations()
            elif "chuyển đổi người dùng" in command.lower():
                self.switch_user()
            else:
                result = self.process_command_with_gemini(command)
                self.notif_label.setText(f"AI: {result}")
                speak(result)

    def add_new_user(self):

        subprocess.call(["python", r"C:\Users\GIGABYTE\Desktop\CarAsisstant\source\face_recognition\capture_user.py"])
        subprocess.call(["python", r"C:\Users\GIGABYTE\Desktop\CarAsisstant\source\face_recognition\train_model.py"])

        self.notif_label.setText(f"✅ Đã thêm người dùng")
        speak(f"Đã thêm người dùng ")
        self.user_name = recognize_user()
        self.notif_label.setText(f"Chào mừng {self.user_name}!")
        speak(f"Chào mừng {self.user_name}!")
        
    def select_song(self):
        try:
            # Đọc file JSON chứa danh sách nhạc
            with open("playlist.json", "r", encoding="utf-8") as f:
                playlist = json.load(f)

            # Kiểm tra nếu user_name có trong danh sách
            if self.user_name in playlist:
                user_playlist = playlist[self.user_name]
                if user_playlist:
                    # Tạo danh sách bài hát để chọn
                    song_titles = [song['title'] for song in user_playlist]
                    song, ok = QInputDialog.getItem(self, "Chọn bài hát", "Danh sách bài hát:", song_titles, 0, False)
                    if ok and song:
                        # Tìm URL của bài hát được chọn
                        for song_data in user_playlist:
                            if song_data['title'] == song:
                                video_url = song_data['video_url']
                                self.play_song_by_url(video_url, song)
                                break
                else:
                    QMessageBox.information(self, "Danh sách nhạc", f"{self.user_name} chưa có bài hát nào trong danh sách.")
            else:
                QMessageBox.information(self, "Danh sách nhạc", f"{self.user_name} chưa có bài hát nào trong danh sách.")
        except FileNotFoundError:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy file danh sách nhạc.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {e}")

    def play_song_by_url(self, video_url, song_title):
        video_id = video_url.split("v=")[-1]
        html = f"""
        <html><body style="margin:0; background:black;">
        <iframe width="100%" height="100%"
        src="https://www.youtube.com/embed/{video_id}?autoplay=1"
        frameborder="0" allow="autoplay; encrypted-media" allowfullscreen>
        </iframe></body></html>
        """
        self.music_player_view.setHtml(html)
        self.notif_label.setText(f"🎵 Đang phát: {song_title}")
        speak(f"Đang phát bài {song_title}")

    def save_location(self, location_name):
        try:
            
            data = {"name": location_name, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            
            try:
                with open("locations.json", "r", encoding="utf-8") as f:
                    locations = json.load(f)
            except (FileNotFoundError, json.decoder.JSONDecodeError):
                locations = {}  

            
            if self.user_name not in locations:
                locations[self.user_name] = []

            
            locations[self.user_name].append(data)

            
            with open("locations.json", "w", encoding="utf-8") as f:
                json.dump(locations, f, ensure_ascii=False, indent=4)

            print(f"Đã lưu địa điểm '{location_name}' vào danh sách của {self.user_name}.")
        except Exception as e:
            print(f"Lỗi khi lưu địa điểm: {e}")

    def show_saved_locations(self):
        try:
           
            with open("locations.json", "r", encoding="utf-8") as f:
                locations = json.load(f)

            
            if self.user_name in locations:
                user_locations = locations[self.user_name]
                if user_locations:
                    
                    locations_text = "\n".join([f"{i+1}. {loc['name']} (Lưu lúc: {loc['timestamp']})" for i, loc in enumerate(user_locations)])
                    QMessageBox.information(self, "Danh sách địa điểm", f"Các địa điểm đã lưu của {self.user_name}:\n\n{locations_text}")
                else:
                    QMessageBox.information(self, "Danh sách địa điểm", f"{self.user_name} chưa có địa điểm nào trong danh sách.")
            else:
                QMessageBox.information(self, "Danh sách địa điểm", f"{self.user_name} chưa có địa điểm nào trong danh sách.")
        except FileNotFoundError:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy file danh sách địa điểm.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {e}")

    def save_address(self, address):
        try:
            
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address.replace(' ', '+')}&key={GOOGLE_MAPS_API_KEY}"
            response = requests.get(url)
            data = response.json()

            if data["status"] == "OK":
                # Lấy thông tin địa chỉ chi tiết
                formatted_address = data["results"][0]["formatted_address"]
                location = data["results"][0]["geometry"]["location"]
                lat, lng = location["lat"], location["lng"]

                # Tạo dữ liệu địa chỉ
                address_data = {
                    "name": formatted_address,
                    "latitude": lat,
                    "longitude": lng,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

               
                try:
                    with open("locations.json", "r", encoding="utf-8") as f:
                        locations = json.load(f)
                except (FileNotFoundError, json.decoder.JSONDecodeError):
                    locations = {}  # Khởi tạo nếu file không tồn tại hoặc bị lỗi

               
                if self.user_name not in locations:
                    locations[self.user_name] = []

                
                locations[self.user_name].append(address_data)

                # Lưu lại danh sách vào file JSON
                with open("locations.json", "w", encoding="utf-8") as f:
                    json.dump(locations, f, ensure_ascii=False, indent=4)

                self.notif_label.setText(f"✅ Đã lưu địa chỉ: {formatted_address}")
                speak(f"Đã lưu địa chỉ {formatted_address}")
            else:
                self.notif_label.setText("❌ Không tìm thấy địa chỉ.")
                speak("Không tìm thấy địa chỉ.")
        except Exception as e:
            self.notif_label.setText("❌ Lỗi khi lưu địa chỉ.")
            print(f"Lỗi khi lưu địa chỉ: {e}")

    def switch_user(self):
        
        options = ["Nhập tên", "Nhận diện giọng nói"]
        option, ok = QInputDialog.getItem(self, "Chuyển đổi người dùng", "Chọn cách chuyển đổi:", options, 0, False)

        if ok and option:
            if option == "Nhập tên":
                
                name, ok = QInputDialog.getText(self, "Nhập tên người dùng", "Tên người dùng:")
                if ok and name.strip():
                    self.user_name = name.strip()
                    self.notif_label.setText(f"Chào mừng {self.user_name}!")
                    speak(f"Chào mừng {self.user_name}!")
            elif option == "Nhận diện giọng nói":
                
                name = self.listen_for_name()
                if name:
                    self.user_name = name
                    self.notif_label.setText(f"Chào mừng {self.user_name}!")
                    speak(f"Chào mừng {self.user_name}!")
                else:
                    QMessageBox.warning(self, "Lỗi", "Không nhận diện được tên người dùng.")

    def update_user_data(self):
        
        self.notif_label.setText(f"Chào mừng {self.user_name}!")

        
        try:
            with open("playlist.json", "r", encoding="utf-8") as f:
                playlist = json.load(f)
            if self.user_name in playlist:
                self.music_playlist = playlist[self.user_name]
            else:
                self.music_playlist = []
        except FileNotFoundError:
            self.music_playlist = []

        
        try:
            with open("locations.json", "r", encoding="utf-8") as f:
                locations = json.load(f)
            if self.user_name in locations:
                self.saved_locations = locations[self.user_name]
            else:
                self.saved_locations = []
        except FileNotFoundError:
            self.saved_locations = []

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarAssistantUI()
    window.show()
    sys.exit(app.exec())
