#!/usr/bin/env python3
"""
Dropbox Upload - Simple Backup
"""
import os
import sys
import requests

# Dropbox App Key (you need to create one at https://www.dropbox.com/developers/apps)
# For now, let's use a simple approach with files

TOKEN_FILE = os.path.expanduser('~/.config/openclaw/dropbox_token')

def get_upload_link(token, path):
    """Get upload URL"""
    url = "https://content.dropboxapi.com/2/files/upload"
    headers = {
        "Authorization": f"Bearer {token}",
        "Dropbox-API-Arg": '{"path":"/' + path + '","mode":"add","autorename":true,"mute":false}',
        "Content-Type": "application/octet-stream"
    }
    return url, headers

def upload_file(token, file_path, dropbox_path):
    """Upload file to Dropbox"""
    url, headers = get_upload_link(token, dropbox_path)
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    headers['Content-Length'] = str(len(data))
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

print("""
📦 Dropbox Upload

1. Create Dropbox App:
   https://www.dropbox.com/developers/apps

2. Choose "Scoped Access" → "App folder"

3. Generate Access Token

4. Save token to: ~/.config/openclaw/dropbox_token
""")
