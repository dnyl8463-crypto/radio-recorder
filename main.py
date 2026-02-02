import os
import requests
import subprocess
import datetime
import json
import time
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# הגדרות
PARENT_FOLDER_ID = "1g4wD9diG4Y4DCGhkjnagkZ0qXPti1glu"
STATIONS = {
    "קול חי": "https://live.kcm.fm/live-new",
    "קול ברמה": "https://cdn.cybercdn.live/Kol_Barama/Live_Audio/icecast.audio",
    "קול חי מיוזיק": "https://live.kcm.fm/livemusic",
    "קול פליי": "https://cdn.cybercdn.live/Kol_Barama/Music/icecast.audio"
}

# הגדרת מספר הימים לשמירת קבצים
DAYS_TO_KEEP = 3 

def is_shabbat():
    try:
        res = requests.get("https://www.hebcal.com/shabbat?cfg=json&geo=pos&lat=31.7683&lon=35.2137&m=50").json()
        now = datetime.datetime.now(datetime.timezone.utc)
        items = res['items']
        start = datetime.datetime.fromisoformat(next(i['date'] for i in items if i['category'] == 'candles'))
        end = datetime.datetime.fromisoformat(next(i['date'] for i in items if i['category'] == 'havdalah'))
        return start <= now <= end
    except:
        return False

def get_drive_service():
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if not creds_json:
        raise Exception("Missing GOOGLE_CREDENTIALS secret")
    info = json.loads(creds_json)
    creds = Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/drive'])
    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, name):
    query = f"name = '{name}' and '{PARENT_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query).execute().get('files', [])
    if results:
        return results[0]['id']
    file_metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [PARENT_FOLDER_ID]}
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def delete_old_files(service):
    print(f"בודק אם יש קבצים ישנים למחיקה (מעל {DAYS_TO_KEEP} ימים)...")
    # חישוב התאריך של לפני X ימים
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=DAYS_TO_KEEP)
    cutoff_iso = cutoff_date.isoformat() + "Z"
    
    # חיפוש קבצים ישנים בתוך התיקייה הראשית (כולל תתי תיקיות)
    query = f"modifiedTime < '{cutoff_iso}' and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute().get('files', [])
    
    for file in results:
        try:
            print(f"מוחק קובץ ישן: {file['name']}")
            service.files().delete(fileId=file['id']).execute()
        except Exception as e:
            print(f"שגיאה במחיקת קובץ: {e}")

def main():
    if is_shabbat():
        print("שבת עכשיו - המערכת בהפסקה.")
        return

    service = get_drive_service()
    
    # שלב הניקוי: מוחק קבצים ישנים לפני שמתחיל להקליט חדשים
    delete_old_files(service)
    
    # שעון ישראל (UTC+2)
    now_str = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%d-%m-%Y_%H-00")

    for name, url in STATIONS.items():
        try:
            folder_id = get_or_create_folder(service, name)
            filename = f"{name}_{now_str}.mp3"
            print(f"מקליט את {name}...")
            
            # הקלטה של 30 שניות (30 שניות)
            subprocess.run(['ffmpeg', '-i', url, '-t', '30', '-acodec', 'libmp3lame', '-ab', '64k', filename], check=True)
            
            print(f"מעלה את {filename}...")
            file_metadata = {'name': filename, 'parents': [folder_id]}
            media = MediaFileUpload(filename, mimetype='audio/mpeg')
            service.files().create(body=file_metadata, media_body=media).execute()
            
            os.remove(filename)
        except Exception as e:
            print(f"שגיאה בטיפול ב-{name}: {e}")

if __name__ == "__main__":
    main()
