import os
import subprocess
import datetime
import requests
import threading
import time

# הלינקים החדשים והמעודכנים ששלחת
STREAMS = {
    "Kol_Chai": "https://live.kcm.fm/live-new",
    "Kol_Barama": "https://cdn.cybercdn.live/Kol_Barama/Live_Audio/icecast.audio",
    "Kol_Chai_Music": "https://live.kcm.fm/livemusic",
    "Kol_Play": "https://cdn.cybercdn.live/Kol_Barama/Music/icecast.audio"
}

# משך הקלטה (שנה ל-60 רק לבדיקה מהירה, ואז ל-3600 לשעה שלמה)
RECORD_DURATION = 60 

def is_it_shabbat():
    """בודק האם עכשיו שבת בירושלים"""
    try:
        response = requests.get("https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&m=50", timeout=15)
        data = response.json()
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        
        items = data['items']
        candle_lighting = next(item['date'] for item in items if item['category'] == 'candles')
        havdalah = next(item['date'] for item in items if item['category'] == 'havdalah')
        
        start_shabbat = datetime.datetime.fromisoformat(candle_lighting)
        end_shabbat = datetime.datetime.fromisoformat(havdalah)
        
        return start_shabbat <= now_utc <= end_shabbat
    except Exception as e:
        print(f"Shabbat check error: {e}")
        return False

def record_stream(name, url, duration):
    # שם הקובץ (השעה תהיה לפי ה-TZ שמוגדר ב-YAML)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"--- Starting Parallel Recording: {name} ---")
    
    # פקודת FFmpeg אמינה עם הגדרות reconnect למקרה של ניתוק
    command = [
        'ffmpeg', '-y',
        '-reconnect', '1', '-reconnect_at_eof', '1', '-reconnect_streamed', '1',
        '-i', url, 
        '-t', str(duration), 
        '-acodec', 'copy', 
        file_name
    ]
    
    try:
        subprocess.run(command, check=True, timeout=duration + 300)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 10000:
            print(f"✅ Created: {file_name}")
    except Exception as e:
        print(f"❌ Failed {name}: {e}")

def main():
    print(f"Current time: {datetime.datetime.now()}")
    
    if is_it_shabbat():
        print("🕯️ SHABBAT DETECTED. Recording skipped.")
        return

    print("✅ NOT SHABBAT. Starting parallel recordings...")
    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
        time.sleep(2) # השהייה קלה כדי לא להעמיס על ה-IP של השרת
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
