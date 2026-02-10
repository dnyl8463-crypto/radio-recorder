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
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    weekday = now.weekday() # 4=שישי, 5=שבת
    if (weekday == 4 and now.hour >= 16) or (weekday == 5 and now.hour < 19):
        return True
    return False

def record_stream(name, url, duration):
    israel_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{israel_time}.mp3"
    
    command = [
        'ffmpeg', '-y',
        '-user_agent', 'Mozilla/5.0',
        '-i', url, '-t', str(duration),
        '-acodec', 'libmp3lame', '-ab', '128k', '-ar', '44100', file_name
    ]
    
    try:
        subprocess.run(command, check=True, timeout=duration + 300)
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

    # חישוב זמן ישראל נוכחי
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    
    # הגדרת היעד: השעה העגולה הבאה בדיוק
    target_end = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    
    # חישוב כמה שניות נשארו עד לשם
    duration = int((target_end - now).total_seconds())

    # אם נשארו יותר מ-60 דקות (בגלל שגיאת זמן) או פחות מ-2 דקות, נתקן ל-60 דקות מקסימום
    if duration > 3600: duration = 3600
    if duration < 120: 
        print("🕒 קרוב מדי לסוף השעה, מדלגים כדי למנוע כפילות")
        return

    print(f"🚀 מתחיל הקלטה של {duration} שניות עד לסוף השעה ({target_end.strftime('%H:%M:%S')})")

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
