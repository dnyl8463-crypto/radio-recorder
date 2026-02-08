import os
import subprocess
import datetime
import threading
import time

STREAMS = {
    "Kol_Chai": "https://live.kcm.fm/live-new",
    "Kol_Barama": "https://cdn.cybercdn.live/Kol_Barama/Live_Audio/icecast.audio",
    "Kol_Chai_Music": "https://live.kcm.fm/livemusic",
    "Kol_Play": "https://cdn.cybercdn.live/Kol_Barama/Music/icecast.audio"
}

def wait_for_top_of_hour():
    print("⏳ Waiting for the exact start of the next hour (Israel Time)...")
    while True:
        israel_now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        if israel_now.minute == 0 and israel_now.second == 0:
            print(f"⏰ IT'S TIME! Starting: {israel_now.strftime('%H:%M:%S')}")
            return israel_now # מחזירים את השעה המדויקת של תחילת ההקלטה
        time.sleep(0.5)

def record_stream(name, url, start_time):
    duration = 3600
    # כאן הקסם: השם נקבע לפי זמן ההתחלה המדויק (למשל 18:00) ולא זמן ההתעוררות (17:55)
    file_timestamp = start_time.strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{file_timestamp}.mp3"
    
    command = [
        'ffmpeg', '-y',
        '-user_agent', 'Mozilla/5.0',
        '-i', url, '-t', str(duration),
        '-acodec', 'libmp3lame', '-ab', '128k', '-ar', '44100', file_name
    ]
    
    try:
        subprocess.run(command, check=True, timeout=duration + 300)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 50000:
            print(f"✅ Finished: {file_name}")
        else:
            if os.path.exists(file_name): os.remove(file_name)
    except:
        if os.path.exists(file_name): os.remove(file_name)

def main():
    # בדיקת שבת
    israel_now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    weekday = israel_now.weekday()
    if (weekday == 4 and israel_now.hour >= 16) or (weekday == 5 and israel_now.hour < 19):
        return

    # מחכים ל-00:00 ומקבלים את השעה העגולה
    start_time = wait_for_top_of_hour()

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, start_time))
        threads.append(t)
        t.start()
        time.sleep(2)
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
