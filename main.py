import os
import subprocess
import datetime
import requests
import threading
import time

# הלינקים שביקשת
STREAMS = {
    "Kol_Chai": "https://cdn.livecast.co.il/radio-kolchai-mp3/stream",
    "Kol_Barama": "https://kbr.livecast.co.il/kolbarama-mp3/stream",
    "Kol_Chai_Music": "https://cdn.livecast.co.il/radio-music-mp3/stream",
    "Kol_Play": "http://live.streamgates.net/radio/kolplay/icecast.audio"
}

RECORD_DURATION = 60 # דקה אחת

def is_it_shabbat():
    """בודק האם עכשיו שבת בירושלים"""
    try:
        # בדיקה מול Hebcal
        response = requests.get("https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&m=50", timeout=15)
        data = response.json()
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        
        items = data['items']
        candle_lighting = next(item['date'] for item in items if item['category'] == 'candles')
        havdalah = next(item['date'] for item in items if item['category'] == 'havdalah')
        
        start_shabbat = datetime.datetime.fromisoformat(candle_lighting)
        end_shabbat = datetime.datetime.fromisoformat(havdalah)
        
        return start_shabbat <= now_utc <= end_shabbat
    except:
        return datetime.datetime.now().weekday() == 5 # גיבוי ליום שבת

def record_stream(name, url, duration):
    # שימוש בשעון ישראל לשם הקובץ
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"--- Starting Parallel Recording: {name} ---")
    
    # פקודת FFmpeg משופרת עם 'reconnect' כדי למנוע את ה-Timeout שראינו בתמונה
    command = [
        'ffmpeg', '-y',
        '-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '10',
        '-i', url,
        '-t', str(duration),
        '-acodec', 'copy',
        file_name
    ]
    
    try:
        # הרצה עם הגדרת זמן מקסימלית כדי שלא ייתקע
        subprocess.run(command, check=True, timeout=duration + 120)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 10000:
            print(f"✅ Success: {file_name}")
    except Exception as e:
        print(f"❌ Failed {name}: {e}")

def main():
    if is_it_shabbat():
        print("🕯️ Shabbat detected. Skipping recordings.")
        return

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
        time.sleep(5) # השהייה קלה בין פתיחת החיבורים כדי למנוע חסימת ה-IP של GitHub
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
