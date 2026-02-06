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
    except: return False

def record_stream(name, url, duration):
    # שימוש בזמן ישראל לשם הקובץ
    israel_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{israel_time}.mp3"
    
    command = [
        'ffmpeg', '-y',
        '-user_agent', 'Mozilla/5.0',
        '-i', url, '-t', str(duration),
        '-acodec', 'libmp3lame', '-ab', '128k', '-ar', '44100', file_name
    ]
    
    try:
        subprocess.run(command, check=True, timeout=duration + 300)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 50000:
            print(f"✅ Success: {file_name}")
        else:
            if os.path.exists(file_name): os.remove(file_name)
    except:
        if os.path.exists(file_name): os.remove(file_name)

def main():
    if is_it_shabbat(): return

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=2) # זמן ישראל
    
    # חישוב זמן עד סוף השעה (60 דקות מלאות)
    target_end_time = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    duration = int((target_end_time - now).total_seconds())
    
    if duration > 3600: duration = 3600
    if duration < 300: return # אם נשארו פחות מ-5 דקות לשעה, אל תקליט (מונע כפילויות)

    print(f"🚀 Starting session at Israel Time: {now.strftime('%H:%M:%S')}")

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
