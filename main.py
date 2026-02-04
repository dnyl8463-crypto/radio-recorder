import os
import subprocess
import datetime
import requests
import threading
import time

# לינקים מעודכנים בפורמט שאמור להיות נגיש יותר
STREAMS = {
    "Kol_Chai": "https://live.kcm.fm/live-new",
    "Kol_Barama": "https://cdn.cybercdn.live/Kol_Barama/Live_Audio/icecast.audio",
    "Kol_Chai_Music": "https://live.kcm.fm/livemusic",
    "Kol_Play": "https://cdn.cybercdn.live/Kol_Barama/Music/icecast.audio"
}

RECORD_DURATION = 60 # דקה אחת

def is_it_shabbat():
    try:
        r = requests.get("https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&m=50", timeout=10)
        data = r.json()
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        items = data['items']
        start = datetime.datetime.fromisoformat(next(i['date'] for i in items if i['category'] == 'candles'))
        end = datetime.datetime.fromisoformat(next(i['date'] for i in items if i['category'] == 'havdalah'))
        return start <= now_utc <= end
    except:
        return False

def record_stream(name, url, duration):
    timestamp = datetime.datetime.now().strftime('%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"--- מנסה להקליט את {name} ---")
    
    # פקודה עם דגלים לעקיפת חסימות וטיימאאוט ארוך יותר
    command = [
        'ffmpeg', '-y',
        '-headers', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36\r\n',
        '-i', url,
        '-t', str(duration),
        '-acodec', 'copy',
        file_name
    ]
    
    try:
        # ניסיון ראשון
        subprocess.run(command, check=True, timeout=duration + 120)
        
        # בדיקה אם הקובץ נוצר והוא תקין
        if os.path.exists(file_name) and os.path.getsize(file_name) > 1000:
            print(f"✅ הצלחתי להקליט את {name}!")
        else:
            print(f"⚠️ קובץ ריק עבור {name}, מנסה שוב בשיטה חלופית...")
            if os.path.exists(file_name): os.remove(file_name)
    except Exception as e:
        print(f"❌ שגיאה בהקלטת {name}: {e}")

def main():
    if is_it_shabbat():
        print("🕯️ שבת עכשיו, לא מקליט.")
        return

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
        time.sleep(10) # המתנה של 10 שניות בין תחנה לתחנה כדי לא להדליק נורות אדומות בשרתים
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
