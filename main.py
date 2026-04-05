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

def record_stream(name, url, duration, label):
    israel_now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    file_name = f"{name}_{label}_{israel_now.strftime('%Y-%m-%d_%H-%M')}.mp3"
    
    command = [
        'ffmpeg', '-y',
        '-user_agent', 'Mozilla/5.0',
        '-i', url, '-t', str(duration),
        '-acodec', 'libmp3lame', '-ab', '128k', '-ar', '44100', file_name
    ]
    
    try:
        # זמן חריגה גדול יותר להקלטת לילה (חצי שעה אקסטרה)
        subprocess.run(command, check=True, timeout=duration + 1800)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 50000:
            print(f"✅ סיימנו הקלטה: {file_name}")
        else:
            if os.path.exists(file_name): os.remove(file_name)
    except Exception as e:
        if os.path.exists(file_name): os.remove(file_name)
        print(f"❌ שגיאה ב-{name}: {e}")

def main():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    hour = now.hour

    # אם השעה 23:00 (11 בלילה) - מקליטים 7 שעות עד 06:00
    if hour == 23:
        duration = 7 * 3600 # 25,200 שניות
        label = "Night_Full"
        print(f"🌙 מתחיל הקלטת לילה ארוכה (7 שעות) מ-23:00 עד 06:00")
    else:
        # בשאר השעות - מקליט שעה אחת רגילה עד סוף השעה
        target_end = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        duration = int((target_end - now).total_seconds())
        label = "Hourly"
        if duration < 300: return
        print(f"📻 הקלטה רגילה לשעה הקרובה: {duration} שניות")

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, duration, label))
        threads.append(t)
        t.start()
        time.sleep(10)
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
