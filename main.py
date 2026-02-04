import os
import subprocess
import datetime
import requests
import threading
import time

# הלינקים המקוריים שלך - אלו שעבדו!
STREAMS = {
    "Kol_Chai": "https://cdn.livecast.co.il/radio-kolchai-mp3/stream",
    "Kol_Barama": "https://kbr.livecast.co.il/kolbarama-mp3/stream",
    "Kol_Chai_Music": "https://cdn.livecast.co.il/radio-music-mp3/stream",
    "Kol_Play": "http://live.streamgates.net/radio/kolplay/icecast.audio"
}

# זמן הקלטה - שעה (שנה ל-60 רק לבדיקה מהירה)
RECORD_DURATION = 3600 

def is_it_shabbat():
    """בודק שבת לפי שעון ישראל"""
    try:
        # פנייה ל-API לקבלת זמני שבת בירושלים
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
        print(f"Shabbat check failed: {e}")
        return False

def record_stream(name, url, duration):
    # שם הקובץ כולל תאריך ושעה בשעון ישראל (TZ מוגדר ב-YAML)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"--- Starting Parallel Recording: {name} ---")
    
    # פקודת FFmpeg הפשוטה שלך, הוספתי רק 'reconnect' קטן בגלל הבעיות בתמונות
    command = [
        'ffmpeg', '-y', 
        '-reconnect', '1', '-reconnect_at_eof', '1', '-reconnect_streamed', '1',
        '-i', url, 
        '-t', str(duration), 
        '-acodec', 'copy', 
        file_name
    ]
    
    try:
        subprocess.run(command, check=True, timeout=duration + 120)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 10000:
            print(f"✅ Created: {file_name}")
    except Exception as e:
        print(f"❌ Failed {name}: {e}")

def main():
    # בדיקת שבת - אם שבת, עוצרים הכל מיד
    if is_it_shabbat():
        print("🕯️ Shabbat mode active - recording skipped.")
        return

    threads = []
    for name, url in STREAMS.items():
        # הקלטה במקביל באמצעות תהליכונים
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
        time.sleep(2) # השהיה קלה כדי לא להעמיס את ה-IP של השרת
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
