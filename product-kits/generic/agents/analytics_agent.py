#!/usr/bin/env python3
"""
📊 Analytics AI Agent - Generic Version
Erstellt Reports und Analysen
"""
import json
import os
from datetime import datetime, timedelta

CONFIG_FILE = "config/analytics_config.json"
STATS_DIR = "data/"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "report_schedule": "0 9 * * *",
        "metrics": ["emails", "leads", "tickets"]
    }

def get_email_stats():
    """Email Statistiken"""
    log_file = os.path.join(STATS_DIR, "email_log.json")
    if not os.path.exists(log_file):
        return {"total": 0, "today": 0, "week": 0}
    
    with open(log_file) as f:
        emails = json.load(f)
    
    now = datetime.now()
    today = now.date()
    week_ago = today - timedelta(days=7)
    
    total = len(emails)
    today_count = sum(1 for e in emails if datetime.fromisoformat(e["timestamp"]).date() == today)
    week_count = sum(1 for e in emails if datetime.fromisoformat(e["timestamp"]).date() >= week_ago)
    
    return {"total": total, "today": today_count, "week": week_count}

def get_ticket_stats():
    """Support Ticket Statistiken"""
    ticket_file = os.path.join(STATS_DIR, "support_tickets.json")
    if not os.path.exists(ticket_file):
        return {"total": 0, "open": 0, "closed": 0}
    
    with open(ticket_file) as f:
        tickets = json.load(f)
    
    return {
        "total": len(tickets),
        "open": sum(1 for t in tickets if t["status"] == "open"),
        "closed": sum(1 for t in tickets if t["status"] == "closed")
    }

def generate_daily_report():
    """Erstelle täglichen Report"""
    email_stats = get_email_stats()
    ticket_stats = get_ticket_stats()
    
    report = f"""
📊 Tagesreport - {datetime.now().strftime('%Y-%m-%d')}

📧 EMAILS
- Gesamt beantwortet: {email_stats['total']}
- Heute: {email_stats['today']}
- Diese Woche: {email_stats['week']}

🎫 SUPPORT TICKETS
- Gesamt: {ticket_stats['total']}
- Offen: {ticket_stats['open']}
- Geschlossen: {ticket_stats['closed']}

💡 INSIGHTS
"""
    if email_stats['today'] > 10:
        report += "- Hohe Email-Aktivität heute!\n"
    if ticket_stats['open'] > 5:
        report += "- Mehrere offene Tickets - Follow-up nötig\n"
    
    report += "\n✅ Report generiert"
    
    return report

def generate_weekly_report():
    """Erstelle wöchentlichen Report"""
    email_stats = get_email_stats()
    ticket_stats = get_ticket_stats()
    
    report = f"""
📈 Wochenreport - KW{datetime.now().isocalendar()[1]}

📧 EMAILS (diese Woche)
- Beantwortet: {email_stats['week']}
- Ø pro Tag: {email_stats['week'] / 7:.1f}

🎫 TICKETS
- Neu: {ticket_stats['total']}
- Offen: {ticket_stats['open']}
- Geschlossen: {ticket_stats['closed']}

📊 TRENDS
"""
    if email_stats['week'] > 50:
        report += "- Email-Volumen: Hoch\n"
    elif email_stats['week'] > 20:
        report += "- Email-Volumen: Normal\n"
    else:
        report += "- Email-Volumen: Niedrig\n"
    
    if ticket_stats['open'] == 0:
        report += "- Alle Tickets geschlossen! 👍\n"
    
    return report

def run_analytics(report_type="daily"):
    """Hauptfunktion"""
    config = load_config()
    
    if report_type == "daily":
        return generate_daily_report()
    elif report_type == "weekly":
        return generate_weekly_report()
    else:
        return {"email": get_email_stats(), "tickets": get_ticket_stats()}

if __name__ == "__main__":
    print("📊 Analytics Agent gestartet...")
    
    daily = run_analytics("daily")
    print(daily)
    
    weekly = run_analytics("weekly")
    print(weekly)
    
    print("✅ Analytics Agent fertig")
