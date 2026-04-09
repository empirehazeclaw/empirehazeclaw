#!/usr/bin/env python3
"""
Google Drive Integration für OpenClaw
- Backup zu Google Drive
- Upload von Dateien
- Download von Dateien
"""
import os
import json
import argparse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
import io

# Config
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',  # Dateien erstellen/bearbeiten
    'https://www.googleapis.com/auth/drive.readonly'  # Dateien lesen
]

CREDENTIALS_FILE = os.path.expanduser('~/.config/openclaw/google_credentials.json')
TOKEN_FILE = os.path.expanduser('~/.config/openclaw/google_token.json')

class GoogleDrive:
    def __init__(self):
        self.service = None
        self.creds = None
        self._authenticate()
    
    def _authenticate(self):
        """Authentifiziere mit Google"""
        self.creds = None
        
        # Token laden
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
                self.creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        
        # Prüfen ob gültig
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("🔄 Token abgelaufen, erneuere...")
                self.creds.refresh(Request())
            else:
                print("🔐 Neue Anmeldung erforderlich...")
                self._run_oauth()
        
        # Service erstellen
        self.service = build('drive', 'v3', credentials=self.creds)
        print("✅ Mit Google Drive verbunden!")
    
    def _run_oauth(self):
        """OAuth Flow starten"""
        # Credentials Datei suchen
        creds_path = CREDENTIALS_FILE
        
        if not os.path.exists(creds_path):
            print(f"""
❌ Keine Credentials gefunden!

1. Gehe zu: https://console.cloud.google.com/apis/credentials
2. Erstelle "OAuth Client ID"
3. Download als JSON → speichere als:
   {creds_path}
4. Führe dieses Script erneut aus
            """)
            exit(1)
        
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        self.creds = flow.run_local_server(port=8080)
        
        # Token speichern
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, 'w') as f:
            f.write(self.creds.to_json())
        
        print("✅ Token gespeichert!")
    
    def list_files(self, folder_id=None, max_results=50):
        """Dateien auflisten"""
        query = f"'{folder_id}' in parents and trashed=false" if folder_id else "trashed=false"
        
        results = self.service.files().list(
            q=query,
            pageSize=max_results,
            fields="files(id, name, mimeType, size, modifiedTime)"
        ).execute()
        
        return results.get('files', [])
    
    def upload(self, file_path, folder_id=None, name=None):
        """Datei hochladen"""
        if not os.path.exists(file_path):
            print(f"❌ Datei nicht gefunden: {file_path}")
            return None
        
        name = name or os.path.basename(file_path)
        
        file_metadata = {'name': name}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(file_path, resumable=True)
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        print(f"✅ Hochgeladen: {file.get('name')} (ID: {file.get('id')})")
        return file
    
    def download(self, file_id, output_path):
        """Datei herunterladen"""
        request = self.service.files().get_media(fileId=file_id)
        
        with open(output_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        
        print(f"✅ Heruntergeladen: {output_path}")
    
    def create_folder(self, name, parent_id=None):
        """Ordner erstellen"""
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        folder = self.service.files().create(
            body=file_metadata,
            fields='id, name'
        ).execute()
        
        print(f"✅ Ordner erstellt: {name} (ID: {folder.get('id')})")
        return folder
    
    def find_file(self, name, folder_id=None):
        """Datei finden"""
        query = f"name='{name}'"
        if folder_id:
            query += f" and '{folder_id}' in parents"
        
        results = self.service.files().list(q=query, pageSize=1).execute()
        files = results.get('files', [])
        
        return files[0] if files else None
    
    def delete(self, file_id):
        """Datei löschen"""
        self.service.files().delete(fileId=file_id).execute()
        print(f"✅ Gelöscht: {file_id}")
    
    def get_share_link(self, file_id):
        """Freigabe-Link erstellen"""
        self.service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        file = self.service.files().get(
            fileId=file_id, 
            fields='webViewLink'
        ).execute()
        
        return file.get('webViewLink')


def main():
    parser = argparse.ArgumentParser(description='Google Drive CLI')
    parser.add_argument('command', choices=['auth', 'list', 'upload', 'download', 'folder', 'delete', 'share'])
    parser.add_argument('--file', '-f', help='Datei')
    parser.add_argument('--name', '-n', help='Name')
    parser.add_argument('--folder', help='Folder ID')
    parser.add_argument('--output', '-o', help='Output Pfad')
    parser.add_argument('--id', help='File ID')
    
    args = parser.parse_args()
    
    drive = GoogleDrive()
    
    if args.command == 'auth':
        print("🔐 OAuth neu starten...")
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        drive._run_oauth()
    
    elif args.command == 'list':
        files = drive.list_files(args.folder)
        print(f"\n📁 Dateien ({len(files)}):")
        for f in files:
            icon = "📁" if f['mimeType'] == 'application/vnd.google-apps.folder' else "📄"
            size = int(f.get('size', 0))
            size_str = f"{size/1024:.1f}KB" if size else "-"
            print(f"  {icon} {f['name']} ({size_str})")
    
    elif args.command == 'upload':
        if not args.file:
            print("❌ --file erforderlich")
            return
        drive.upload(args.file, args.folder, args.name)
    
    elif args.command == 'download':
        if not args.id or not args.output:
            print("❌ --id und --output erforderlich")
            return
        drive.download(args.id, args.output)
    
    elif args.command == 'folder':
        if not args.name:
            print("❌ --name erforderlich")
            return
        drive.create_folder(args.name, args.folder)
    
    elif args.command == 'delete':
        if not args.id:
            print("❌ --id erforderlich")
            return
        drive.delete(args.id)
    
    elif args.command == 'share':
        if not args.id:
            print("❌ --id erforderlich")
            return
        link = drive.get_share_link(args.id)
        print(f"🔗 Link: {link}")


if __name__ == '__main__':
    main()
