import os
import time
import datetime
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests

# הגדרות
PARENT_FOLDER_ID = '12UDAp_Gr86BnA7qGWnFTNWlIRNKeQtnI'

STREAMS = {
    "קול חי": "https://bit.ly/3S1R9Z9",
    "קול ברמה": "https://live.kol-barama.co.il/live/kolbarama/playlist.m3u8",
    "קול חי מיוזיק": "https://bit.ly/3S4kG2R",
    "קול פליי": "https://live.kol-play.co.il/live/kolplay/playlist.m3u8"
}

# זמן הקלטה בשניות (30 לבדיקה, שנה ל-3600 אחרי שזה עובד)
RECORD_DURATION = 30 

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
    
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(body=folder_metadata, fields='id', supportsAllDrives=True).execute()
    return folder.get('id')

def upload_to_drive(service, file_name, file_path, folder_id):
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaFileUpload(file_path, mimetype='audio/mpeg', resumable=True)
    # תיקון קריטי למניעת שגיאת מכסה (Quota)
    file = service.files().create(
        body=file_metadata, 
        media_body=media, 
        fields='id',
        supportsAllDrives=True
    ).execute()
    return file.get('id')

def record_stream(name, url, duration):
    file_name = f"{name}_{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')}.mp3"
    print(f"מקליט את {name}...")
    try:
        response = requests.get(url, stream=True, timeout=10)
        with open(file_name, 'wb') as f:
            start_time = time.time()
            for chunk in response.iter_content(chunk_size=1024*1024):
                if time.time() - start_time > duration:
                    break
                if chunk:
                    f.write(chunk)
        return file_name
    except Exception as e:
        print(f"שגיאה בהקלטת {name}: {e}")
        return None

def delete_old_files(service):
    three_days_ago = (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat() + 'Z'
    query = f"modifiedTime < '{three_days_ago}' and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
    try:
        results = service.files().list(q=query, fields="files(id, name)").execute().get('files', [])
        for f in results:
            service.files().delete(fileId=f['id'], supportsAllDrives=True).execute()
    except:
        pass

def main():
    service = get_drive_service()
    delete_old_files(service)
    
    for name, url in STREAMS.items():
        file_path = record_stream(name, url, RECORD_DURATION)
        if file_path:
            folder_id = get_or_create_folder(service, name, PARENT_FOLDER_ID)
            print(f"מעלה את {file_path}...")
            try:
                upload_to_drive(service, file_path, file_path, folder_id)
                os.remove(file_path)
            except Exception as e:
                print(f"שגיאה בטיפול ב-{name}: {e}")

if __name__ == "__main__":
    main()
