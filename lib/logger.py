"""
📝 CENTRALIZED ERROR LOGGING
"""

import os
import json
from datetime import datetime

LOG_DIR = "/home/clawbot/.openclaw/workspace/logs"

def log(level, source, message, data=None):
    """Centralized logging"""
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "source": source,
        "message": message,
        "data": data
    }
    
    log_file = f"{LOG_DIR}/{level.lower()}.log"
    
    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except:
        pass
    
    emoji = {"INFO": "ℹ️", "WARN": "⚠️", "ERROR": "❌", "CRITICAL": "🚨"}
    print(f"{emoji.get(level, '📝')} [{source}] {message}")
    
    return entry

def info(source, message): log("INFO", source, message)
def warn(source, message): log("WARN", source, message)
def error(source, message, data=None): log("ERROR", source, message, data)
def critical(source, message, data=None): log("CRITICAL", source, message, data)

if __name__ == "__main__":
    info("test", "Logger works!")
    error("test", "Error message", {"code": 404})
