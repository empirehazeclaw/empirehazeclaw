#!/usr/bin/env python3
"""
Daily Notes - Chronological timeline
"""

import os
from datetime import datetime
from pathlib import Path

class DailyNotes:
    """Daily Notes with time blocks"""
    
    TIME_BLOCKS = {
        "morning": (0, 12),
        "afternoon": (12, 18),
        "evening": (18, 24)
    }
    
    def __init__(self, path: str = None):
        if path is None:
            path = "/home/clawbot/.openclaw/workspace/memory/daily"
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
    
    def _get_time_block(self, hour: int = None) -> str:
        """Get current time block"""
        if hour is None:
            hour = datetime.now().hour
        
        for block, (start, end) in self.TIME_BLOCKS.items():
            if start <= hour < end:
                return block.capitalize()
        return "Night"
    
    def add_entry(self, content: str, block: str = None, date: str = None):
        """Add entry to daily notes"""
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        if block is None:
            block = self._get_time_block()
        
        file_path = self.path / f"{date}.md"
        
        # Create file with header if new
        if not file_path.exists():
            with open(file_path, "w") as f:
                f.write(f"# Daily Notes - {date}\n\n")
        
        # Add entry
        with open(file_path, "a") as f:
            f.write(f"\n### {block}\n")
            f.write(f"- {content}\n")
    
    def get_today(self) -> str:
        """Get today's notes"""
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = self.path / f"{today}.md"
        
        if file_path.exists():
            return file_path.read_text()
        return ""
    
    def get_date(self, date: str) -> str:
        """Get notes for specific date"""
        file_path = self.path / f"{date}.md"
        
        if file_path.exists():
            return file_path.read_text()
        return ""
    
    def get_range(self, start_date: str, end_date: str) -> dict:
        """Get notes for date range"""
        notes = {}
        
        for file in self.path.glob("*.md"):
            date = file.stem
            if start_date <= date <= end_date:
                notes[date] = file.read_text()
        
        return notes
    
    def get_recent(self, days: int = 7) -> dict:
        """Get recent notes"""
        from datetime import timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        notes = {}
        for i in range(days):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            file_path = self.path / f"{date}.md"
            if file_path.exists():
                notes[date] = file_path.read_text()
        
        return notes

# CLI
if __name__ == "__main__":
    import sys
    
    notes = DailyNotes()
    
    if len(sys.argv) < 2:
        print("Daily Notes CLI")
        print("Usage:")
        print("  python3 daily_notes.py add <content>")
        print("  python3 daily_notes.py today")
        print("  python3 daily_notes.py recent [days]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "add":
        if len(sys.argv) < 3:
            print("Usage: python3 daily_notes.py add <content>")
            sys.exit(1)
        content = " ".join(sys.argv[2:])
        notes.add_entry(content)
        print(f"✓ Added to today's notes")
    
    elif action == "today":
        print(notes.get_today())
    
    elif action == "recent":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        recent = notes.get_recent(days)
        for date, content in recent.items():
            print(f"\n## {date}")
            print(content[:500])
