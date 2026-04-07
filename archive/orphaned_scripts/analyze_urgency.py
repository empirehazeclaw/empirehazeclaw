import os
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace')

def check_urgency():
    issues = []
    
    # 1. Payment Gateway Check
    stripe_link = "buy.stripe.com"
    with open(WORKSPACE / '/var/www/empirehazeclaw-store/prompt-cache.html', 'r') as f:
        if stripe_link not in f.read():
            issues.append("CRITICAL: Keine Zahlungsabwicklung auf der Prompt-Cache Sales-Page!")
            
    # 2. Inbound Comm Check (Gmail)
    try:
        # Pseudo-Check ob OAuth existiert (da wir es noch nicht gemacht haben)
        with open(os.path.expanduser('~/.gog/credentials.json'), 'r') as f:
            pass
    except FileNotFoundError:
        issues.append("URGENT (Prio 1 morgen): Inbound Mails von Leads landen im Nirgendwo! 'gog auth add empirehazeclaw@gmail.com' MUSS gemacht werden.")

    # 3. Social Media Blockade Check
    log_files = list((WORKSPACE / 'logs').glob('*.log'))
    twitter_blocked = False
    for log in log_files:
        try:
            with open(log, 'r') as f:
                content = f.read()
                if "403 Forbidden" in content and "xurl" in content:
                    twitter_blocked = True
        except:
            pass
    if twitter_blocked:
        issues.append("URGENT: X/Twitter Account hat Post-Sperre (403 Forbidden). Die Content-Maschine postet aktuell ins Leere.")

    # 4. Error Rate Check
    error_count = 0
    if (WORKSPACE / 'logs/logger.log').exists():
        with open(WORKSPACE / 'logs/logger.log', 'r') as f:
            error_count = f.read().count("ERROR")
    if error_count > 10:
        issues.append(f"WARNING: Hohe Fehler-Rate in den Logs ({error_count} Errors).")

    return issues

if __name__ == "__main__":
    issues = check_urgency()
    if issues:
        print("🚨 DRINGENDE BAUSTELLEN:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("✅ Keine kritischen Baustellen gefunden.")
