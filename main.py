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

def wait_for_top_of_hour():
    """לולאה שבודקת כל שנייה מתי מתחילה השעה החדשה"""
    print("⏳ Waiting for the exact start of the next hour...")
    while True:
        # זמן ישראל
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        if now.minute == 0 and now.second == 0:
            print(f"⏰ IT'S TIME! Starting recordings at: {now.strftime('%H:%M:%S')}")
            break
        time.sleep(0.5) # בדיקה פעמיים בשנייה לדיוק מקסימלי

def record_stream(name, url):
    # הקלטה ל-60 דקות בדיוק (3600 שניות)
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
        subprocess.run(command, check=True, timeout=duration + 300)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 50000:
            print(f"✅ Finished: {file_name}")
        else:
            if os.path.exists(file_name): os.remove(file_name)
    except:
        if os.path.exists(file_name): os.remove(file_name)

def main():
    # בדיקת שבת (לפי יום ושעה בישראל)
    israel_now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    weekday = israel_now.weekday()
    if (weekday == 4 and israel_now.hour >= 16) or (weekday == 5 and israel_now.hour < 19):
        print("🕯️ Shabbat - Skipping")
        return

    # מנגנון ההמתנה לשנייה ה-0
    wait_for_top_of_hour()

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url))
        threads.append(t)
        t.start()
        time.sleep(2) # מרווח קצר כדי לא להעמיס את המעבד בבת אחת
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
