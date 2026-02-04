import os
import subprocess
import datetime
import requests
import threading
import time

# הלינקים שציינת שעבדו לך
STREAMS = {
    "Kol_Chai": "https://cdn.livecast.co.il/radio-kolchai-mp3/stream",
    "Kol_Barama": "https://kbr.livecast.co.il/kolbarama-mp3/stream",
    "Kol_Chai_Music": "https://cdn.livecast.co.il/radio-music-mp3/stream",
    "Kol_Play": "http://live.streamgates.net/radio/kolplay/icecast.audio"
}

RECORD_DURATION = 60 # שעה אחת (שנה ל-60 רק לבדיקה אם תרצה)

def is_it_shabbat():
    """בודק האם עכשיו שבת בירושלים"""
    try:
        # פנייה ל-API של Hebcal לקבלת זמני שבת
        response = requests.get("https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&m=50", timeout=10)
        data = response.json()
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        
        items = data['items']
        candle_lighting = next(item['date'] for item in items if item['category'] == 'candles')
        havdalah = next(item['date'] for item in items if item['category'] == 'havdalah')
        
        start_shabbat = datetime.datetime.fromisoformat(candle_lighting)
        end_shabbat = datetime.datetime.fromisoformat(havdalah)
        
        return start_shabbat <= now_utc <= end_shabbat
    except Exception as e:
        print(f"Shabbat check failed, skipping: {e}")
        return False

def record_stream(name, url, duration):
    # הגדרת שם הקובץ עם תאריך ושעה בשעון ישראל
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"--- Starting Parallel Recording: {name} ---")
    
    command = [
        'ffmpeg', '-y', '-i', url, '-t', str(duration), '-acodec', 'copy', file_name
    ]
    
    try:
        subprocess.run(command, check=True, timeout=duration + 60)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 10000:
            print(f"✅ Created: {file_name}")
    except Exception as e:
        print(f"❌ Failed {name}: {e}")

def main():
    # בדיקת שבת - אם שבת, עוצרים הכל
    if is_it_shabbat():
        print("🕯️ Shabbat detected. Recording cancelled.")
        return

    threads = []
    for name, url in STREAMS.items():
        # הפעלה במקביל של כל התחנות
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
        time.sleep(1) # השהייה קלה כדי לא להעמיס על המעבד בשנייה אחת
    
    # מחכים שכל ההקלטות יסתיימו
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
