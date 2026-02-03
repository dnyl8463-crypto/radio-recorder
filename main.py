import os
import subprocess
import datetime

# הלינקים האמינים ששלחת
STREAMS = {
    "Kol_Chai": "https://live.kcm.fm/live-new",
    "Kol_Barama": "https://cdn.cybercdn.live/Kol_Barama/Live_Audio/icecast.audio",
    "Kol_Chai_Music": "https://live.kcm.fm/livemusic",
    "Kol_Play": "https://cdn.cybercdn.live/Kol_Barama/Music/icecast.audio"
}

RECORD_DURATION = 60 # הקלטה של דקה אחת לבדיקה

def record_stream(name, url, duration):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"--- Recording {name} using FFmpeg ---")
    
    # פקודת FFmpeg מותאמת ללינקים של Icecast
    command = [
        'ffmpeg',
        '-headers', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        '-i', url,                # הלינק ששלחת
        '-t', str(duration),      # זמן הקלטה
        '-c:a', 'libmp3lame',     # קידוד ל-MP3
        '-b:a', '128k',           # איכות סאונד טובה
        '-y',                     # דריסת קובץ אם קיים
        file_name
    ]
    
    try:
        # הרצת ההקלטה עם timeout לביטחון
        subprocess.run(command, check=True, timeout=duration + 60)
        
        if os.path.exists(file_name) and os.path.getsize(file_name) > 10000:
            print(f"✅ Success: {file_name} saved. Size: {os.path.getsize(file_name)} bytes")
            return file_name
        else:
            print(f"❌ Error: File {name} is too small or was not created.")
            return None
    except Exception as e:
        print(f"❌ FFmpeg error for {name}: {e}")
        return None

def main():
    recorded_count = 0
    for name, url in STREAMS.items():
        if record_stream(name, url, RECORD_DURATION):
            recorded_count += 1
    
    print(f"--- Finished! Total successful recordings: {recorded_count} ---")

if __name__ == "__main__":
    main()
