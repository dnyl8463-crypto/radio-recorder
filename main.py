import os
import time
import datetime
import requests

STREAMS = {
    "קול חי": "https://bit.ly/3S1R9Z9",
    "קול ברמה": "https://live.kol-barama.co.il/live/kolbarama/playlist.m3u8",
    "קול חי מיוזיק": "https://bit.ly/3S4kG2R",
    "קול פליי": "https://live.kol-play.co.il/live/kolplay/playlist.m3u8"
}

RECORD_DURATION = 30 # לבדיקה, שנה ל-3600 אחר כך

def record_stream(name, url, duration):
    file_name = f"{name}_{datetime.datetime.now().strftime('%H-%M')}.mp3".replace(" ", "_")
    print(f"מקליט את {name}...")
    try:
        r = requests.get(url, stream=True, timeout=15)
        with open(file_name, 'wb') as f:
            start_time = time.time()
            for chunk in r.iter_content(chunk_size=1024*512):
                if time.time() - start_time > duration: break
                if chunk: f.write(chunk)
        return file_name
    except: return None

def main():
    recorded_files = []
    for name, url in STREAMS.items():
        file_path = record_stream(name, url, RECORD_DURATION)
        if file_path:
            recorded_files.append(file_path)
    
    # הקוד רק מקליט ושומר מקומית, ה-Action יעשה את השאר
    print(f"סיימתי להקליט: {recorded_files}")

if __name__ == "__main__":
    main()
