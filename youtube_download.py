#!/usr/bin/env python3
"""YouTube Download using ffmpeg"""
import subprocess
import sys
import os

def download_youtube(url, output="video.mp4"):
    """Download YouTube video"""
    if not os.path.exists("/usr/bin/yt-dlp"):
        return "❌ yt-dlp not installed"
    
    cmd = ["yt-dlp", "-f", "best", "-o", output, url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return f"✅ Downloaded: {output}" if result.returncode == 0 else f"❌ {result.stderr}"

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    if not url:
        print("Usage: python3 youtube_download.py <youtube_url>")
    else:
        print(f"=== 📥 YOUTUBE DOWNLOAD ===")
        print(download_youtube(url))
