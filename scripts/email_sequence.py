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
sys.path.insert(0, str(Path(__file__).parent.parent))

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data")
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
        "name": "Follow-up 1 (Day 3)",
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
        "name": "Follow-up 2 (Day 7)",
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
        "name": "Final Follow-up (Day 14)",
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

def load_sent():
    """Load sent emails tracking"""
    if SENT_FILE.exists():
        with open(SENT_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_sent(sent):
    """Save sent emails tracking"""
    SENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SENT_FILE, 'w') as f:
        json.dump(sent, f, indent=2)

def load_sequences():
    """Load sequence definitions"""
    if SEQUENCES_FILE.exists():
        with open(SEQUENCES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_sequences(sequences):
    """Save sequence definitions"""
    SEQUENCES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SEQUENCES_FILE, 'w') as f:
        json.dump(sequences, f, indent=2)

def init_sequences():
    """Initialize sequences for all leads"""
    import csv
    crm_file = DATA_DIR / "crm_leads.csv"
    sent = load_sent()
    sequences = {}
    
    if not crm_file.exists():
        print("No leads found!")
        return
    
    with open(crm_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '')
            if email and email not in sent:
                sequences[email] = {
                    "step": 1,
                    "name": row.get('contact_name', row.get('company', 'Unknown')),
                    "company": row.get('company', ''),
                    "industry": row.get('industry', ''),
                    "started_at": datetime.now().isoformat(),
                    "next_send": datetime.now().isoformat(),
                    "status": "active"
                }
    
    save_sequences(sequences)
    return sequences

def get_sequence_for(email):
    """Get sequence info for email"""
    sequences = load_sequences()
    return sequences.get(email)

def get_pending_sequences():
    """Get all sequences ready to send"""
    sequences = load_sequences()
    pending = []
    now = datetime.now()
    
    for email, seq in sequences.items():
        if seq.get('status') != 'active':
            continue
        
        next_send = datetime.fromisoformat(seq['next_send'])
        if next_send <= now:
            pending.append((email, seq))
    
    return pending

def advance_sequence(email):
    """Advance sequence to next step"""
    sequences = load_sequences()
    sent = load_sent()
    
    if email not in sequences:
        return None
    
    seq = sequences[email]
    current_step = seq.get('step', 1)
    
    # Move to next step
    next_step = current_step + 1
    seq['step'] = next_step
    
    if next_step > 4:
        seq['status'] = 'completed'
    else:
        # Calculate next send date
        template = EMAIL_TEMPLATES.get(f"step{next_step}")
        if template:
            delay = template['delay_days']
            next_send = datetime.now() + timedelta(days=delay)
            seq['next_send'] = next_send.isoformat()
    
    sequences[email] = seq
    save_sequences(sequences)
    
    return next_step

def format_email(email, template_key):
    """Format email template for specific lead"""
    template = EMAIL_TEMPLATES.get(template_key)
    if not template:
        return None, None
    
    sequences = load_sequences()
    seq = sequences.get(email, {})
    
    name = seq.get('name', ' ')
    company = seq.get('company', 'Ihrem Unternehmen')
    
    subject = template['subject'].replace('[Restaurant/Klinik/Shop]', company).replace('{company}', company)
    body = template['template'].format(name=name, company=company)
    
    return subject, body

def mark_sent(email, step):
    """Mark email as sent"""
    sent = load_sent()
    sent[email] = {
        "step": step,
        "sent_at": datetime.now().isoformat(),
        "company": load_sequences().get(email, {}).get('company', ''),
        "name": load_sequences().get(email, {}).get('name', '')
    }
    save_sent(sent)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: email_sequence.py <command> [args]")
        print("Commands:")
        print("  init              - Initialize sequences for all leads")
        print("  pending           - Show pending emails to send")
        print("  next <email>      - Preview next email for lead")
        print("  advance <email>   - Advance sequence for email")
        print("  status            - Show sequence status")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "init":
        sequences = init_sequences()
        print(f"✅ Initialized {len(sequences)} sequences")
    
    elif cmd == "pending":
        pending = get_pending_sequences()
        print(f"📬 {len(pending)} emails ready to send:")
        for email, seq in pending:
            print(f"  [{seq['step']}/4] {email} - {seq.get('company', '')}")
    
    elif cmd == "next" and len(sys.argv) >= 3:
        email = sys.argv[2]
        seq = get_sequence_for(email)
        if seq:
            step_key = f"step{seq['step']}"
            subject, body = format_email(email, step_key)
            if subject:
                print(f"Subject: {subject}")
                print("-" * 50)
                print(body)
            else:
                print("Sequence completed!")
        else:
            print(f"No sequence found for {email}")
    
    elif cmd == "advance" and len(sys.argv) >= 3:
        email = sys.argv[2]
        next_step = advance_sequence(email)
        if next_step:
            print(f"✅ Advanced {email} to step {next_step}")
        else:
            print("Sequence completed!")
    
    elif cmd == "status":
        sequences = load_sequences()
        by_status = {}
        for seq in sequences.values():
            status = seq.get('status', 'unknown')
            by_status[status] = by_status.get(status, 0) + 1
        
        print("📊 Email Sequence Status:")
        print(f"Total active: {len([s for s in sequences.values() if s.get('status') == 'active'])}")
        for status, count in by_status.items():
            print(f"  {status}: {count}")
