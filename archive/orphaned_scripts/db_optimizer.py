#!/usr/bin/env python3
"""
Database Performance Optimizer
"""
import sqlite3

def create_indexes():
    """Create performance indexes"""
    conn = sqlite3.connect('data/memory/memory.db')
    c = conn.cursor()
    
    # Indexes for faster queries
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_leads_date ON leads(date)",
        "CREATE INDEX IF NOT EXISTS idx_content_date ON content(date)",
        "CREATE INDEX IF NOT EXISTS idx_emails_date ON emails(date)",
    ]
    
    for idx in indexes:
        try:
            c.execute(idx)
            print(f"✅ Created: {idx.split('IF NOT EXISTS ')[1]}")
        except Exception as e:
            print(f"❌ {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_indexes()
