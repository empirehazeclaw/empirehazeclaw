#!/usr/bin/env python3
"""
Email Scam Filter - EXPANDED VERSION
Schützt vor Scams + lernt + Reportet + Analytics
Nutzung: python3 email_scam_filter_v2.py
"""

import re
import json
import os
from datetime import datetime, timedelta
from collections import Counter

CONFIG_FILE = "/home/clawbot/.openclaw/config/email_scam_config.json"
LOG_FILE = "/home/clawbot/.openclaw/logs/email_scam.log"
STATS_FILE = "/home/clawbot/.openclaw/data/email_scam_stats.json"

# ================== SCAM PATTERNS ==================

SCAM_PATTERNS = {
    "CRITICAL": [
        # Urgency/Fear
        r"(immediately|urgent|within \d+ hours?|within \d+ days?)",
        r"(account will be|shall be|will be) (closed|deleted|suspended|terminated)",
        r"(final|last) (warning|notice|reminder)",
        r"(fail|failure) to (respond|act|comply|verify)",
        r"(legal|police|law) (action|notice|warning|investigation)",
        
        # Account Security
        r"(suspended|locked|restricted|disabled) (account|profile|shop)",
        r"(unusual|unauthorized|suspicious) (activity|login|access)",
        r"(password|credential|login) (reset|change|update|expire)",
        
        # Fake Links
        r"click (here|now|immediately|below)",
        r"(verify|confirm|validate|unlock) (your|account|identity)",
        
        # Payment
        r"(payment (information|details|method)|bank (information|details))",
        r"(gift card|bitcoin|cryptocurrency|western union)",
        r"(refund|compensation|bonus|prize).*(available|pending|claim)",
        
        # Too good to be true
        r"(congratulations|you (have|ve) (won|been selected))",
        r"(lottery|prize|reward|inheritance).*(won|claim|receive)",
        r"(make|earn).*(money|profit|income).*(fast|quick|easy|overnight)",
    ],
    
    "HIGH": [
        # Etsy Specific
        r"(etsy|etsy\.com).*(suspended|closed|restricted|terminated)",
        r"etsy.*(tax|legal|compliance) (issue|problem|requirement|notice)",
        r"etsy.*(payment|earnings|funds).*(held|frozen|pending|review)",
        r"etsy.*(seller|shop|listing).*(violation|breach|warning)",
        r"(etsy|etsy\.com).*(security|department|support).*@",
        
        # Fiverr Specific
        r"fiverr.*(suspended|blocked|terminated|disabled)",
        r"fiverr.*(verify|confirm|validate).*(identity|account|profile)",
        r"fiverr.*(payment|earnings|earnings).*(frozen|held|pending)",
        r"fiverr.*(level|seller level|reputation).*(downgraded|removed|revoked)",
        
        # Amazon Specific
        r"amazon.*(account|seller).*(suspended|restricted|review)",
        r"amazon.*(payment|order).*(problem|issue|hold)",
    ],
    
    "MEDIUM": [
        # Suspicious Domains
        r"@.*(verify|secure|account|support)\.",
        r"@.*(info|help|service)\..*\.",
        r"(http|https)://(?!.*\.(etsy|fiverr|amazon|google|paypal|ebay)\.com)",
        
        # Poor Grammar/Writing
        r"(dear|dear valued|dear customer).*(kindly|urgently|immediately)",
        
        # Generic
        r"(update|verify) (your|account|information|details)",
    ],
    
    "LOW": [
        # Warnings
        r"(phishing|scam|fraud|fake).*(alert|warning|notice)",
    ]
}

# ================== WHITELIST ==================

WHITELIST = {
    "domains": [
        r".*@etsy\.com$",
        r".*@fiverr\.com$",
        r".*@mail\.etsy\.com$",
        r".*@mail\.fiverr\.com$",
        r".*@notifications\.etsy\.com$",
        r".*@accounts\.etsy\.com$",
        r".*@amazon\.com$",
        r".*@amazon\.de$",
        r".*@paypal\.com$",
        r".*@paypal\.de$",
        r".*@google\.com$",
        r".*@googlemail\.com$",
        r".*@youtube\.com$",
        r".*@github\.com$",
        r".*@gitlab\.com$",
        r".*@discord\.com$",
        r".*@slack\.com$",
        r".*@printful\.com$",
        r".*@printify\.com$",
    ],
    
    "subjects": [
        r"New order received",
        r"You received a payment",
        r"Order confirmed",
        r"Delivery update",
        r"Your item has shipped",
    ]
}

# ================== BLACKLIST ==================

BLACKLIST = {
    "domains": [
        r".*@.*\.tk$",
        r".*@.*\.ml$",
        r".*@.*\.ga$",
        r".*@.*\.cf$",
        r".*@.*\.gq$",
        r".*@account-security\..*",
        r".*@verify-account\..*",
        r".*@secure-login\..*",
        r".*@etsy-verify\..*",
        r".*@fiverr-support\..*",
    ],
    
    "keywords": [
        "scam", "phishing", "fake", "fraud",
    ]
}

# ================== ANALYZER ==================

class EmailScamFilter:
    def __init__(self):
        self.load_config()
        self.load_stats()
    
    def load_config(self):
        """Lade Konfiguration"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                self.config = json.load(f)
        else:
            self.config = {
                "actions": {
                    "critical": "block",
                    "high": "spam",
                    "medium": "label",
                    "low": "none"
                },
                "notifications": {
                    "telegram": False,
                    "email": False
                },
                "learning": True
            }
    
    def load_stats(self):
        """Lade Statistiken"""
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE) as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                "total_scanned": 0,
                "blocked": 0,
                "spam": 0,
                "warnings": 0,
                "safe": 0,
                "by_level": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
                "recent_blocks": []
            }
    
    def save_stats(self):
        """Speichere Statistiken"""
        os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
        with open(STATS_FILE, "w") as f:
            json.dump(self.stats, f, indent=2)
    
    def is_whitelisted(self, sender: str, subject: str) -> bool:
        """Prüfe Whitelist"""
        for pattern in WHITELIST["domains"]:
            if re.search(pattern, sender, re.IGNORECASE):
                return True
        
        for pattern in WHITELIST["subjects"]:
            if re.search(pattern, subject, re.IGNORECASE):
                return True
        
        return False
    
    def is_blacklisted(self, sender: str, body: str) -> bool:
        """Prüfe Blacklist"""
        for pattern in BLACKLIST["domains"]:
            if re.search(pattern, sender, re.IGNORECASE):
                return True
        
        text = f"{sender} {body}".lower()
        for keyword in BLACKLIST["keywords"]:
            if keyword in text:
                return True
        
        return False
    
    def analyze(self, sender: str, subject: str, body: str) -> dict:
        """Analysiere E-Mail"""
        full_text = f"{sender} {subject} {body}".lower()
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "subject": subject,
            "risk_level": "SAFE",
            "score": 0,
            "findings": [],
            "action": "none",
            "is_whitelisted": False,
            "is_blacklisted": False
        }
        
        # Update stats
        self.stats["total_scanned"] += 1
        
        # 1. Check Whitelist
        if self.is_whitelisted(sender, subject):
            result["is_whitelisted"] = True
            result["risk_level"] = "SAFE"
            result["action"] = "none"
            self.stats["safe"] += 1
            return result
        
        # 2. Check Blacklist
        if self.is_blacklisted(sender, body):
            result["is_blacklisted"] = True
            result["risk_level"] = "CRITICAL"
            result["score"] = 100
            result["findings"].append("Blacklisted sender/domain")
            result["action"] = "block"
            self.stats["blocked"] += 1
            self.stats["by_level"]["CRITICAL"] += 1
            self._add_recent_block(sender, subject, "Blacklist")
            self.save_stats()
            return result
        
        # 3. Check Patterns
        scores = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for level, patterns in SCAM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    score_map = {"CRITICAL": 40, "HIGH": 25, "MEDIUM": 15, "LOW": 5}
                    scores[level] += score_map[level]
                    result["findings"].append(f"{level}: {pattern[:50]}")
        
        # Calculate total score
        total_score = sum(scores.values())
        result["score"] = min(total_score, 100)
        
        # Determine risk level
        if total_score >= 60 or scores["CRITICAL"] >= 40:
            result["risk_level"] = "CRITICAL"
            result["action"] = "block"
            self.stats["blocked"] += 1
            self.stats["by_level"]["CRITICAL"] += 1
        elif total_score >= 35 or scores["HIGH"] >= 25:
            result["risk_level"] = "HIGH"
            result["action"] = "spam"
            self.stats["spam"] += 1
            self.stats["by_level"]["HIGH"] += 1
        elif total_score >= 15:
            result["risk_level"] = "MEDIUM"
            result["action"] = "label"
            self.stats["warnings"] += 1
            self.stats["by_level"]["MEDIUM"] += 1
        else:
            result["risk_level"] = "SAFE"
            result["action"] = "none"
            self.stats["safe"] += 1
        
        # Log blocked
        if result["action"] in ["block", "spam"]:
            self._add_recent_block(sender, subject, result["risk_level"])
        
        self.save_stats()
        return result
    
    def _add_recent_block(self, sender: str, subject: str, reason: str):
        """Füge Block zur Recent-Liste hinzu"""
        entry = {
            "sender": sender[:50],
            "subject": subject[:50],
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        self.stats["recent_blocks"].insert(0, entry)
        self.stats["recent_blocks"] = self.stats["recent_blocks"][:50]  # Keep last 50
    
    def get_stats(self) -> dict:
        """Gib Statistiken zurück"""
        return self.stats
    
    def get_report(self) -> str:
        """Erstelle Report"""
        stats = self.stats
        total = stats["total_scanned"] or 1
        
        report = f"""
📧 Email Scam Filter - Report
================================
Gescannte E-Mails: {stats['total_scanned']}

🚫 Blockiert: {stats['blocked']} ({stats['blocked']/total*100:.1f}%)
📧 Als Spam: {stats['spam']} ({stats['spam']/total*100:.1f}%)
⚠️ Warnungen: {stats['warnings']} ({stats['warnings']/total*100:.1f}%)
✅ Sicher: {stats['safe']} ({stats['safe']/total*100:.1f}%)

Nach Risiko:
  CRITICAL: {stats['by_level']['CRITICAL']}
  HIGH: {stats['by_level']['HIGH']}
  MEDIUM: {stats['by_level']['MEDIUM']}
  LOW: {stats['by_level']['LOW']}

Letzte 5 Blockierungen:
"""
        for block in stats["recent_blocks"][:5]:
            report += f"  - {block['sender'][:30]} | {block['subject'][:30]} | {block['reason']}\n"
        
        return report

# ================== MAIN ==================

if __name__ == "__main__":
    import sys
    
    filter_obj = EmailScamFilter()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--stats":
        print(filter_obj.get_report())
    
    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode
        test_emails = [
            ("support@etsy.com", "New order received", "You have a new order from buyer John"),
            ("security@etsy-verify.xyz", "URGENT: Verify your account", "Click here immediately or your account will be closed"),
            ("hello@fiverr.com", "Payment received", "You received $50 for your order"),
            ("fiverr-support@scam.net", "Account suspended", "Your Fiverr account has been suspended. Verify immediately!"),
        ]
        
        print("🛡️ Email Scam Filter V2 - Test\n")
        print("=" * 60)
        
        for sender, subject, body in test_emails:
            result = filter_obj.analyze(sender, subject, body)
            
            icon = {"SAFE": "✅", "MEDIUM": "⚠️", "HIGH": "🚨", "CRITICAL": "🚫"}[result["risk_level"]]
            
            print(f"\n{icon} {sender}")
            print(f"   Subject: {subject}")
            print(f"   Risk: {result['risk_level']} (Score: {result['score']})")
            print(f"   Action: {result['action']}")
            if result["findings"]:
                print(f"   Findings: {len(result['findings'])}")
        
        print("\n" + "=" * 60)
        print(filter_obj.get_report())
    
    else:
        print("🛡️ Email Scam Filter V2")
        print("Usage:")
        print("  python3 email_scam_filter_v2.py --test   # Test mode")
        print("  python3 email_scam_filter_v2.py --stats  # Show stats")
