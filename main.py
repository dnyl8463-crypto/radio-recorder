import os
import subprocess
import datetime
import threading
import requests

STREAMS = {
    "Kol_Chai": "https://cdn.livecast.co.il/radio-kolchai-mp3/stream",
    "Kol_Barama": "https://kbr.livecast.co.il/kolbarama-mp3/stream",
    "Kol_Chai_Music": "https://cdn.livecast.co.il/radio-music-mp3/stream",
    "Kol_Play": "http://live.streamgates.net/radio/kolplay/icecast.audio"
}

RECORD_DURATION = 3600 

def is_it_shabbat():
    try:
        # פנייה ל-API של Hebcal לקבלת זמני שבת בירושלים
        response = requests.get("https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&m=50", timeout=10)
        data = response.json()
        
        # זמן נוכחי ב-UTC (ככה ה-API מחזיר נתונים)
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        
        items = data['items']
        # מוצאים את הדלקת נרות והבדלה
        candle_lighting_str = next(item['date'] for item in items if item['category'] == 'candles')
        havdalah_str = next(item['date'] for item in items if item['category'] == 'havdalah')
        
        # המרה לאובייקט זמן של פייתון
        start_shabbat = datetime.datetime.fromisoformat(candle_lighting_str)
        end_shabbat = datetime.datetime.fromisoformat(havdalah_str)
        
        if start_shabbat <= now_utc <= end_shabbat:
            return True
        return False
    except Exception as e:
        print(f"Error checking Shabbat: {e}")
        # גיבוי: אם ה-API נפל, בודקים אם היום יום שבת (יום 5 במערכת)
        return datetime.datetime.now().weekday() == 5

def record_stream(name, url, duration):
    timestamp = datetime.datetime.now().strftime('%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    command = ['ffmpeg', '-y', '-i', url, '-t', str(duration), '-acodec', 'copy', file_name]
    try:
        subprocess.run(command, check=True)
        print(f"✅ Finished: {file_name}")
    except Exception as e:
        print(f"❌ Error recording {name}: {e}")

def main():
    if is_it_shabbat():
        print("🕯️ Shabbat/Chag detected. Exiting without recording.")
        return

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
