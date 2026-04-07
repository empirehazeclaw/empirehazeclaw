#!/usr/bin/env python3
"""
💰 REVENUE TRACKING SYSTEM
=========================
Tracks income from all sources.
"""

import requests
import json
from datetime import datetime, timedelta

class RevenueTracker:
    def __init__(self):
        self.revenue = {
            "stripe": 0,
            "etsy": 0,
            "printify": 0,
            "fiverr": 0,
            "upwork": 0,
            "other": 0
        }
        self.transactions = []
        
        # API Keys (from environment)
        self.stripe_key = "export STRIPE_SECRET_KEY"
    
    def check_stripe(self):
        """Check Stripe balance and recent transactions"""
        
        try:
            # Get balance
            r = requests.get(
                "https://api.stripe.com/v1/balance",
                auth=(self.stripe_key, "")
            )
            
            if r.status_code == 200:
                data = r.json()
                available = data.get("available", [{}])[0].get("amount", 0) / 100
                pending = data.get("pending", [{}])[0].get("amount", 0) / 100
                
                self.revenue["stripe"] = available + pending
                
                # Get recent charges
                r2 = requests.get(
                    "https://api.stripe.com/v1/charges?limit=10",
                    auth=(self.stripe_key, "")
                )
                
                if r2.status_code == 200:
                    charges = r2.json().get("data", [])
                    for charge in charges:
                        if charge.get("paid") and not charge.get("refunded"):
                            amount = charge.get("amount", 0) / 100
                            self.transactions.append({
                                "source": "stripe",
                                "amount": amount,
                                "currency": charge.get("currency", "eur"),
                                "date": charge.get("created"),
                                "status": "completed" if charge.get("captured") else "pending"
                            })
                
                return {"status": "ok", "balance": available}
            else:
                return {"error": r.text}
        except Exception as e:
            return {"error": str(e)}
    
    def check_etsy(self):
        """Check Etsy shop (requires API - placeholder)"""
        # Would use Etsy API
        return {"status": "no_api"}
    
    def check_printify(self):
        """Check Printify earnings"""
        # Would use Printify API
        return {"status": "no_api"}
    
    def get_total(self):
        """Calculate total revenue"""
        return sum(self.revenue.values())
    
    def get_daily_report(self):
        """Get daily revenue breakdown"""
        
        today = datetime.now().date()
        
        daily_transactions = [
            t for t in self.transactions 
            if datetime.fromtimestamp(t["date"]).date() == today
        ]
        
        daily_total = sum(t["amount"] for t in daily_transactions)
        
        return {
            "date": today.isoformat(),
            "transactions": len(daily_transactions),
            "revenue": daily_total,
            "sources": self.revenue
        }
    
    def get_monthly_report(self):
        """Get monthly revenue"""
        
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0)
        
        month_transactions = [
            t for t in self.transactions 
            if datetime.fromtimestamp(t["date"]) >= month_start
        ]
        
        month_total = sum(t["amount"] for t in month_transactions)
        
        return {
            "month": now.strftime("%Y-%m"),
            "transactions": len(month_transactions),
            "revenue": month_total,
            "daily_avg": month_total / now.day if now.day > 0 else 0
        }
    
    def generate_report(self):
        """Generate full revenue report"""
        
        # Check all sources
        self.check_stripe()
        self.check_etsy()
        self.check_printify()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total": self.get_total(),
            "by_source": self.revenue,
            "daily": self.get_daily_report(),
            "monthly": self.get_monthly_report(),
            "recent_transactions": self.transactions[:10]
        }


def get_revenue():
    """Main entry point"""
    tracker = RevenueTracker()
    return tracker.generate_report()


if __name__ == "__main__":
    report = get_revenue()
    print(json.dumps(report, indent=2))
