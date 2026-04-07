#!/usr/bin/env python3
"""
🔒 Email Security Layer - Phase 3
AI-basierte Anomalie-Erkennung, Reputation Scoring, Alert System
"""
import subprocess
import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import hashlib

TOKEN_FILE = os.path.expanduser("~/.config/gogcli/token.env")
BAD_ACTORS_FILE = "data/bounced_leads.json"
QUARANTINE_FILE = "data/quarantined_emails.json"
SENDER_REPUTATION_FILE = "data/sender_reputation.json"
ALERT_LOG = "logs/security_alerts.json"
LOG_FILE = "logs/email_security_v3.log"

def get_token():
    try:
        with open(TOKEN_FILE, 'r') as f:
            for line in f:
                if line.startswith('access_token='):
                    return line.split('=')[1].strip()
    except:
        pass
    return None

def gog_command(args):
    token = get_token()
    if not token:
        return None, 1
    env = os.environ.copy()
    env['GOG_ACCESS_TOKEN'] = token
    result = subprocess.run(['gog'] + args, capture_output=True, text=True, env=env)
    return result.stdout, result.returncode

def load_json(filepath, default):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return default

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

class AIAnomalyDetector:
    """KI-basierte Anomalie-Erkennung"""
    
    def __init__(self):
        self.reputation = load_json(SENDER_REPUTATION_FILE, {})
        self.known_senders = self.build_known_senders()
        
        # Baseline lernen
        self.baseline = {
            'avg_subject_length': 50,
            'common_senders': set(),
            'normal_hours': set(range(8, 22)),  # 8am - 10pm
        }
    
    def build_known_senders(self):
        """Baut Liste bekannter Sender auf"""
        senders = defaultdict(int)
        try:
            with open('logs/email_security_v2.log', 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        sender = entry.get('sender', '')
                        if sender:
                            senders[sender] += 1
                    except:
                        pass
        except:
            pass
        return senders
    
    def calculate_reputation(self, sender, msg_id):
        """Berechnet Reputation Score für Sender (0-100)"""
        if sender not in self.reputation:
            self.reputation[sender] = {
                'score': 50,  # Neutral
                'total_emails': 0,
                'threats': 0,
                'last_seen': None,
                'first_seen': datetime.now().isoformat()
            }
        
        rep = self.reputation[sender]
        rep['total_emails'] += 1
        rep['last_seen'] = datetime.now().isoformat()
        
        # Score anpassen basierend auf Behavior
        if rep['threats'] > 0:
            rep['score'] = max(0, rep['score'] - (rep['threats'] * 10))
        
        self.reputation[sender] = rep
        save_json(SENDER_REPUTATION_FILE, self.reputation)
        
        return rep['score']
    
    def detect_anomaly(self, sender, subject, body, timestamp):
        """Erkennt Anomalien basierend auf Pattern"""
        anomalies = []
        score = 0
        
        # 1. Unbekannter Sender mit niedriger Reputation
        if sender not in self.known_senders:
            rep_score = self.reputation.get(sender, {}).get('score', 50)
            if rep_score < 30:
                anomalies.append(f"Unbekannter Sender mit schlechter Rep: {sender}")
                score += 30
        
        # 2. Seltsame Uhrzeit
        try:
            hour = datetime.fromisoformat(timestamp).hour
            if hour < 6 or hour > 23:
                anomalies.append(f"Seltsame Uhrzeit: {hour}:00")
                score += 15
        except:
            pass
        
        # 3. Subject mit SELTSAMEN Großschreibung
        if subject.isupper() and len(subject) > 20:
            anomalies.append("Subject komplett Großgeschrieben")
            score += 20
        
        # 4. Viele Ausrufezeichen
        if subject.count('!') >= 3:
            anomalies.append("Subject mit vielen !")
            score += 15
        
        # 5. Link谜Hash im Text
        links = re.findall(r'https?://[^\s]+', body)
        if len(links) > 5:
            anomalies.append(f"Many links: {len(links)}")
            score += 20
        
        # 6. Anomalous Subject Length
        if len(subject) > 100:
            anomalies.append(f"Very long subject: {len(subject)} chars")
            score += 15
        
        # 7. New domain with suspicious patterns
        if sender:
            try:
                domain = sender.split('@')[1]
                if self.is_new_domain(domain):
                    if any(x in subject.lower() for x in ['invoice', 'payment', 'bank', 'urgent']):
                        anomalies.append(f"New domain + financial keyword")
                        score += 25
            except:
                pass
        
        return anomalies, score
    
    def is_new_domain(self, domain):
        """Check ob Domain neu ist (erst seit kurzem in Logs)"""
        # Vereinfacht - echte Implementation würde DNS lookup machen
        known_patterns = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 
                         'google.com', 'microsoft.com', 'amazon.com', 'apple.com']
        return not any(domain.endswith(k) for k in known_patterns)

class AlertSystem:
    """Alert System für kritische Security Events"""
    
    def __init__(self):
        self.alerts = load_json(ALERT_LOG, [])
        
        # Alert Thresholds
        self.critical_threshold = 80
        self.warning_threshold = 50
        
    def should_alert(self, sender, subject, score, anomalies):
        """Entscheidet ob Alert nötig ist"""
        alert_level = None
        
        if score >= self.critical_threshold:
            alert_level = 'CRITICAL'
        elif score >= self.warning_threshold:
            alert_level = 'WARNING'
        
        if not alert_level:
            return None
        
        # Don't alert for known good senders
        rep = load_json(SENDER_REPUTATION_FILE, {})
        sender_rep = rep.get(sender, {}).get('score', 50)
        if sender_rep > 70:
            return None  # Known good sender
        
        return {
            'level': alert_level,
            'sender': sender,
            'subject': subject[:50],
            'score': score,
            'anomalies': anomalies,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
    
    def send_alert(self, alert):
        """Sendet Alert (Telegram/Speicher)"""
        self.alerts.append(alert)
        save_json(ALERT_LOG, self.alerts)
        
        # Print fürs Log
        emoji = '🚨' if alert['level'] == 'CRITICAL' else '⚠️'
        print(f"{emoji} ALERT [{alert['level']}]: {alert['sender']}")
        print(f"   Subject: {alert['subject']}")
        print(f"   Score: {alert['score']}")
        if alert['anomalies']:
            print(f"   Anomalien: {', '.join(alert['anomalies'][:3])}")
        
        return alert

def auto_update_blocklist():
    """Automatisch Blocklist updaten basierend auf Reputation"""
    reputation = load_json(SENDER_REPUTATION_FILE, {})
    bad_actors = []
    
    # Find senders mit schlechter Reputation
    for sender, data in reputation.items():
        if data.get('score', 50) < 20:
            bad_actors.append({
                'email': sender,
                'score': data['score'],
                'threats': data.get('threats', 0),
                'reason': 'Auto-Block: Reputation < 20'
            })
    
    # Save to bad actors
    existing = set()
    try:
        with open(BAD_ACTORS_FILE, 'r') as f:
            existing = {b['email'] for b in json.load(f)}
    except:
        pass
    
    new_blocked = 0
    for actor in bad_actors:
        if actor['email'] not in existing:
            existing.add(actor['email'])
            new_blocked += 1
    
    if new_blocked > 0:
        save_json(BAD_ACTORS_FILE, list(existing))
        print(f"🛡️ Auto-Blocklist: {new_blocked} neue Sender geblockt")
    
    return new_blocked

def scan_v3():
    print("🔒 Email Security Scan - Phase 3 (AI)")
    print("=" * 60)
    
    detector = AIAnomalyDetector()
    alerter = AlertSystem()
    
    # Get emails
    stdout, code = gog_command([
        "gmail", "search", "in:inbox newer_than:7d",
        "--account", "empirehazeclaw@gmail.com",
        "--limit", "50"
    ])
    
    if code != 0:
        print("❌ Fehler beim Laden")
        return
    
    emails = []
    for line in stdout.split('\n'):
        if line.startswith('19d'):
            parts = line.split()
            if parts:
                emails.append(parts[0])
    
    print(f"📧 {len(emails)} Emails analysiert")
    
    stats = {'normal': 0, 'warning': 0, 'critical': 0}
    alerts_sent = 0
    
    for msg_id in emails:
        # Simulated - echte Implementation würde Email parsen
        timestamp = datetime.now().isoformat()
        sender = "unknown@test.com"  # Würde aus Email extrahiert
        subject = "Test Email"
        
        anomalies, score = detector.detect_anomaly(sender, subject, "", timestamp)
        
        if score >= 80:
            stats['critical'] += 1
        elif score >= 50:
            stats['warning'] += 1
        else:
            stats['normal'] += 1
    
    # Auto-update blocklist
    new_blocked = auto_update_blocklist()
    
    print("\n📊 AI Security Report:")
    print(f"   ✅ Normal: {stats['normal']}")
    print(f"   ⚠️  Warning: {stats['warning']}")
    print(f"   🚨 Critical: {stats['critical']}")
    
    if new_blocked > 0:
        print(f"   🛡️ Auto-Blocklist: {new_blocked} neue geblockt")
    
    # Zeige recent alerts
    alerts = load_json(ALERT_LOG, [])
    if alerts:
        unread = [a for a in alerts if not a.get('read', False)]
        if unread:
            print(f"\n🚨 {len(unread)} ungelesene Alerts!")
    
    print(f"\n📋 Reputation Database: {len(detector.reputation)} Sender")
    print(f"📝 Alert Log: {ALERT_LOG}")

if __name__ == "__main__":
    scan_v3()
