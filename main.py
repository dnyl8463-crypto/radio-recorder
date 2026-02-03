import subprocess
import datetime
import threading
import requests
import time
import os

STREAMS = {
    "Kol_Chai": "https://cdn.livecast.co.il/radio-kolchai-mp3/stream",
    "Kol_Barama": "https://kbr.livecast.co.il/kolbarama-mp3/stream",
    "Kol_Chai_Music": "https://cdn.livecast.co.il/radio-music-mp3/stream",
    "Kol_Play": "http://live.streamgates.net/radio/kolplay/icecast.audio"
}

# לבדיקה עכשיו: שנה ל-60. אחרי שתראה שזה עובד, תחזיר ל-3600.
RECORD_DURATION = 60 

def is_it_shabbat():
    try:
        response = requests.get("https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&m=50", timeout=15)
        data = response.json()
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        items = data['items']
        candle_lighting = next(item['date'] for item in items if item['category'] == 'candles')
        havdalah = next(item['date'] for item in items if item['category'] == 'havdalah')
        if datetime.datetime.fromisoformat(candle_lighting) <= now_utc <= datetime.datetime.fromisoformat(havdalah):
            return True
        return False
    except:
        return datetime.datetime.now().weekday() == 5

def record_stream(name, url, duration):
    timestamp = datetime.datetime.now().strftime('%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    # פקודה עם התחזות לדפדפן כדי למנוע חסימה
    command = [
        'ffmpeg', '-y',
        '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        '-i', url, 
        '-t', str(duration), 
        '-acodec', 'copy', 
        file_name
    ]
    
    try:
        print(f"--- Starting {name} ---")
        subprocess.run(command, check=True, timeout=duration + 300)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 1000:
            print(f"✅ Created: {file_name}")
        else:
            print(f"⚠️ {name} finished but file is empty.")
    except Exception as e:
        print(f"❌ Error with {name}: {e}")

def main():
    if is_it_shabbat():
        print("🕯️ Shabbat detected. Skipping.")
        return

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
        time.sleep(10) # דיליי של 10 שניות בין תחנה לתחנה
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
