#!/usr/bin/env python3
"""
Daily Outreach - Automated Email Campaigns
Processes email sequences and sends pending emails
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Run the automated outreach
from automated_outreach import process_outreach

if __name__ == "__main__":
    print(f"[{datetime.now()}] Starting daily outreach...")
    
    try:
        process_outreach()
        print(f"[{datetime.now()}] Daily outreach completed")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR in daily outreach: {e}")
