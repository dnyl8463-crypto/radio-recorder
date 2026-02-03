import os
import subprocess
import datetime
import threading
import requests

# רשימת התחנות והלינקים לסטרים
STREAMS = {
    "Kol_Chai": "https://cdn.livecast.co.il/radio-kolchai-mp3/stream",
    "Kol_Barama": "https://kbr.livecast.co.il/kolbarama-mp3/stream",
    "Kol_Chai_Music": "https://cdn.livecast.co.il/radio-music-mp3/stream",
    "Kol_Play": "http://live.streamgates.net/radio/kolplay/icecast.audio"
}

# משך ההקלטה בשניות (60 שניות = דקה)
# טיפ: בשביל בדיקה ראשונה, אפשר לשנות ל-60 כדי לראות שזה עובד מהר
RECORD_DURATION = 60 

def is_it_shabbat():
    """בודק מול ה-API של Hebcal האם עכשיו שבת בירושלים"""
    try:
        # פנייה ל-API עם נתוני מיקום של ירושלים
        response = requests.get("https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&m=50", timeout=15)
        data = response.json()
        
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        
        items = data['items']
        # מוצאים את זמני כניסת ויציאת שבת
        candle_lighting_str = next(item['date'] for item in items if item['category'] == 'candles')
        havdalah_str = next(item['date'] for item in items if item['category'] == 'havdalah')
        
        start_shabbat = datetime.datetime.fromisoformat(candle_lighting_str)
        end_shabbat = datetime.datetime.fromisoformat(havdalah_str)
        
        if start_shabbat <= now_utc <= end_shabbat:
            return True
        return False
    except Exception as e:
        print(f"Checking Shabbat failed: {e}. Defaulting to standard clock check.")
        # גיבוי: יום 5 הוא יום שבת במערכת הפנימית של פייתון
        return datetime.datetime.now().weekday() == 5

def record_stream(name, url, duration):
    """מבצע הקלטה של סטרים בודד עם מנגנון התחברות מחדש"""
    timestamp = datetime.datetime.now().strftime('%H-%M')
    file_name = f"{name}_{timestamp}.mp3"
    
    print(f"Starting recording: {name}...")
    
    # פקודת FFmpeg משופרת להתמודדות עם ניתוקים
    command = [
        'ffmpeg', '-y',
        '-reconnect', '1', 
        '-reconnect_streamed', '1', 
        '-reconnect_delay_max', '10', # ינסה להתחבר מחדש במשך 10 שניות אם הניתוק נמשך
        '-i', url, 
        '-t', str(duration), 
        '-acodec', 'copy', 
        file_name
    ]
    
    try:
        # הפעלת הפקודה עם Timeout של 5 דקות מעבר לזמן ההקלטה למקרה של תקיעה
        subprocess.run(command, check=True, timeout=duration + 300)
        print(f"✅ Successfully saved: {file_name}")
    except subprocess.TimeoutExpired:
        print(f"⚠️ {name} recording reached limit timeout.")
    except Exception as e:
        print(f"❌ Error recording {name}: {e}")

def main():
    # שלב 1: בדיקת שבת
    if is_it_shabbat():
        print("🕯️ Shabbat/Chag detected in Jerusalem. Skipping recording.")
        return

    # שלב 2: הקלטה במקביל
    threads = []
    for name, url in STREAMS.items():
        t = threading.Thread(target=record_stream, args=(name, url, RECORD_DURATION))
        threads.append(t)
        t.start()
    
    # המתנה לסיום כל ההקלטות
    for t in threads:
        t.join()
    
    print("--- Process Finished ---")

if __name__ == "__main__":
    main()
