#!/usr/bin/env python3
"""
Log Rotation - Begrenzt Log-Dateien auf max. Größe/Alter
"""

import os
import glob
from datetime import datetime, timedelta

LOG_DIR = "/home/clawbot/.openclaw/logs"
MAX_SIZE_MB = 10  # Max 10MB pro Log
MAX_AGE_DAYS = 7  # Max 7 Tage alt

def rotate_logs():
    """Rotiere alte/zu große Logs"""
    rotated = 0
    
    for log_file in glob.glob(f"{LOG_DIR}/*.log"):
        try:
            size_mb = os.path.getsize(log_file) / (1024 * 1024)
            mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
            age = (datetime.now() - mtime).days
            
            # Zu groß?
            if size_mb > MAX_SIZE_MB:
                # Archivieren
                archive = f"{log_file}.{datetime.now().strftime('%Y%m%d')}"
                os.rename(log_file, archive)
                # Leere neue Datei erstellen
                open(log_file, 'w').close()
                rotated += 1
                print(f"📦 Rotated (size): {os.path.basename(log_file)} ({size_mb:.1f}MB)")
            
            # Zu alt?
            elif age > MAX_AGE_DAYS:
                os.remove(log_file)
                rotated += 1
                print(f"🗑️ Removed (age): {os.path.basename(log_file)} ({age}d)")
                
        except Exception as e:
            print(f"❌ Error: {log_file}: {e}")
    
    # Auch .gz Archive aufräumen
    for old_log in glob.glob(f"{LOG_DIR}/*.log.*.gz"):
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(old_log))
            age = (datetime.now() - mtime).days
            if age > 30:  # 30 Tage Archive behalten
                os.remove(old_log)
                rotated += 1
                print(f"🗑️ Removed archive: {os.path.basename(old_log)}")
        except:
            pass
    
    print(f"\n✅ Log-Rotation abgeschlossen: {rotated} Dateien bearbeitet")
    return rotated

if __name__ == "__main__":
    rotate_logs()
