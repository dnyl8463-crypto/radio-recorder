import os
import time
import datetime
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests

# ה-ID שלך
PARENT_FOLDER_ID = '12UDAp_Gr86BnA7qGWnFTNWlIRNKeQtnI'

STREAMS = {
    "קול חי": "https://bit.ly/3S1R9Z9",
    "קול ברמה": "https://live.kol-barama.co.il/live/kolbarama/playlist.m3u8",
    "קול חי מיוזיק": "https://bit.ly/3S4kG2R",
    "קול פליי": "https://live.kol-play.co.il/live/kolplay/playlist.m3u8"
}

RECORD_DURATION = 30 # לבדיקה

def get_drive_service():
    scopes = ['https://www.googleapis.com/auth/drive']
    service_account_info = json.loads(os.environ['GOOGLE_CREDENTIALS'])
    creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=scopes)
    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, folder_name, parent_id):
    query = f"name = '{folder_name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute().get('files', [])
    if results:
        return results[0]['id']
    folder_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
    return service.files().create(body=folder_metadata, fields='id', supportsAllDrives=True).execute().get('id')

def record_and_upload(service, name, url, folder_id):
    file_name = f"{name}_{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')}.mp3"
    print(f"מקליט ומעלה את {name}...")
    
    # הקלטה לקובץ זמני
    try:
        response = requests.get(url, stream=True, timeout=15)
        with open("temp.mp3", 'wb') as f:
            start_time = time.time()
            for chunk in response.iter_content(chunk_size=1024*512):
                if time.time() - start_time > RECORD_DURATION: break
                if chunk: f.write(chunk)
        
        # העלאה
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        media = MediaFileUpload("temp.mp3", mimetype='audio/mpeg', resumable=True)
        
        # כאן הקוד פשוט "יוצר" את הקובץ בתוך האחסון של התיקייה הציבורית
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True
        ).execute()
        
        print(f"✅ {name} עלה בהצלחה!")
        if os.path.exists("temp.mp3"): os.remove("temp.mp3")
        
    except Exception as e:
        print(f"❌ שגיאה ב-{name}: {e}")

def main():
    service = get_drive_service()
    for name, url in STREAMS.items():
        folder_id = get_or_create_folder(service, name, PARENT_FOLDER_ID)
        record_and_upload(service, name, url, folder_id)

if __name__ == "__main__":
    main()
