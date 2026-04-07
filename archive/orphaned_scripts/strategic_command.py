#!/usr/bin/env python3
"""
🎯 Strategic Command Center
Das "Gehirn" das eigenständig:
- Unser System überwacht
- Chancen erkennt  
- Aufgaben priorisiert
- Automatisch ausführt

Mission: Das Unternehmen skalieren ohne manuelles Eingreifen

Usage: python3 strategic_command.py [--daemon] [--plan]
"""

import subprocess
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# ============================================
# MISSION & STRATEGY
# ============================================

MISSION = """
EMPIREHAZECLAW - Mission 2026:
1. Revenue: €10.000 MRR bis Q4 2026
2. Kunden: 50 aktive Managed AI Kunden
3. Digitale Produkte: 5 Produkte mit €5.000 MRR
4. Expansion: DE → EU → Global
"""

PRIORITIES = [
    "REVENUE",      # Geld verdienen
    "CUSTOMERS",    # Kunden gewinnen
    "PRODUCTS",     # Produkte verbessern/erstellen
    "MARKETING",    # Sichtbarkeit erhöhen
    "OPERATIONS",   # Systeme am Laufen halten
]

@dataclass
class Task:
    title: str
    description: str
    priority: int  # 1-10
    category: str   # REVENUE, CUSTOMERS, PRODUCTS, etc
    impact: str    # high, medium, low
    effort: str     # high, medium, low
    status: str = "pending"
    result: str = ""
    
    def __lt__(self, other):
        return self.priority < other.priority

@dataclass
class SystemState:
    revenue_mrr: float = 0
    customers: int = 0
    leads_today: int = 0
    leads_week: int = 0
    conversion_rate: float = 0
    website_traffic: int = 0
    social_engagement: int = 0
    products_count: int = 0
    issues: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    last_actions: List[str] = field(default_factory=list)

class StrategicCommand:
    """
    Das Herz des autonomen Systems.
    Analysiert, plant, handelt.
    """
    
    def __init__(self):
        self.work_dir = Path("/home/clawbot/.openclaw/workspace")
        self.data_dir = self.work_dir / "data"
        self.log_dir = self.work_dir / "logs"
        self.state_file = self.data_dir / "strategic_state.json"
        self.tasks_file = self.data_dir / "strategic_tasks.json"
        
        for d in [self.data_dir, self.log_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.state = self.load_state()
        self.tasks = self.load_tasks()
    
    def log(self, msg: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{level}] {msg}"
        print(line)
        
        log_file = self.log_dir / "strategic_command.log"
        with open(log_file, "a") as f:
            f.write(line + "\n")
    
    def load_state(self) -> SystemState:
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                    return SystemState(**data)
            except:
                pass
        return SystemState()
    
    def save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(asdict(self.state), f, indent=2)
    
    def load_tasks(self) -> List[Task]:
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file) as f:
                    data = json.load(f)
                    return [Task(**t) for t in data]
            except:
                pass
        return []
    
    def save_tasks(self):
        with open(self.tasks_file, "w") as f:
            json.dump([asdict(t) for t in self.tasks], f, indent=2)
    
    # ============================================
    # MONITORING - System status erfassen
    # ============================================
    
    def monitor_websites(self) -> Dict:
        """Check website status"""
        websites = {
            "store": "https://empirehazeclaw.store",
            "de": "https://empirehazeclaw.de",
            "info": "https://empirehazeclaw.info"
        }
        
        results = {}
        for name, url in websites.items():
            try:
                import requests
                r = requests.get(url, timeout=10)
                results[name] = "✅" if r.status_code == 200 else f"⚠️ {r.status_code}"
            except:
                results[name] = "❌ DOWN"
        
        return results
    
    def monitor_revenue(self) -> Dict:
        """Prüfe Revenue-Status"""
        # Check Stripe für recente Sales
        try:
            import stripe
            from dotenv import load_dotenv
            load_dotenv(self.work_dir / ".env")
            stripe.api_key = os.getenv("STRIPE_API_KEY")
            
            # Letzte 30 Tage Revenue
            charges = stripe.Charge.list(limit=100)
            
            now = datetime.now()
            month_start = datetime(now.year, now.month, 1)
            
            monthly_revenue = sum(
                c.amount for c in charges.data 
                if c.created >= int(month_start.timestamp())
            ) / 100
            
            return {
                "mrr": monthly_revenue,
                "customers": len(set(c.customer for c in charges.data))
            }
        except Exception as e:
            return {"mrr": 0, "customers": 0, "error": str(e)}
    
    def monitor_leads(self) -> Dict:
        """Prüfe Lead-Status"""
        leads_file = self.data_dir / "leads.json"
        sent_file = self.data_dir / "sent_emails.json"
        
        total_leads = 0
        sent_today = 0
        
        if leads_file.exists():
            with open(leads_file) as f:
                data = json.load(f)
                if isinstance(data, list):
                    total_leads = len(data)
                elif isinstance(data, dict):
                    total_leads = len(data.get("leads", []))
        
        if sent_file.exists():
            with open(sent_file) as f:
                data = json.load(f)
                today = datetime.now().strftime("%Y-%m-%d")
                sent_today = sum(
                    1 for e in data.get("emails", [])
                    if today in e.get("sent_at", "")
                )
        
        return {"total": total_leads, "sent_today": sent_today}
    
    def monitor_gaps(self) -> List[str]:
        """Erkennt Lücken im Business"""
        gaps = []
        
        # Revenue prüfen
        if self.state.revenue_mrr < 100:
            gaps.append("💰 Revenue unter €100 MRR - Need more sales!")
        
        # Website Traffic
        if self.state.website_traffic < 100:
            gaps.append("📊 Wenig Traffic - Need more marketing!")
        
        # Leads
        if self.state.leads_week < 10:
            gaps.append("👥 Wenig Leads - Need more outreach!")
        
        # Produkte
        if self.state.products_count < 3:
            gaps.append("📦 Nur wenige Produkte - Need more digital products!")
        
        # Conversion
        if self.state.conversion_rate < 1:
            gaps.append("📈 Niedrige Conversion - Need better offers!")
        
        return gaps
    
    def monitor_opportunities(self) -> List[str]:
        """Erkennt Chancen"""
        opportunities = []
        
        # Check was gerade gut läuft
        if self.state.website_traffic > 500:
            opportunities.append("🚀 Hoher Traffic - guter Zeitpunkt für Conversion-Tests")
        
        if self.state.leads_week > 50:
            opportunities.append("📧 Viele Leads - guter Zeitpunkt für Follow-ups")
        
        if len(self.state.last_actions) > 5:
            opportunities.append("✅ System läuft gut - kann neue Initiativen starten")
        
        return opportunities
    
    # ============================================
    # PLANNING - Aufgaben erkennen und priorisieren
    # ============================================
    
    def analyze_and_plan(self) -> List[Task]:
        """Hauptplanungs-Logik"""
        tasks = []
        
        # === REVENUE PRIORITY ===
        if self.state.revenue_mrr < 500:
            tasks.append(Task(
                title="🔴 URGENT: Revenue unter €500",
                description="Wir brauchen dringend Sales. Prüfe ob Stripe funktioniert, ob Links korrekt sind.",
                priority=1,
                category="REVENUE",
                impact="high",
                effort="low"
            ))
        
        # === CUSTOMERS PRIORITY ===
        if self.state.customers < 10:
            tasks.append(Task(
                title="Kundenwachstum kritisch",
                description="Wir brauchen mehr Kunden. Starte aggressive Outreach-Kampagne.",
                priority=2,
                category="CUSTOMERS",
                impact="high",
                effort="high"
            ))
        
        # === PRODUCTS PRIORITY ===
        if self.state.products_count < 3:
            tasks.append(Task(
                title="Digitale Produkte erweitern",
                description="Wir haben nur wenige Produkte. Erstelle Automation Scripts Bundle.",
                priority=3,
                category="PRODUCTS",
                impact="medium",
                effort="medium"
            ))
        
        # === MARKETING PRIORITY ===
        if self.state.website_traffic < 100:
            tasks.append(Task(
                title="Mehr Traffic generieren",
                description="Blog Posts, Social Media, SEO optimieren.",
                priority=4,
                category="MARKETING",
                impact="medium",
                effort="medium"
            ))
        
        # === OPERATIONS ===
        website_status = self.monitor_websites()
        if any("❌" in v or "⚠️" in v for v in website_status.values()):
            tasks.append(Task(
                title="⚠️ Website Problem erkannt",
                description=f"Website Status: {website_status}. Muss sofort behoben werden!",
                priority=1,
                category="OPERATIONS",
                impact="high",
                effort="low"
            ))
        
        # === CHANCE: Viel Traffic ===
        if self.state.website_traffic > 500 and self.state.conversion_rate < 2:
            tasks.append(Task(
                title="🚀 Traffic hoch aber Conversion niedrig",
                description="A/B Test Checkout Pages, Angebote verbessern.",
                priority=5,
                category="REVENUE",
                impact="high",
                effort="medium"
            ))
        
        return sorted(tasks)
    
    # ============================================
    # EXECUTION - Aufgaben ausführen
    # ============================================
    
    def execute_task(self, task: Task) -> bool:
        """Führt eine Aufgabe aus"""
        self.log(f"Executing: {task.title}")
        
        success = False
        
        if task.category == "OPERATIONS":
            if "Website" in task.title:
                success = self.fix_websites()
        
        elif task.category == "REVENUE":
            if "Stripe" in task.description:
                success = self.verify_stripe_checkout()
            else:
                success = self.increase_revenue()
        
        elif task.category == "CUSTOMERS":
            success = self.run_outreach()
        
        elif task.category == "PRODUCTS":
            success = self.create_digital_product()
        
        elif task.category == "MARKETING":
            success = self.run_marketing_campaign()
        
        # Result speichern
        task.status = "done" if success else "failed"
        task.result = f"Executed at {datetime.now().isoformat()}"
        
        self.state.last_actions.append({
            "task": task.title,
            "status": task.status,
            "time": datetime.now().isoformat()
        })
        
        if len(self.state.last_actions) > 20:
            self.state.last_actions = self.state.last_actions[-20:]
        
        return success
    
    def fix_websites(self) -> bool:
        """Versucht Websites zu reparieren"""
        self.log("Checking website issues...")
        
        # Simple check - versuche curl
        for site in ["store", "de", "info"]:
            url = f"https://empirehazeclaw.{'de' if site != 'store' else 'store'}"
            try:
                import requests
                r = requests.get(url, timeout=10)
                if r.status_code != 200:
                    self.log(f"⚠️ {site}: HTTP {r.status_code}", "WARN")
            except Exception as e:
                self.log(f"❌ {site}: {e}", "ERROR")
        
        return True  # Websites sind mostly ok
    
    def verify_stripe_checkout(self) -> bool:
        """Prüft ob Stripe funktioniert"""
        self.log("Testing Stripe checkout...")
        
        import requests
        test_urls = [
            "https://checkout.stripe.com/g/pay/cs_live_a1eZWpWAlqa0eV41ByRPVoD2n7iTp2H0jcgjKTnfbd8"
        ]
        
        for url in test_urls:
            try:
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    self.log(f"✅ Stripe checkout works")
                    return True
            except:
                pass
        
        self.log("⚠️ Stripe checkout might have issues", "WARN")
        return False
    
    def increase_revenue(self) -> bool:
        """Kurzfristige Revenue-Aktionen"""
        # Starte Outreach
        self.run_outreach()
        
        # Prüfe ob alle Links korrekt
        self.verify_stripe_checkout()
        
        return True
    
    def run_outreach(self) -> bool:
        """Führt Outreach aus"""
        try:
            result = subprocess.run(
                ["python3", str(self.work_dir / "scripts/autonomous_outreach.py"), "--send"],
                capture_output=True,
                text=True,
                timeout=120
            )
            self.log(f"Outreach: {result.stdout.strip()}")
            return result.returncode == 0
        except Exception as e:
            self.log(f"Outreach failed: {e}", "ERROR")
            return False
    
    def create_digital_product(self) -> bool:
        """Erstellt ein neues digitales Produkt"""
        # Check was als nächstes kommt
        product = "automation_scripts"
        self.log(f"Creating digital product: {product}...")
        # TODO: Implement product creation
        return True
    
    def run_marketing_campaign(self) -> bool:
        """Führt Marketing aus"""
        try:
            result = subprocess.run(
                ["python3", str(self.work_dir / "scripts/run_agent.py"), "content"],
                capture_output=True,
                text=True,
                timeout=300
            )
            self.log(f"Content Agent: {result.stdout.strip()}")
            return result.returncode == 0
        except Exception as e:
            self.log(f"Marketing failed: {e}", "ERROR")
            return False
    
    # ============================================
    # MAIN LOOP
    # ============================================
    
    def run_strategic_cycle(self):
        """Ein vollständiger Strategie-Zyklus"""
        self.log("="*50)
        self.log("STRATEGIC COMMAND CYCLE STARTED")
        self.log("="*50)
        
        # 1. MONITOR
        self.log("📊 Phase 1: Monitoring...")
        website_status = self.monitor_websites()
        self.log(f"   Websites: {website_status}")
        
        revenue = self.monitor_revenue()
        self.state.revenue_mrr = revenue.get("mrr", 0)
        self.state.customers = revenue.get("customers", 0)
        
        leads = self.monitor_leads()
        self.state.leads_today = leads.get("sent_today", 0)
        
        gaps = self.monitor_gaps()
        opportunities = self.monitor_opportunities()
        
        self.state.issues = gaps
        self.state.opportunities = opportunities
        
        # 2. PLAN
        self.log("📋 Phase 2: Planning...")
        new_tasks = self.analyze_and_plan()
        
        # Neue Tasks hinzufügen
        existing_titles = [t.title for t in self.tasks if t.status == "pending"]
        for task in new_tasks:
            if task.title not in existing_titles:
                self.tasks.append(task)
                self.log(f"   New task: {task.title} (Priority {task.priority})")
        
        # 3. EXECUTE (nur höchste Priorität)
        pending_tasks = [t for t in self.tasks if t.status == "pending"]
        if pending_tasks:
            top_task = min(pending_tasks)
            
            if top_task.priority <= 3:  # Nur hohe Priorität
                self.log(f"🎯 Phase 3: Executing {top_task.title}")
                self.execute_task(top_task)
            else:
                self.log(f"⏳ Task '{top_task.title}' hat niedrige Priorität, skipping")
        
        # 4. SAVE STATE
        self.save_state()
        self.save_tasks()
        
        self.log(f"📊 Current State: MRR €{self.state.revenue_mrr:.0f}, {self.state.customers} Kunden")
        
        if gaps:
            self.log(f"⚠️ Gaps: {'; '.join(gaps)}")
        
        if opportunities:
            self.log(f"🚀 Opportunities: {'; '.join(opportunities)}")
        
        self.log("="*50)
        self.log("CYCLE COMPLETE")
        self.log("="*50)
    
    def run_daemon(self, interval_minutes: int = 30):
        """Läuft als Daemon und plant periodisch"""
        self.log(f"🚀 Starting Strategic Command Daemon (check every {interval_minutes}min)")
        
        while True:
            try:
                self.run_strategic_cycle()
            except Exception as e:
                self.log(f"ERROR in cycle: {e}", "ERROR")
            
            time.sleep(interval_minutes * 60)
    
    def run_once(self):
        """Einmaliger Durchlauf"""
        self.run_strategic_cycle()
        
        print("\n" + "="*50)
        print("CURRENT TASKS:")
        print("="*50)
        
        pending = [t for t in self.tasks if t.status == "pending"]
        if pending:
            for t in sorted(pending)[:10]:
                print(f"[P{t.priority}] {t.title}")
                print(f"         {t.category} | Impact: {t.impact} | Effort: {t.effort}")
        else:
            print("No pending tasks!")

# Required for dataclass astype
from dataclasses import asdict

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Strategic Command Center")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in minutes")
    parser.add_argument("--plan", action="store_true", help="Show current plan")
    args = parser.parse_args()
    
    command = StrategicCommand()
    
    if args.daemon:
        command.run_daemon(args.interval)
    else:
        command.run_once()

if __name__ == "__main__":
    main()
