import subprocess
import datetime
import threading
import requests
import time
import os

# יצירת תיקייה להקלטות
output_dir = "recordings"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

STREAMS = {
    "Kol_Chai": "https://cdn.livecast.co.il/radio-kolchai-mp3/stream",
    "Kol_Barama": "https://kbr.livecast.co.il/kolbarama-mp3/stream",
    "Kol_Chai_Music": "https://cdn.livecast.co.il/radio-music-mp3/stream",
    "Kol_Play": "http://live.streamgates.net/radio/kolplay/icecast.audio"
}

# משך הקלטה לבדיקה (שנה ל-3600 אחרי שתראה שזה עובד)
RECORD_DURATION = 60 

def is_it_shabbat():
    try:
        # בדיקה מול API של זמני שבת בירושלים
        response = requests.get("https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&m=50", timeout=15)
        data = response.json()
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        
        items = data['items']
        candle_lighting_str = next(item['date'] for item in items if item['category'] == 'candles')
        havdalah_str = next(item['date'] for item in items if item['category'] == 'havdalah')
        
        start_shabbat = datetime.datetime.fromisoformat(candle_lighting_str)
        end_shabbat = datetime.datetime.fromisoformat(havdalah_str)
        
        print(f"Current UTC: {now_utc}")
        print(f"Shabbat starts: {start_shabbat}")
        print(f"Shabbat ends: {end_shabbat}")
        
        if start_shabbat <= now_utc <= end_shabbat:
            return True
        return False
    except Exception as e:
        print(f"Shabbat check error: {e}")
        # גיבוי: יום שבת רגיל
        return datetime.datetime.now().weekday() == 5

def record_stream(name, url, duration):
    timestamp = datetime.datetime.now().strftime('%H-%M')
    file_name = os.path.join(output_dir, f"{name}_{timestamp}.mp3")
    
    # פקודה עם התחזות לדפדפן
    command = [
        'ffmpeg', '-y',
        '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        '-i', url, 
        '-t', str(duration), 
        '-acodec', 'copy', 
        file_name
    ]
    
    try:
        print(f"--- Starting recording: {name} ---")
        subprocess.run(command, check=True, timeout=duration + 300)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 1000:
            print(f"✅ Created: {file_name} ({os.path.getsize(file_name)} bytes)")
        else:
            print(f"⚠️ {name} finished but file is too small or missing.")
    except Exception as e:
        print(f"❌ Error with {name}: {e}")

def main():
    print("Starting process...")
    if is_it_shabbat():
        print("🕯️ SHABBAT DETECTED. Skipping recording to keep Shabbat.")
        return

    print("✅ NOT SHABBAT. Starting recordings...")
    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
        time.sleep(10) # דיליי למניעת חסימות
    
    for t in threads:
        t.join()
    print("--- All processes finished ---")

if __name__ == "__main__":
    main()
