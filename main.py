import os
import subprocess
import datetime
import requests
import threading
import time

STREAMS = {
    "Kol_Chai": "https://cdn.livecast.co.il/radio-kolchai-mp3/stream",
    "Kol_Barama": "https://kbr.livecast.co.il/kolbarama-mp3/stream",
    "Kol_Chai_Music": "https://cdn.livecast.co.il/radio-music-mp3/stream",
    "Kol_Play": "http://live.streamgates.net/radio/kolplay/icecast.audio"
}

RECORD_DURATION = 60 

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
    
    # פקודה משופרת: הוספנו timeout של 30 שניות לחיבור וזהות דפדפן
    command = [
        'ffmpeg', '-y',
        '-timeout', '30000000', # 30 שניות המתנה לחיבור
        '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        '-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '5',
        '-i', url,
        '-t', str(duration),
        '-acodec', 'copy',
        file_name
    ]
    
    try:
        print(f"--- Trying to connect to {name}... ---")
        # שימוש ב-wait במקום run כדי לתת לזה לרוץ בשקט
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            process.wait(timeout=duration + 120)
            if os.path.exists(file_name) and os.path.getsize(file_name) > 5000:
                print(f"✅ Created: {file_name}")
            else:
                print(f"⚠️ {name} finished but file is missing or too small.")
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"❌ {name} timed out.")
    except Exception as e:
        print(f"❌ Error with {name}: {e}")

def main():
    if is_it_shabbat():
        print("🕯️ Shabbat - skipping.")
        return

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
        time.sleep(10) # חשוב! השהייה בין פתיחת חיבורים כדי שהשרת לא יחסום אותנו
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
