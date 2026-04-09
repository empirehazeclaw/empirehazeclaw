#!/usr/bin/env python3
"""
💳 Stripe Integration - Vollständige API Anbindung
Features:
- Payment verification
- Subscription management
- Customer lookup
- Refund processing
- Webhook handling

Usage:
  python3 stripe_integration.py status          # Show account status
  python3 stripe_integration.py customers       # List recent customers
  python3 stripe_integration.py payments        # List recent payments
  python3 stripe_integration.py check <session> # Check specific payment
  python3 stripe_integration.py refund <id>     # Refund payment
  python3 stripe_integration.py webhook         # Start webhook listener
"""

import os
import sys
import json
import stripe
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
ENV_FILE = WORKSPACE / ".env"
load_dotenv(ENV_FILE)

# Stripe API Key
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Products map
PRODUCTS = {
    "cs_live_a1eZWpWAlqa0eV41ByRPVoD2n7iTp2H0jcgjKTnfbd8": {"name": "Restaurant AI Starter Kit", "price": 29},
    "cs_live_a1nyAnwC3EaJGJwk4ZGgcLVdPCdOpukcFnKwUpWV8mQkGKytyWircgz7MX": {"name": "Automation Scripts Bundle", "price": 49},
    "cs_live_a1Jyv9QNTUUGV81RpdtpmLtjfmnMIWpZwLE7PqdTVFlGm20rrwX0JS7xZo": {"name": "Notion Templates", "price": 19},
}

class StripeIntegration:
    def __init__(self):
        if not STRIPE_API_KEY:
            print("❌ STRIPE_API_KEY not found in .env")
            sys.exit(1)
        
        stripe.api_key = STRIPE_API_KEY
        self.workspace = WORKSPACE
    
    def get_account_status(self):
        """Zeigt Stripe Konto Status"""
        try:
            account = stripe.Account.retrieve()
            print(f"✅ Stripe Account Active")
            print(f"   ID: {account.id}")
            print(f"   Country: {account.country}")
            print(f"   Email: {account.email}")
            
            # Balance
            balance = stripe.Balance.retrieve()
            available = balance.available[0] if balance.available else None
            pending = balance.pending[0] if balance.pending else None
            
            if available:
                print(f"   Available: {available.amount/100:.2f} {available.currency}")
            if pending:
                print(f"   Pending: {pending.amount/100:.2f} {pending.currency}")
            
            return True
        except stripe.error.AuthenticationError:
            print("❌ Invalid API Key")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def list_recent_payments(self, days=7, limit=20):
        """Liste recente Payments"""
        print(f"\n📊 Recent Payments (last {days} days):")
        print("-" * 60)
        
        try:
            # Get charges
            charges = stripe.Charge.list(limit=limit, created={
                "gte": int((datetime.now() - timedelta(days=days)).timestamp())
            })
            
            total_revenue = 0
            for charge in charges.data:
                if charge.paid and not charge.refunded:
                    total_revenue += charge.amount
                    created = datetime.fromtimestamp(charge.created)
                    print(f"  {created.strftime('%Y-%m-%d %H:%M')} | {charge.amount/100:>8.2f}€ | {charge.description or 'Payment':<25} | {charge.status}")
            
            print("-" * 60)
            print(f"  Total Revenue: {total_revenue/100:.2f}€")
            print(f"  Transactions: {len(charges.data)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def list_customers(self, limit=10):
        """Liste recente Customers"""
        print(f"\n👥 Recent Customers:")
        print("-" * 60)
        
        try:
            customers = stripe.Customer.list(limit=limit)
            
            for cust in customers.data:
                created = datetime.fromtimestamp(cust.created)
                email = cust.email or "No email"
                name = cust.name or ""
                print(f"  {email:<30} | {name:<20} | {created.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def check_payment(self, session_id):
        """Prüft specific Checkout Session"""
        print(f"\n🔍 Checking Session: {session_id}")
        print("-" * 60)
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            print(f"  Status: {session.payment_status}")
            print(f"  Amount: {session.amount_total/100:.2f}€" if session.amount_total else "  Amount: N/A")
            print(f"  Customer: {session.customer_details.email if session.customer_details else 'N/A'}")
            print(f"  Name: {session.customer_details.name if session.customer_details else 'N/A'}")
            print(f"  Created: {datetime.fromtimestamp(session.created).strftime('%Y-%m-%d %H:%M')}")
            
            if session.line_items:
                for item in session.line_items.data:
                    print(f"  Product: {item.description}")
            
            # Payment Intent
            if session.payment_intent:
                pi = stripe.PaymentIntent.retrieve(session.payment_intent)
                print(f"  Payment Intent: {pi.status}")
            
            return session
        
        except stripe.error.StripeError as e:
            print(f"❌ Stripe Error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def list_subscriptions(self, limit=10):
        """Liste aktive Subscriptions"""
        print(f"\n📋 Active Subscriptions:")
        print("-" * 60)
        
        try:
            subs = stripe.Subscription.list(limit=limit, status="active")
            
            for sub in subs.data:
                customer = stripe.Customer.retrieve(sub.customer)
                print(f"  {customer.email:<30} | {sub.items.data[0].price.unit_amount/100:.2f}€/mo | ID: {sub.id[:20]}...")
            
            print("-" * 60)
            print(f"  Total Active: {len(subs.data)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def create_refund(self, payment_intent_id, amount=None, reason="requested_by_customer"):
        """Erstellt Refund"""
        print(f"\n💸 Creating Refund for: {payment_intent_id}")
        
        try:
            params = {"payment_intent": payment_intent_id}
            if amount:
                params["amount"] = int(amount * 100)  # Convert to cents
            
            refund = stripe.Refund.create(**params)
            
            print(f"  ✅ Refund created: {refund.id}")
            print(f"  Amount: {refund.amount/100:.2f}€")
            print(f"  Status: {refund.status}")
            
            return refund
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_revenue_summary(self, days=30):
        """Zeigt Revenue Summary"""
        print(f"\n💰 Revenue Summary (last {days} days):")
        print("=" * 60)
        
        start = int((datetime.now() - timedelta(days=days)).timestamp())
        
        # Payments
        charges = stripe.Charge.list(limit=100, created={"gte": start})
        
        total = sum(c.amount for c in charges.data if c.paid and not c.refunded)
        refunded = sum(c.amount_refunded for c in charges.data if c.paid)
        net = total - refunded
        
        print(f"  Gross Revenue:  {total/100:>10.2f}€")
        print(f"  Refunded:       {refunded/100:>10.2f}€")
        print(f"  Net Revenue:    {net/100:>10.2f}€")
        print(f"  Transactions:   {len(charges.data):>10}")
        
        # Subscriptions
        subs = stripe.Subscription.list(limit=100, status="active", created={"gte": start})
        mrr = sum(s.items.data[0].price.unit_amount or 0 for s in subs.data) / 100
        
        print(f"\n  Active Subs:     {len(subs.data):>10}")
        print(f"  Est. MRR:        {mrr:>10.2f}€")
        print("=" * 60)
        
        return {"gross": total/100, "refunded": refunded/100, "net": net/100, "mrr": mrr}

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Stripe Integration CLI")
    parser.add_argument("action", choices=["status", "customers", "payments", "subscriptions", "check", "refund", "summary", "webhook"], help="Action to perform")
    parser.add_argument("--session", type=str, help="Session ID for check command")
    parser.add_argument("--payment-intent", type=str, help="Payment Intent ID for refund")
    parser.add_argument("--amount", type=float, help="Amount to refund")
    parser.add_argument("--days", type=int, default=30, help="Number of days to look back")
    args = parser.parse_args()
    
    stripe_int = StripeIntegration()
    
    if args.action == "status":
        stripe_int.get_account_status()
    
    elif args.action == "customers":
        stripe_int.list_customers()
    
    elif args.action == "payments":
        stripe_int.list_recent_payments(days=args.days)
    
    elif args.action == "subscriptions":
        stripe_int.list_subscriptions()
    
    elif args.action == "check":
        if not args.session:
            print("❌ --session required")
            sys.exit(1)
        stripe_int.check_payment(args.session)
    
    elif args.action == "refund":
        if not args.payment_intent:
            print("❌ --payment-intent required")
            sys.exit(1)
        stripe_int.create_refund(args.payment_intent, amount=args.amount)
    
    elif args.action == "summary":
        stripe_int.get_revenue_summary(days=args.days)
    
    elif args.action == "webhook":
        print("🚀 Starting Stripe Webhook Listener...")
        print("   Use: stripe listen --forward-to localhost:8899/webhook")
        print("   Or set webhook URL in Stripe Dashboard")
        
        from stripe_webhook import start_webhook_server
        start_webhook_server(8899)
        
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopped")

if __name__ == "__main__":
    main()
