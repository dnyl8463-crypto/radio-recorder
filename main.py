import os
import time
import datetime
import requests

# לינקים ישירים בפורמט MP3 - הכי יציב שיש
STREAMS = {
    "Kol_Chai": "http://live.streamgates.net/radio/kolchai/icecast.audio",
    "Kol_Barama": "http://live.streamgates.net/radio/kolbarama/icecast.audio",
    "Kol_Chai_Music": "http://live.streamgates.net/radio/kolchaimusic/icecast.audio",
    "Kol_Play": "http://live.streamgates.net/radio/kolplay/icecast.audio"
}

RECORD_DURATION = 60 

def record_stream(name, url, duration):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"--- Recording: {name} ---")
    try:
        # התחזות ל-iPhone (שרתים כמעט אף פעם לא חוסמים iPhone)
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
        }
        
        r = requests.get(url, stream=True, timeout=30, headers=headers)
        print(f"Server Response for {name}: {r.status_code}")
        
        if r.status_code != 200:
            return None

        with open(file_name, 'wb') as f:
            start_time = time.time()
            # קריאת נתונים בבלוקים קטנים יותר ליציבות
            for chunk in r.iter_content(chunk_size=1024*64):
                if time.time() - start_time > duration: 
                    break
                if chunk:
                    f.write(chunk)
        
        size = os.path.getsize(file_name)
        print(f"Final size: {size} bytes")
        
        # אם הקובץ קטן מ-100KB הוא פגום
        if size < 100000:
            os.remove(file_name)
            return None
            
        return file_name
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    recorded_files = []
    for name, url in STREAMS.items():
        file_path = record_stream(name, url, RECORD_DURATION)
        if file_path:
            recorded_files.append(file_path)
    print(f"Files ready: {recorded_files}")

if __name__ == "__main__":
    main()
