import os
import time
import datetime
import requests

# לינקים חלופיים ויציבים יותר
STREAMS = {
    "Kol_Chai": "https://cdn.livecast.co.il/radio-kolchai-mp3/stream",
    "Kol_Barama": "https://kbr.livecast.co.il/kolbarama-mp3/stream",
    "Kol_Chai_Music": "https://cdn.livecast.co.il/radio-music-mp3/stream",
    "Kol_Play": "https://live.kol-play.co.il/live/kolplay/playlist.m3u8"
}

RECORD_DURATION = 60 # נגדיל לדקה כדי להבטיח קובץ משמעותי

def record_stream(name, url, duration):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"--- Attempting to record: {name} ---")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # התחברות לסטרים
        r = requests.get(url, stream=True, timeout=30, headers=headers)
        print(f"Response code for {name}: {r.status_code}")
        
        if r.status_code != 200:
            return None

        with open(file_name, 'wb') as f:
            start_time = time.time()
            for chunk in r.iter_content(chunk_size=1024*128):
                if time.time() - start_time > duration: 
                    break
                if chunk:
                    f.write(chunk)
        
        size = os.path.getsize(file_name)
        print(f"Finished {name}. File size: {size} bytes")
        
        # אם הקובץ קטן מ-50KB הוא כנראה לא מכיל סאונד
        if size < 50000:
            os.remove(file_name)
            return None
            
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
    
    print(f"Final list for upload: {recorded_files}")

if __name__ == "__main__":
    main()
