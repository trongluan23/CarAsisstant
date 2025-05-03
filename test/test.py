import json
import os
import pygame

PLAYLIST_FILE = "music/user_playlists.json"

def play_youtube_audio(url):
    # Tải audio từ YouTube và phát bằng pygame
    os.system(f"yt-dlp -x --audio-format mp3 -o 'temp_audio.%(ext)s' {url}")
    pygame.mixer.init()
    pygame.mixer.music.load("temp_audio.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.quit()
    os.remove("temp_audio.mp3")

def add_to_playlist(user, song_title, video_url):
    if not os.path.exists(PLAYLIST_FILE):
        data = {}
    else:
        with open(PLAYLIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    if user not in data:
        data[user] = []

    data[user].append({
        "title": song_title,
        "url": video_url
    })

    with open(PLAYLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_user_playlist(user):
    if not os.path.exists(PLAYLIST_FILE):
        return []
    with open(PLAYLIST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(user, [])
