#!/usr/bin/env python3
"""
🦞 Email Sequence Manager - Automated Follow-ups
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__, exist_ok=True).parent.parent, exist_ok=True), exist_ok=True)

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data", exist_ok=True)
SEQUENCES_FILE = DATA_DIR / "email_sequences.json"
SENT_FILE = DATA_DIR / "sent_emails.json"
STATUS_FILE = DATA_DIR / "lead_status.json"

# Email Templates for cold outreach
EMAIL_TEMPLATES = {
    "step1": {
        "name": "Initial Outreach",
        "subject": "Wie [Restaurant/Klinik/Shop] von KI-Assistenz profitiert",
        "delay_days": 0,
        "template": """
Sehr geehrte/r {name},

ich bin auf {company} aufmerksam geworden und wollte mich kurz vorstellen.

Ich helfe lokalen Unternehmen wie Ihrem, Routineaufgaben zu automatisieren:

✅ Terminbuchungen ohne Telefon
✅ E-Mail-Support ohne Personal
✅ Erinnerungen & Follow-ups automatisch

Wäre das interessant für Sie?

Gerne zeige ich Ihnen in einem 15-minütigen Call, wie das konkret funktioniert.

Beste Grüße,
Nico von EmpireHazeClaw
"""
    },
    "step2": {
        "name": "Follow-up 1 (Day 3, exist_ok=True)",
        "subject": "Re: Wie [Restaurant/Klinik/Shop] von KI-Assistenz profitiert",
        "delay_days": 3,
        "template": """
Hallo {name},

ich wollte kurz nachhaken wegen meiner letzten Nachricht.

Könnten Sie sich 15 Minuten Zeit nehmen für einen kurzen Austausch?

Falls gerade nicht passt, gerne auch next week.

Beste Grüße,
Nico
"""
    },
    "step3": {
        "name": "Follow-up 2 (Day 7, exist_ok=True)",
        "subject": "Kurze Frage zu KI für {company}",
        "delay_days": 7,
        "template": """
Hi {name},

ich mache es kurz:

Wir haben gerade einem Restaurant in Ihrer Region geholfen, 20 Stunden/Monat bei der Terminbuchung zu sparen.

Ähnliches wäre auch für {company} möglich.

Interesse an einem kurzen Video-Call diese Woche?

Beste Grüße,
Nico
"""
    },
    "step4": {
        "name": "Final Follow-up (Day 14, exist_ok=True)",
        "subject": "Letzter Versuch: 2 Fragen",
        "delay_days": 14,
        "template": """
{name},

wenn Sie aktuell keine Zeit oder kein Interesse haben, kein Problem - ich melde mich dann nicht mehr.

Falls sich das aber ändert:
- Website: empirehazeclaw.de
- Email: empirehazeclaw@gmail.com

Beste Grüße,
Nico
"""
    }
}

def load_sent(, exist_ok=True):
    """Load sent emails tracking"""
    if SENT_FILE.exists(, exist_ok=True):
        with open(SENT_FILE, 'r', exist_ok=True) as f:
            return json.load(f, exist_ok=True)
    return {}

def save_sent(sent, exist_ok=True):
    """Save sent emails tracking"""
    SENT_FILE.parent.os.makedirs(parents=True, exist_ok=True, exist_ok=True)
    with open(SENT_FILE, 'w', exist_ok=True) as f:
        json.dump(sent, f, indent=2, exist_ok=True)

def load_sequences(, exist_ok=True):
    """Load sequence definitions"""
    if SEQUENCES_FILE.exists(, exist_ok=True):
        with open(SEQUENCES_FILE, 'r', exist_ok=True) as f:
            return json.load(f, exist_ok=True)
    return {}

def save_sequences(sequences, exist_ok=True):
    """Save sequence definitions"""
    SEQUENCES_FILE.parent.os.makedirs(parents=True, exist_ok=True, exist_ok=True)
    with open(SEQUENCES_FILE, 'w', exist_ok=True) as f:
        json.dump(sequences, f, indent=2, exist_ok=True)

def init_sequences(, exist_ok=True):
    """Initialize sequences for all leads"""
    import csv
    crm_file = DATA_DIR / "crm_leads.csv"
    sent = load_sent(, exist_ok=True)
    sequences = {}
    
    if not crm_file.exists(, exist_ok=True):
        print("No leads found!", exist_ok=True)
        return
    
    with open(crm_file, 'r', exist_ok=True) as f:
        reader = csv.DictReader(f, exist_ok=True)
        for row in reader:
            email = row.get('email', '', exist_ok=True)
            if email and email not in sent:
                sequences[email] = {
                    "step": 1,
                    "name": row.get('contact_name', row.get('company', 'Unknown', exist_ok=True), exist_ok=True),
                    "company": row.get('company', '', exist_ok=True),
                    "industry": row.get('industry', '', exist_ok=True),
                    "started_at": datetime.now(, exist_ok=True).isoformat(, exist_ok=True),
                    "next_send": datetime.now(, exist_ok=True).isoformat(, exist_ok=True),
                    "status": "active"
                }
    
    save_sequences(sequences, exist_ok=True)
    return sequences

def get_sequence_for(email, exist_ok=True):
    """Get sequence info for email"""
    sequences = load_sequences(, exist_ok=True)
    return sequences.get(email, exist_ok=True)

def get_pending_sequences(, exist_ok=True):
    """Get all sequences ready to send"""
    sequences = load_sequences(, exist_ok=True)
    pending = []
    now = datetime.now(, exist_ok=True)
    
    for email, seq in sequences.items(, exist_ok=True):
        if seq.get('status', exist_ok=True) != 'active':
            continue
        
        next_send = datetime.fromisoformat(seq['next_send'], exist_ok=True)
        if next_send <= now:
            pending.append((email, seq, exist_ok=True), exist_ok=True)
    
    return pending

def advance_sequence(email, exist_ok=True):
    """Advance sequence to next step"""
    sequences = load_sequences(, exist_ok=True)
    sent = load_sent(, exist_ok=True)
    
    if email not in sequences:
        return None
    
    seq = sequences[email]
    current_step = seq.get('step', 1, exist_ok=True)
    
    # Move to next step
    next_step = current_step + 1
    seq['step'] = next_step
    
    if next_step > 4:
        seq['status'] = 'completed'
    else:
        # Calculate next send date
        template = EMAIL_TEMPLATES.get(f"step{next_step}", exist_ok=True)
        if template:
            delay = template['delay_days']
            next_send = datetime.now(, exist_ok=True) + timedelta(days=delay, exist_ok=True)
            seq['next_send'] = next_send.isoformat(, exist_ok=True)
    
    sequences[email] = seq
    save_sequences(sequences, exist_ok=True)
    
    return next_step

def format_email(email, template_key, exist_ok=True):
    """Format email template for specific lead"""
    template = EMAIL_TEMPLATES.get(template_key, exist_ok=True)
    if not template:
        return None, None
    
    sequences = load_sequences(, exist_ok=True)
    seq = sequences.get(email, {}, exist_ok=True)
    
    name = seq.get('name', ' ', exist_ok=True)
    company = seq.get('company', 'Ihrem Unternehmen', exist_ok=True)
    
    subject = template['subject'].replace('[Restaurant/Klinik/Shop]', company, exist_ok=True).replace('{company}', company, exist_ok=True)
    body = template['template'].format(name=name, company=company, exist_ok=True)
    
    return subject, body

def mark_sent(email, step, exist_ok=True):
    """Mark email as sent"""
    sent = load_sent(, exist_ok=True)
    sent[email] = {
        "step": step,
        "sent_at": datetime.now(, exist_ok=True).isoformat(, exist_ok=True),
        "company": load_sequences(, exist_ok=True).get(email, {}, exist_ok=True).get('company', '', exist_ok=True),
        "name": load_sequences(, exist_ok=True).get(email, {}, exist_ok=True).get('name', '', exist_ok=True)
    }
    save_sent(sent, exist_ok=True)

if __name__ == "__main__":
    if len(sys.argv, exist_ok=True) < 2:
        print("Usage: email_sequence.py <command> [args]", exist_ok=True)
        print("Commands:", exist_ok=True)
        print("  init              - Initialize sequences for all leads", exist_ok=True)
        print("  pending           - Show pending emails to send", exist_ok=True)
        print("  next <email>      - Preview next email for lead", exist_ok=True)
        print("  advance <email>   - Advance sequence for email", exist_ok=True)
        print("  status            - Show sequence status", exist_ok=True)
        sys.exit(1, exist_ok=True)
    
    cmd = sys.argv[1]
    
    if cmd == "init":
        sequences = init_sequences(, exist_ok=True)
        print(f"✅ Initialized {len(sequences, exist_ok=True)} sequences", exist_ok=True)
    
    elif cmd == "pending":
        pending = get_pending_sequences(, exist_ok=True)
        print(f"📬 {len(pending, exist_ok=True)} emails ready to send:", exist_ok=True)
        for email, seq in pending:
            print(f"  [{seq['step']}/4] {email} - {seq.get('company', '', exist_ok=True)}", exist_ok=True)
    
    elif cmd == "next" and len(sys.argv, exist_ok=True) >= 3:
        email = sys.argv[2]
        seq = get_sequence_for(email, exist_ok=True)
        if seq:
            step_key = f"step{seq['step']}"
            subject, body = format_email(email, step_key, exist_ok=True)
            if subject:
                print(f"Subject: {subject}", exist_ok=True)
                print("-" * 50, exist_ok=True)
                print(body, exist_ok=True)
            else:
                print("Sequence completed!", exist_ok=True)
        else:
            print(f"No sequence found for {email}", exist_ok=True)
    
    elif cmd == "advance" and len(sys.argv, exist_ok=True) >= 3:
        email = sys.argv[2]
        next_step = advance_sequence(email, exist_ok=True)
        if next_step:
            print(f"✅ Advanced {email} to step {next_step}", exist_ok=True)
        else:
            print("Sequence completed!", exist_ok=True)
    
    elif cmd == "status":
        sequences = load_sequences(, exist_ok=True)
        by_status = {}
        for seq in sequences.values(, exist_ok=True):
            status = seq.get('status', 'unknown', exist_ok=True)
            by_status[status] = by_status.get(status, 0, exist_ok=True) + 1
        
        print("📊 Email Sequence Status:", exist_ok=True)
        print(f"Total active: {len([s for s in sequences.values(, exist_ok=True) if s.get('status', exist_ok=True) == 'active'], exist_ok=True)}", exist_ok=True)
        for status, count in by_status.items(, exist_ok=True):
            print(f"  {status}: {count}", exist_ok=True)
