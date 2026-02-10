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
    # זמן ישראל
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    weekday = now.weekday() # 4=Friday, 5=Saturday
    if (weekday == 4 and now.hour >= 16) or (weekday == 5 and now.hour < 19):
        return True
    return False

def record_stream(name, url, duration):
    now_israel = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    file_name = f"{name}_{now_israel.strftime('%Y-%m-%d_%H-%M')}.mp3"
    
    command = [
        'ffmpeg', '-y',
        '-user_agent', 'Mozilla/5.0',
        '-i', url, '-t', str(duration),
        '-acodec', 'libmp3lame', '-ab', '128k', '-ar', '44100', file_name
    ]
    
    try:
        subprocess.run(command, check=True, timeout=duration + 120)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 50000:
            print(f"✅ הצלחנו: {file_name}")
        else:
            if os.path.exists(file_name): os.remove(file_name)
    except:
        if os.path.exists(file_name): os.remove(file_name)

def main():
    if is_it_shabbat():
        print("🕯️ שבת - מדלגים")
        return

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    
    # חישוב יעד: השעה העגולה הבאה
    target_end = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    duration = int((target_end - now).total_seconds())

    # הגנה: אם ה-Cron איחר מאוד ונשאר פחות מ-5 דקות, נקליט שעה שלמה מהרגע הזה
    if duration < 300:
        duration = 3600

    print(f"🚀 מתחיל הקלטה של {duration} שניות. נסיים ב-00:00.")

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, duration))
        threads.append(t)
        t.start()
        time.sleep(5)
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
