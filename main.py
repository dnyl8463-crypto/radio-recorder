import os
import time
import datetime
import requests

# הגדרות
PARENT_FOLDER_ID = '12UDAp_Gr86BnA7qGWnFTNWlIRNKeQtnI'
STREAMS = {
    "קול חי": "https://bit.ly/3S1R9Z9",
    "קול ברמה": "https://live.kol-barama.co.il/live/kolbarama/playlist.m3u8",
    "קול חי מיוזיק": "https://bit.ly/3S4kG2R",
    "קול פליי": "https://live.kol-play.co.il/live/kolplay/playlist.m3u8"
}
RECORD_DURATION = 30 # לבדיקה, שנה ל-3600 אחר כך

def get_access_token():
    """משיג Access Token חדש בעזרת ה-Refresh Token"""
    url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": os.environ['CLIENT_ID'],
        "client_secret": os.environ['CLIENT_SECRET'],
        "refresh_token": os.environ['REFRESH_TOKEN'],
        "grant_type": "refresh_token"
    }
    response = requests.post(url, data=data)
    return response.json().get("access_token")

def upload_to_drive(file_name, file_path, folder_id, access_token):
    """מעלה קובץ ישירות לדרייב ללא צורך ב-Service Account"""
    metadata = {
        "name": file_name,
        "parents": [folder_id]
    }
    files = {
        'data': ('metadata', str(metadata), 'application/json; charset=UTF-8'),
        'file': open(file_path, 'rb')
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
        headers=headers,
        files=files
    )
    return response.json()

def record_stream(name, url, duration):
    file_name = f"{name}_{datetime.datetime.now().strftime('%H-%M')}.mp3"
    print(f"מקליט את {name}...")
    try:
        r = requests.get(url, stream=True, timeout=15)
        with open(file_name, 'wb') as f:
            start_time = time.time()
            for chunk in r.iter_content(chunk_size=1024*512):
                if time.time() - start_time > duration: break
                if chunk: f.write(chunk)
        return file_name
    except: return None

def main():
    token = get_access_token()
    if not token:
        print("שגיאה: לא הצלחתי להשיג Access Token. בדוק את ה-Secrets.")
        return

    for name, url in STREAMS.items():
        file_path = record_stream(name, url, RECORD_DURATION)
        if file_path:
            print(f"מעלה את {name} לחשבון האישי שלך...")
            result = upload_to_drive(file_path, file_path, PARENT_FOLDER_ID, token)
            if 'id' in result:
                print(f"✅ הצלחנו! הקובץ בדרייב.")
                os.remove(file_path)
            else:
                print(f"❌ שגיאה בהעלאה: {result}")

if __name__ == "__main__":
    main()
