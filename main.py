import os
import time
import datetime
import requests

# מיפוי שמות לאנגלית כדי למנוע שגיאות העלאה ב-GitHub
STREAMS = {
    "Kol_Chai": "https://bit.ly/3S1R9Z9",
    "Kol_Barama": "https://live.kol-barama.co.il/live/kolbarama/playlist.m3u8",
    "Kol_Chai_Music": "https://bit.ly/3S4kG2R",
    "Kol_Play": "https://live.kol-play.co.il/live/kolplay/playlist.m3u8"
}

RECORD_DURATION = 30 # לבדיקה, שנה ל-3600 אחר כך

def record_stream(name, url, duration):
    # שם קובץ נקי באנגלית עם תאריך ושעה
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"Recording {name}...")
    try:
        r = requests.get(url, stream=True, timeout=15)
        with open(file_name, 'wb') as f:
            start_time = time.time()
            for chunk in r.iter_content(chunk_size=1024*512):
                if time.time() - start_time > duration: break
                if chunk: f.write(chunk)
        return file_name
    except Exception as e:
        print(f"Error recording {name}: {e}")
        return None

def main():
    recorded_files = []
    for name, url in STREAMS.items():
        file_path = record_stream(name, url, RECORD_DURATION)
        if file_path:
            recorded_files.append(file_path)
    
    print(f"Finished recording: {recorded_files}")

if __name__ == "__main__":
    main()
