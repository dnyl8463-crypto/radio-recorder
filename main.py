import os
import subprocess
import datetime
import requests
import threading
import time

# לינקים עוקפי חסימה (פרוקסים)
STREAMS = {
    "Kol_Chai": "https://live.kcm.fm/live-new",
    "Kol_Barama": "https://sc.mediacast.co.il/proxy/kolbarama/",
    "Kol_Chai_Music": "https://live.kcm.fm/livemusic",
    "Kol_Play": "https://sc.mediacast.co.il/proxy/kolplay/"
}

RECORD_DURATION = 60 

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
    
    # פקודה עם התחזות מלאה לדפדפן וזמן המתנה ארוך
    command = [
        'ffmpeg', '-y',
        '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        '-headers', 'Referer: https://www.93fm.co.il/\r\n',
        '-i', url,
        '-t', str(duration),
        '-acodec', 'copy',
        file_name
    ]
    
    try:
        # הרצה עם סבלנות גבוהה לחיבור
        subprocess.run(command, check=True, timeout=duration + 120)
        
        if os.path.exists(file_name) and os.path.getsize(file_name) > 10000:
            print(f"✅ הצלחה: {file_name}")
        else:
            if os.path.exists(file_name): os.remove(file_name)
            print(f"⚠️ {name} יצר קובץ ריק (נחסם)")
    except Exception as e:
        if os.path.exists(file_name): os.remove(file_name)
        print(f"❌ שגיאה ב-{name}: {e}")

def main():
    if is_it_shabbat():
        print("🕯️ שבת - מדלג על הקלטה")
        return

    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
        time.sleep(15) # המתנה ארוכה בין תחנה לתחנה כדי לא לעורר חשד
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
