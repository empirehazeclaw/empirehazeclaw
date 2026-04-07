#!/usr/bin/env python3
"""
Central SQLite Database
- Unified data storage for all services
- Clients, Leads, Tasks, Invoices
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
DB_PATH = WORKSPACE / "data" / "central.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema"""
    conn = get_db()
    c = conn.cursor()
    
    # Clients table
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        name TEXT,
        product TEXT,
        purchase_date TEXT,
        status TEXT DEFAULT 'active',
        created TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Leads table
    c.execute('''CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        email TEXT,
        industry TEXT,
        city TEXT,
        status TEXT DEFAULT 'new',
        source TEXT,
        contacted_date TEXT,
        notes TEXT,
        created TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tasks table
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent TEXT,
        task TEXT,
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'pending',
        result TEXT,
        created TEXT DEFAULT CURRENT_TIMESTAMP,
        completed TEXT
    )''')
    
    # Invoices table
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT UNIQUE,
        customer_email TEXT,
        customer_name TEXT,
        product TEXT,
        amount REAL,
        vat REAL,
        status TEXT DEFAULT 'pending',
        created TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()
    return True

# Client operations
def add_client(email, name, product):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO clients (email, name, product) VALUES (?, ?, ?)", (email, name, product))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_clients():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM clients ORDER BY created DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Lead operations
def add_lead(company, email, industry, city, source="crawler"):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO leads (company, email, industry, city, source) VALUES (?, ?, ?, ?, ?)",
              (company, email, industry, city, source))
    conn.commit()
    conn.close()

def get_leads(status=None):
    conn = get_db()
    c = conn.cursor()
    if status:
        c.execute("SELECT * FROM leads WHERE status=? ORDER BY created DESC", (status,))
    else:
        c.execute("SELECT * FROM leads ORDER BY created DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Task operations
def add_task(agent, task, priority="medium"):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO tasks (agent, task, priority) VALUES (?, ?, ?)", (agent, task, priority))
    conn.commit()
    conn.close()

def get_tasks(status=None):
    conn = get_db()
    c = conn.cursor()
    if status:
        c.execute("SELECT * FROM tasks WHERE status=? ORDER BY created DESC", (status,))
    else:
        c.execute("SELECT * FROM tasks ORDER BY created DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Invoice operations
def add_invoice(invoice_number, customer_email, customer_name, product, amount):
    conn = get_db()
    c = conn.cursor()
    vat = amount * 0.19
    c.execute("INSERT INTO invoices (invoice_number, customer_email, customer_name, product, amount, vat) VALUES (?, ?, ?, ?, ?, ?)",
              (invoice_number, customer_email, customer_name, product, amount, vat))
    conn.commit()
    conn.close()

def get_invoices(status=None):
    conn = get_db()
    c = conn.cursor()
    if status:
        c.execute("SELECT * FROM invoices WHERE status=? ORDER BY created DESC", (status,))
    else:
        c.execute("SELECT * FROM invoices ORDER BY created DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Stats
def get_stats():
    conn = get_db()
    c = conn.cursor()
    
    stats = {}
    
    c.execute("SELECT COUNT(*) FROM clients")
    stats['clients'] = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM leads")
    stats['leads'] = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM tasks")
    stats['tasks'] = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM invoices")
    stats['invoices'] = c.fetchone()[0]
    
    c.execute("SELECT SUM(amount) FROM invoices")
    stats['revenue'] = c.fetchone()[0] or 0
    
    conn.close()
    return stats

# CLI
if __name__ == "__main__":
    import sys
    
    init_db()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "stats":
            stats = get_stats()
            print("📊 Database Stats:")
            print(f"   Clients: {stats['clients']}")
            print(f"   Leads: {stats['leads']}")
            print(f"   Tasks: {stats['tasks']}")
            print(f"   Invoices: {stats['invoices']}")
            print(f"   Revenue: €{stats['revenue']:.2f}")
        
        elif cmd == "clients":
            for c in get_clients():
                print(f"   {c['name']} - {c['email']} - {c['product']}")
        
        elif cmd == "leads":
            for l in get_leads():
                print(f"   {l['company']} - {l['industry']} - {l['status']}")
        
        elif cmd == "invoices":
            for i in get_invoices():
                print(f"   {i['invoice_number']} - €{i['amount']} - {i['status']}")
    else:
        print("Central Database CLI")
        print("Usage: central_db.py [stats|clients|leads|invoices]")
