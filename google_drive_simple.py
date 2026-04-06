#!/usr/bin/env python3
"""
Google Drive - Service Account Version
"""
import os
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = os.path.expanduser('~/.config/openclaw/service_account.json')

def main():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("❌ Keine Credentials gefunden!")
        return
    
    # Load as service account
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        
        # Test - list files
        results = service.files().list(pageSize=10).execute()
        files = results.get('files', [])
        
        print("✅ Mit Google Drive verbunden!")
        print(f"📁 Dateien: {len(files)}")
        for f in files:
            print(f"  - {f['name']}")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
        print("\nService Account muss im Google Cloud Console freigeschaltet werden!")
        print("APIs → Drive API → Enable")

if __name__ == '__main__':
    main()
