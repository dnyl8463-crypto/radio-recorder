import os
import subprocess
import datetime
import time

# הלינקים הכי אמינים ששלחת
STREAMS = {
    "Kol_Chai": "https://live.kcm.fm/live-new",
    "Kol_Barama": "https://cdn.cybercdn.live/Kol_Barama/Live_Audio/icecast.audio",
    "Kol_Chai_Music": "https://live.kcm.fm/livemusic",
    "Kol_Play": "https://cdn.cybercdn.live/Kol_Barama/Music/icecast.audio"
}

RECORD_DURATION = 60 # משך הקלטה של דקה אחת

def record_stream(name, url, duration):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"--- Starting FFmpeg recording for: {name} ---")
    
    # פקודה חזקה שמתעלמת משגיאות קטנות בזרם ומקליטה ישירות
    command = [
        'ffmpeg',
        '-y',                      # דריסת קובץ קיים
        '-i', url,                 # הלינק הישיר
        '-t', str(duration),       # זמן הקלטה
        '-c:a', 'libmp3lame',      # קידוד MP3
        '-b:a', '128k',            # איכות
        '-timeout', '20000000',    # המתנה של 20 שניות לחיבור
        file_name
    ]
    
    try:
        # הרצה
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # בדיקת תוצאה
        if os.path.exists(file_name):
            size = os.path.getsize(file_name)
            if size > 50000: # מעל 50KB זה נחשב הקלטה אמיתית
                print(f"✅ Success: {name} recorded! Size: {size} bytes")
                return file_name
            else:
                print(f"⚠️ Warning: {name} file too small ({size} bytes). Deleting.")
                os.remove(file_name)
        else:
            print(f"❌ Error: {name} file was not created.")
            print(f"FFmpeg output: {process.stderr[-200:]}") # מדפיס את סוף השגיאה ללוג
            
    except Exception as e:
        print(f"❌ Exception for {name}: {e}")
    return None

def main():
    results = []
    for name, url in STREAMS.items():
        res = record_stream(name, url, RECORD_DURATION)
        if res:
            results.append(res)
    print(f"--- Final: Recorded {len(results)} files ---")

if __name__ == "__main__":
    main()
