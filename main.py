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
    print("⏳ Server is ready. Waiting for the exact top of the hour (00:00:00)...")
    while True:
        # זמן ישראל (UTC+2)
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        
        # אם הגענו לשנייה ה-0 של הדקה ה-0
        if now.minute == 0 and now.second == 0:
            print(f"⏰ STARTING NOW: {now.strftime('%H:%M:%S')}")
            return now
        
        # בדיקה מהירה כל חצי שנייה לדיוק מקסימלי
        time.sleep(0.5)

def record_stream(name, url, start_time):
    # הקלטה של 3600 שניות = 60 דקות מלאות
    duration = 3600 
    
    # שם הקובץ יהיה השעה העגולה (למשל 18-00)
    file_timestamp = start_time.strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{file_timestamp}.mp3"
    
    command = [
        'ffmpeg', '-y',
        '-user_agent', 'Mozilla/5.0',
        '-i', url,
        '-t', str(duration),
        '-acodec', 'libmp3lame',
        '-ab', '128k',
        '-ar', '44100',
        file_name
    ]
    
    try:
        # הרצה עם חריגת זמן קטנה לביטחון
        subprocess.run(command, check=True, timeout=duration + 120)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 50000:
            print(f"✅ Success: {file_name}")
        else:
            if os.path.exists(file_name): os.remove(file_name)
    except:
        if os.path.exists(file_name): os.remove(file_name)

def main():
    # בדיקת שבת (לפי זמן ישראל)
    israel_now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    weekday = israel_now.weekday()
    if (weekday == 4 and israel_now.hour >= 16) or (weekday == 5 and israel_now.hour < 19):
        print("🕯️ Shabbat mode - Skipping")
        return

    # המתנה ליריית הפתיחה
    actual_start_time = wait_for_top_of_hour()

    threads = []
    for name, url in STREAMS.items():
        # כל תחנה מקבלת פקודה להקליט 60 דקות
        t = threading.Thread(target=record_stream, args=(name, url, actual_start_time))
        threads.append(t)
        t.start()
        time.sleep(1) # השהייה קלה כדי לא להעמיס את המעבד בשנייה הראשונה
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
