import os
import subprocess
import datetime
import requests
import threading
import time

# הלינקים החדשים שנתת - נשתמש בהם כי הם הכי יציבים
STREAMS = {
    "Kol_Chai": "https://live.kcm.fm/live-new",
    "Kol_Barama": "https://cdn.cybercdn.live/Kol_Barama/Live_Audio/icecast.audio",
    "Kol_Chai_Music": "https://live.kcm.fm/livemusic",
    "Kol_Play": "https://cdn.cybercdn.live/Kol_Barama/Music/icecast.audio"
}

RECORD_DURATION = 3600 # שעה אחת

def is_it_shabbat():
    try:
        response = requests.get("https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&m=50", timeout=15)
        data = response.json()
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        items = data['items']
        start_shabbat = datetime.datetime.fromisoformat(next(item['date'] for item in items if item['category'] == 'candles'))
        end_shabbat = datetime.datetime.fromisoformat(next(item['date'] for item in items if item['category'] == 'havdalah'))
        return start_shabbat <= now_utc <= end_shabbat
    except:
        return False

def record_stream(name, url, duration):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"--- Starting parallel record: {name} ---")
    
    # פקודת FFmpeg עם הגדרות reconnect כדי לוודא ששאר התחנות לא יתנתקו
    command = [
        'ffmpeg', '-y',
        '-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '5',
        '-i', url,
        '-t', str(duration),
        '-acodec', 'copy',
        file_name
    ]
    
    try:
        # הקצאת זמן הקלטה + 5 דקות מרווח ביטחון
        subprocess.run(command, check=True, timeout=duration + 300)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 10000:
            print(f"✅ Created: {file_name}")
    except Exception as e:
        print(f"❌ Failed {name}: {e}")

def main():
    if is_it_shabbat():
        print("🕯️ Shabbat - Skipping recordings.")
        return

    print("✅ Not Shabbat. Starting all recordings in parallel...")
    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
        time.sleep(5) # השהייה קלה כדי שכל תחנה תתחבר בתורה ולא כולן בשנייה אחת
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
