import os
import subprocess
import datetime
import requests
import threading
import time

STREAMS = {
    "Kol_Chai": "https://live.kcm.fm/live-new",
    "Kol_Barama": "https://cdn.cybercdn.live/Kol_Barama/Live_Audio/icecast.audio",
    "Kol_Chai_Music": "https://live.kcm.fm/livemusic",
    "Kol_Play": "https://cdn.cybercdn.live/Kol_Barama/Music/icecast.audio"
}

def is_it_shabbat():
    try:
        r = requests.get("https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&m=50", timeout=10)
        data = r.json()
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        items = data['items']
        start = datetime.datetime.fromisoformat(next(i['date'] for i in items if i['category'] == 'candles'))
        end = datetime.datetime.fromisoformat(next(i['date'] for i in items if i['category'] == 'havdalah'))
        return start <= now_utc <= end
    except:
        return False

def record_stream(name, url, duration):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    command = [
        'ffmpeg', '-y',
        '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        '-i', url,
        '-t', str(duration),
        '-acodec', 'libmp3lame',
        '-ab', '128k',
        '-ar', '44100',
        file_name
    ]
    
    try:
        # הרצה עם הגנה
        subprocess.run(command, check=True, timeout=duration + 120)
        
        if os.path.exists(file_name) and os.path.getsize(file_name) > 50000:
            print(f"✅ Success: {file_name}")
        else:
            if os.path.exists(file_name): os.remove(file_name)
    except Exception as e:
        if os.path.exists(file_name): os.remove(file_name)
        print(f"❌ Error {name}: {e}")

def main():
    if is_it_shabbat():
        print("🕯️ Shabbat - Skipping")
        return

    now = datetime.datetime.now()
    
    # סנכרון להתחלה מדויקת
    if now.minute >= 50:
        seconds_to_wait = ((60 - now.minute) * 60) - now.second
        print(f"🕒 Waiting {seconds_to_wait}s until the top of the hour...")
        time.sleep(seconds_to_wait)
        now = datetime.datetime.now()

    # חישוב זמן עד סוף השעה (לדקה 00:00 של השעה הבאה)
    # אנחנו מוסיפים שעה אחת וקובעים את הדקות והשניות ל-0
    target_end_time = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    
    duration = int((target_end_time - now).total_seconds())

    # הגנה למקרה שהזמן שחושב ארוך מ-60 דקות בגלל סטיות קטנות
    if duration > 3600:
        duration = 3600

    print(f"🚀 Starting 60-min recording session at {now.strftime('%H:%M:%S')}. Duration: {duration}s")

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, duration))
        threads.append(t)
        t.start()
        time.sleep(10) 
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
