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

# 59 דקות הקלטה
RECORD_DURATION = 3540 

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
        subprocess.run(command, check=True, timeout=duration + 150)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 20000:
            print(f"✅ Success: {file_name}")
        else:
            if os.path.exists(file_name): os.remove(file_name)
            print(f"⚠️ {name} failed: small file.")
    except Exception as e:
        if os.path.exists(file_name): os.remove(file_name)
        print(f"❌ Error {name}: {e}")

def main():
    if is_it_shabbat():
        print("🕯️ Shabbat - Skipping")
        return

    now = datetime.datetime.now()
    
    # אם הגענו מוקדם (דקות 50-59) - נחכה לשעה העגולה
    if now.minute >= 50:
        seconds_to_wait = ((60 - now.minute) * 60) - now.second
        print(f"🕒 Started early ({now.strftime('%H:%M:%S')}). Waiting {seconds_to_wait} seconds...")
        time.sleep(seconds_to_wait)
    
    # אם הגענו בדקה 1 עד 10 - נתחיל מיד (זה אומר שזה הגיבוי או שהיה איחור)
    elif 1 <= now.minute <= 10:
        print(f"🕒 Backup trigger or slight delay. Starting now: {now.strftime('%H:%M:%S')}")
    
    # אם הגענו סתם באמצע השעה (מעל דקה 10) - אל תקליט כדי למנוע כפילויות
    elif now.minute > 10:
        print(f"🕒 Current minute is {now.minute}. Skipping to avoid double recording.")
        return

    print(f"🚀 Final start time: {datetime.datetime.now().strftime('%H:%M:%S')}")

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
        time.sleep(12) 
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
