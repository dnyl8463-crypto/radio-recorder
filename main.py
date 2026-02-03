import subprocess
import datetime
import threading
import requests
import time # הוספנו ספריית זמן

STREAMS = {
    "Kol_Chai": "https://cdn.livecast.co.il/radio-kolchai-mp3/stream",
    "Kol_Barama": "https://kbr.livecast.co.il/kolbarama-mp3/stream",
    "Kol_Chai_Music": "https://cdn.livecast.co.il/radio-music-mp3/stream",
    "Kol_Play": "http://live.streamgates.net/radio/kolplay/icecast.audio"
}

# נסה לשנות ל-60 רק לבדיקה אחת, ואז תחזיר ל-3600
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
    
    # פקודה חזקה יותר עם reconnect וזמני המתנה
    command = [
        'ffmpeg', '-y',
        '-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '20',
        '-i', url, '-t', str(duration), '-acodec', 'copy', file_name
    ]
    
    try:
        print(f"--- Attempting to connect to {name} ---")
        subprocess.run(command, check=True, timeout=duration + 300)
        print(f"✅ Success: {file_name}")
    except Exception as e:
        print(f"❌ Failed {name}: {e}")

def main():
    if is_it_shabbat():
        print("🕯️ Shabbat detected. Skipping.")
        return

    threads = []
    for name, url in STREAMS.items():
        # הפעלת כל הקלטה בהפרש של 10 שניות מהקודמת
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
        print(f"Waiting 10 seconds before next station...")
        time.sleep(10) 
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
