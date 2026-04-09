#!/usr/bin/env python3
"""
🦞 Outreach Optimizer - Analyzes email performance and suggests improvements
Tracks which templates/approaches get responses
"""

import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data"

class OutreachOptimizer:
    def __init__(self):
        self.sent_file = DATA_DIR / "sent_emails.json"
        self.responses_file = DATA_DIR / "responses.json"
        self.leads_file = DATA_DIR / "crm_leads.csv"
        self.sequences_file = DATA_DIR / "email_sequences.json"
    
    def load_data(self) -> Dict:
        """Load all outreach data"""
        data = {
            "sent": {},
            "responses": [],
            "leads": [],
            "sequences": {}
        }
        
        if self.sent_file.exists():
            with open(self.sent_file, 'r') as f:
                data["sent"] = json.load(f)
        
        if self.responses_file.exists():
            with open(self.responses_file, 'r') as f:
                data["responses"] = json.load(f)
        
        if self.leads_file.exists():
            with open(self.leads_file, 'r') as f:
                reader = csv.DictReader(f)
                data["leads"] = list(reader)
        
        if self.sequences_file.exists():
            with open(self.sequences_file, 'r') as f:
                data["sequences"] = json.load(f)
        
        return data
    
    def analyze_response_rate(self, data: Dict) -> Dict:
        """Calculate response rates by various factors"""
        sent = data["sent"]
        responses = data["responses"]
        
        total_sent = len(sent)
        total_responses = len(responses)
        
        # Calculate by step
        by_step = defaultdict(lambda: {"sent": 0, "responses": 0})
        
        for email, info in sent.items():
            step = info.get("step", 1)
            by_step[step]["sent"] += 1
        
        for resp in responses:
            # Try to match to sent email
            from_email = resp.get("from", "")
            if from_email in sent:
                step = sent[from_email].get("step", 1)
                by_step[step]["responses"] += 1
        
        # Calculate rates
        for step in by_step:
            s = by_step[step]
            if s["sent"] > 0:
                s["rate"] = (s["responses"] / s["sent"]) * 100
            else:
                s["rate"] = 0
        
        return {
            "total_sent": total_sent,
            "total_responses": total_responses,
            "overall_rate": (total_responses / total_sent * 100) if total_sent > 0 else 0,
            "by_step": dict(by_step)
        }
    
    def analyze_by_industry(self, data: Dict) -> Dict:
        """Analyze which industries respond best"""
        sent = data["sent"]
        leads = data["leads"]
        responses = data["responses"]
        
        # Build email -> industry map
        email_to_industry = {}
        for lead in leads:
            email = lead.get("email", "")
            industry = lead.get("industry", "unknown")
            email_to_industry[email] = industry
        
        # Count by industry
        by_industry = defaultdict(lambda: {"sent": 0, "responses": 0})
        
        for email in sent:
            industry = email_to_industry.get(email, "unknown")
            by_industry[industry]["sent"] += 1
        
        for resp in responses:
            from_email = resp.get("from", "")
            industry = email_to_industry.get(from_email, "unknown")
            by_industry[industry]["responses"] += 1
        
        # Calculate rates
        for ind in by_industry:
            s = by_industry[ind]
            if s["sent"] > 0:
                s["rate"] = (s["responses"] / s["sent"]) * 100
            else:
                s["rate"] = 0
        
        return dict(by_industry)
    
    def suggest_improvements(self, data: Dict) -> List[str]:
        """Generate improvement suggestions based on data"""
        suggestions = []
        
        rate = self.analyze_response_rate(data)
        
        # Overall response rate
        if rate["overall_rate"] < 1:
            suggestions.append("⚠️ Response rate below 1% - consider more personalized outreach")
        elif rate["overall_rate"] < 3:
            suggestions.append("📊 Response rate is okay but could be improved with personalization")
        else:
            suggestions.append("✅ Good response rate!")
        
        # Best performing step
        by_step = rate.get("by_step", {})
        if by_step:
            best_step = max(by_step.items(), key=lambda x: x[1].get("rate", 0))
            if best_step[1].get("rate", 0) > 0:
                suggestions.append(f"📈 Step {best_step[0]} has best response rate: {best_step[1]['rate']:.1f}%")
        
        # Best industry
        by_industry = self.analyze_by_industry(data)
        if by_industry:
            best_industry = max(by_industry.items(), key=lambda x: x[1].get("rate", 0))
            if best_industry[1].get("rate", 0) > 0:
                suggestions.append(f"🎯 Best responding industry: {best_industry[0]} ({best_industry[1]['rate']:.1f}%)")
            
            # Worst industry
            worst_industry = min(by_industry.items(), key=lambda x: x[1].get("rate", 999))
            if worst_industry[1].get("sent", 0) > 3 and worst_industry[1].get("rate", 0) < 1:
                suggestions.append(f"❌ Lowest responding industry: {worst_industry[0]} - consider pausing or changing approach")
        
        # Recommendations
        suggestions.append("\n💡 RECOMMENDATIONS:")
        suggestions.append("1. Focus on industries with higher response rates")
        suggestions.append("2. Personalize initial outreach emails more")
        suggestions.append("3. A/B test different subject lines")
        suggestions.append("4. Consider phone follow-up for warm leads")
        
        return suggestions
    
    def generate_report(self) -> str:
        """Generate full optimization report"""
        data = self.load_data()
        
        report = []
        report.append("=" * 60)
        report.append("🦞 OUTREACH OPTIMIZER REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 60)
        
        # Response rate analysis
        rate = self.analyze_response_rate(data)
        report.append("\n📊 RESPONSE RATE ANALYSIS")
        report.append("-" * 40)
        report.append(f"Total Emails Sent: {rate['total_sent']}")
        report.append(f"Total Responses: {rate['total_responses']}")
        report.append(f"Overall Response Rate: {rate['overall_rate']:.2f}%")
        
        # By step
        report.append("\n📧 Response Rate by Step:")
        for step, stats in sorted(rate.get("by_step", {}).items()):
            sent = stats.get("sent", 0)
            resp = stats.get("responses", 0)
            r = stats.get("rate", 0)
            report.append(f"  Step {step}: {resp}/{sent} ({r:.1f}%)")
        
        # By industry
        by_industry = self.analyze_by_industry(data)
        if by_industry:
            report.append("\n🏭 Response Rate by Industry:")
            for ind, stats in sorted(by_industry.items(), key=lambda x: x[1].get("rate", 0), reverse=True):
                sent = stats.get("sent", 0)
                resp = stats.get("responses", 0)
                r = stats.get("rate", 0)
                report.append(f"  {ind}: {resp}/{sent} ({r:.1f}%)")
        
        # Suggestions
        suggestions = self.suggest_improvements(data)
        report.append("\n" + "=" * 40)
        report.append("💡 INSIGHTS & RECOMMENDATIONS")
        report.append("-" * 40)
        for s in suggestions:
            report.append(s)
        
        return "\n".join(report)
    
    def run(self):
        """Main execution"""
        print(self.generate_report())

if __name__ == "__main__":
    optimizer = OutreachOptimizer()
    optimizer.run()
