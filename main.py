import os
import subprocess
import datetime
import threading

STREAMS = {
    "Kol_Chai": "https://cdn.livecast.co.il/radio-kolchai-mp3/stream",
    "Kol_Barama": "https://kbr.livecast.co.il/kolbarama-mp3/stream",
    "Kol_Chai_Music": "https://cdn.livecast.co.il/radio-music-mp3/stream",
    "Kol_Play": "http://live.streamgates.net/radio/kolplay/icecast.audio"
}

# הגדר כאן כמה שניות להקליט (למשל 3600 לשעה שלמה)
RECORD_DURATION = 3600 

def record_stream(name, url, duration):
    # הזמן ייקלח מהגדרת ה-TZ ב-Workflow
    timestamp = datetime.datetime.now().strftime('%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"Starting recording: {name} for {duration} seconds...")
    
    # פקודת FFmpeg יעילה שפשוט מעתיקה את הזרם בלי לאמץ את המעבד
    command = [
        'ffmpeg', '-y', '-i', url, '-t', str(duration),
        '-acodec', 'copy', file_name
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"✅ Finished: {file_name}")
    except Exception as e:
        print(f"❌ Error recording {name}: {e}")

def main():
    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("--- All parallel recordings finished! ---")

if __name__ == "__main__":
    main()
