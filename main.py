import os
import subprocess
import datetime
import requests
import threading
import time

# הלינקים הכי מעודכנים ששלחת
STREAMS = {
    "Kol_Chai": "https://live.kcm.fm/live-new",
    "Kol_Barama": "https://cdn.cybercdn.live/Kol_Barama/Live_Audio/icecast.audio",
    "Kol_Chai_Music": "https://live.kcm.fm/livemusic",
    "Kol_Play": "https://cdn.cybercdn.live/Kol_Barama/Music/icecast.audio"
}

RECORD_DURATION = 3600 # שעה אחת

def is_it_shabbat():
    try:
        r = requests.get("https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&m=50", timeout=15)
        data = r.json()
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        items = data['items']
        start = datetime.datetime.fromisoformat(next(i['date'] for i in items if i['category'] == 'candles'))
        end = datetime.datetime.fromisoformat(next(i['date'] for i in items if i['category'] == 'havdalah'))
        return start <= now_utc <= end
    except:
        return False

def record_stream(name, url, duration):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"--- Launching parallel recording for {name} ---")
    
    # פקודת FFmpeg משופרת עם הגדרות עקיפת חסימה
    command = [
        'ffmpeg', '-y',
        '-timeout', '30000000', # המתנה של 30 שניות לחיבור ראשוני
        '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        '-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '10',
        '-i', url,
        '-t', str(duration),
        '-acodec', 'copy',
        file_name
    ]
    
    try:
        # הרצה עם מרווח ביטחון של 5 דקות
        subprocess.run(command, check=True, timeout=duration + 300)
        
        if os.path.exists(file_name) and os.path.getsize(file_name) > 1000:
            print(f"✅ Created: {file_name} ({os.path.getsize(file_name)} bytes)")
        else:
            if os.path.exists(file_name): os.remove(file_name)
            print(f"⚠️ {name} failed: Stream provided no data")
    except Exception as e:
        print(f"❌ {name} error: {e}")

def main():
    if is_it_shabbat():
        print("🕯️ Shabbat - Skipping")
        return

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
        # המתנה של 7 שניות בין תחנה לתחנה כדי לא לעורר את הגנות השרתים
        time.sleep(7) 
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
