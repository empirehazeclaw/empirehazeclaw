"""
🗄️ DATABASE SETUP
================
PostgreSQL connection for future use
"""

import os

# For now, use SQLite as simple alternative
# Can migrate to PostgreSQL later

DB_CONFIG = {
    "type": "sqlite",  # or "postgresql"
    "path": "/home/clawbot/.openclaw/workspace/data/empire.db"
}

def get_connection():
    """Get database connection"""
    if DB_CONFIG["type"] == "sqlite":
        import sqlite3
        return sqlite3.connect(DB_CONFIG["path"])
    # PostgreSQL later
    return None

# Initialize tables
def init_db():
    os.makedirs(os.path.dirname(DB_CONFIG["path"]), exist_ok=True)
    conn = get_connection()
    c = conn.cursor()
    
    # Products table
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, name TEXT, price REAL, 
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Revenue table
    c.execute('''CREATE TABLE IF NOT EXISTS revenue
                 (id INTEGER PRIMARY KEY, source TEXT, amount REAL,
                  date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()
    print("🗄️ Database initialized!")

if __name__ == "__main__":
    init_db()
