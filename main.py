import os
import subprocess
import datetime
import threading
import time

STREAMS = {
    "Kol_Chai": "https://live.kcm.fm/live-new",
    "Kol_Barama": "https://cdn.cybercdn.live/Kol_Barama/Live_Audio/icecast.audio",
    "Kol_Chai_Music": "https://live.kcm.fm/livemusic",
    "Kol_Play": "https://cdn.cybercdn.live/Kol_Barama/Music/icecast.audio"
}

def is_it_shabbat():
    # בדיקה פשוטה לפי יום ושעה (זמן ישראל)
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    weekday = now.weekday() # 4=Friday, 5=Saturday
    if (weekday == 4 and now.hour >= 16) or (weekday == 5 and now.hour < 19):
        return True
    return False

def record_stream(name, url):
    # הקלטה ל-60 דקות (3600 שניות)
    duration = 3600
    israel_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{israel_time}.mp3"
    
    command = [
        'ffmpeg', '-y',
        '-user_agent', 'Mozilla/5.0',
        '-i', url, '-t', str(duration),
        '-acodec', 'libmp3lame', '-ab', '128k', '-ar', '44100', file_name
    ]
    
    try:
        # הרצה עם חריגת זמן לביטחון
        subprocess.run(command, check=True, timeout=duration + 300)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 50000:
            print(f"✅ Success: {file_name}")
        else:
            if os.path.exists(file_name): os.remove(file_name)
    except:
        if os.path.exists(file_name): os.remove(file_name)

def main():
    if is_it_shabbat():
        print("🕯️ Shabbat - Skipping")
        return

    print(f"🚀 Starting 60-minute recording session...")

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url))
        threads.append(t)
        t.start()
        time.sleep(5) # מרווח קצר למניעת עומס
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
