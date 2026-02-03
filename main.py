import os
import time
import datetime
import requests

# קישורים ישירים מעודכנים
STREAMS = {
    "Kol_Chai": "https://stream.kol-chai.co.il/direct/radio/stream",
    "Kol_Barama": "https://live.kol-barama.co.il/live/kolbarama/playlist.m3u8",
    "Kol_Chai_Music": "https://stream.kol-chai.co.il/direct/music/stream",
    "Kol_Play": "https://live.kol-play.co.il/live/kolplay/playlist.m3u8"
}

RECORD_DURATION = 40 # הגדלנו מעט את זמן ההקלטה לבדיקה

def record_stream(name, url, duration):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"Attempting to record {name}...")
    try:
        # התחזות לדפדפן כדי למנוע חסימה
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # התחלת הבקשה
        r = requests.get(url, stream=True, timeout=30, headers=headers)
        
        if r.status_code != 200:
            print(f"Skipping {name}: Server returned {r.status_code}")
            return None

        with open(file_name, 'wb') as f:
            start_time = time.time()
            for chunk in r.iter_content(chunk_size=1024*256): # צ'אנק גדול יותר ליציבות
                if time.time() - start_time > duration: 
                    break
                if chunk: 
                    f.write(chunk)
        
        # בדיקה קריטית: אם הקובץ קטן מ-100KB, הוא כנראה פגום
        file_size = os.path.getsize(file_name)
        if file_size < 102400: 
            print(f"File {name} is too small ({file_size} bytes), ignoring.")
            os.remove(file_name)
            return None
            
        print(f"Successfully recorded {name} ({file_size} bytes)")
        return file_name
        
    except Exception as e:
        print(f"Failed to record {name}: {e}")
        return None

def main():
    recorded_files = []
    for name, url in STREAMS.items():
        file_path = record_stream(name, url, RECORD_DURATION)
        if file_path:
            recorded_files.append(file_path)
    
    if not recorded_files:
        print("No valid recordings were created. Check the stream URLs.")
    else:
        print(f"Finished! Files to upload: {recorded_files}")

if __name__ == "__main__":
    main()
