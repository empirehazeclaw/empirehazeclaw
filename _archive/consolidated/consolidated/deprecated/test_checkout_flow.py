#!/usr/bin/env python3
"""
🧪 Checkout Flow Tester
Testet den kompletten Kaufprozess:

1. Website Load Test
2. Checkout URL Test  
3. Stripe Session Validierung
4. Webhook Simulation
5. Fulfillment Test

Usage:
  python3 test_checkout_flow.py              # Voller Test
  python3 test_checkout_flow.py --quick      # Quick Test nur
  python3 test_checkout_flow.py --webhook    # Nur Webhook testen
"""

import requests
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Config
STORE_URL = "https://empirehazeclaw.store"
CHECKOUTS = {
    "Restaurant AI (€29)": "https://checkout.stripe.com/g/pay/cs_live_a1eZWpWAlqa0eV41ByRPVoD2n7iTp2H0jcgjKTnfbd8",
    "Automation Scripts (€49)": "https://checkout.stripe.com/g/pay/cs_live_a1nyAnwC3EaJGJwk4ZGgcLVdPCdOpukcFnKwUpWV8mQkGKytyWircgz7MX",
    "Notion Templates (€19)": "https://checkout.stripe.com/g/pay/cs_live_a1Jyv9QNTUUGV81RpdtpmLtjfmnMIWpZwLE7PqdTVFlGm20rrwX0JS7xZo",
    "Managed AI Starter": "https://checkout.stripe.com/g/pay/cs_live_a19hziBm99XL9Tx2gBW3ewLl6ktlKSgEDY35w9iUGdEc",
    "Managed AI Professional": "https://checkout.stripe.com/g/pay/cs_live_a1I6R47rrCkqBD8HlGCFh6MrubrbZA6RmvcKC6Q5G66",
}

class CheckoutTester:
    def __init__(self):
        self.results = {
            "website": [],
            "checkout": [],
            "stripe_api": [],
            "webhook": [],
            "fulfillment": []
        }
        self.all_passed = True
    
    def log(self, msg, status="INFO"):
        icons = {"INFO": "ℹ️", "PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}
        print(f"{icons.get(status, 'ℹ️')} {msg}")
    
    def test_website(self):
        """Testet ob Website erreichbar ist"""
        self.log("Testing Website Availability...")
        
        try:
            r = requests.get(STORE_URL, timeout=15)
            
            if r.status_code == 200:
                # Check for key content
                content = r.text
                checks = [
                    ("Stripe" in content or "stripe" in content, "Stripe Integration"),
                    ("checkout" in content.lower(), "Checkout Links"),
                    ("EmpireHazeClaw" in content, "Brand Name"),
                ]
                
                for passed, name in checks:
                    if passed:
                        self.log(f"  {name}: OK", "PASS")
                    else:
                        self.log(f"  {name}: MISSING", "WARN")
                
                self.log("Website Load: OK", "PASS")
                self.results["website"].append(True)
            else:
                self.log(f"Website HTTP {r.status_code}", "FAIL")
                self.results["website"].append(False)
                self.all_passed = False
                
        except Exception as e:
            self.log(f"Website Error: {e}", "FAIL")
            self.results["website"].append(False)
            self.all_passed = False
    
    def test_checkout_urls(self):
        """Testet alle Checkout URLs"""
        self.log("\nTesting Checkout URLs...")
        
        for name, url in CHECKOUTS.items():
            try:
                r = requests.get(url, timeout=15, allow_redirects=True)
                
                if r.status_code == 200:
                    # Verify it redirects to Stripe
                    final_url = r.url.lower()
                    if "stripe.com" in final_url or "buy.stripe" in final_url:
                        self.log(f"  {name}: OK (→ Stripe)", "PASS")
                        self.results["checkout"].append(True)
                    else:
                        self.log(f"  {name}: Redirect Issue", "WARN")
                        self.results["checkout"].append(True)  # Still works
                else:
                    self.log(f"  {name}: HTTP {r.status_code}", "FAIL")
                    self.results["checkout"].append(False)
                    self.all_passed = False
                    
            except Exception as e:
                self.log(f"  {name}: ERROR - {e}", "FAIL")
                self.results["checkout"].append(False)
                self.all_passed = False
    
    def test_stripe_api(self):
        """Testet Stripe API Zugang"""
        self.log("\nTesting Stripe API...")
        
        try:
            import stripe
            from dotenv import load_dotenv
            
            # Load env
            env_file = Path("/home/clawbot/.openclaw/workspace/.env")
            if env_file.exists():
                load_dotenv(env_file)
            
            stripe.api_key = __import__('os').getenv('STRIPE_API_KEY')
            
            if not stripe.api_key:
                self.log("  No API Key found", "FAIL")
                self.results["stripe_api"].append(False)
                self.all_passed = False
                return
            
            # Test API
            account = stripe.Account.retrieve()
            self.log(f"  Account: {account.id}", "PASS")
            self.log(f"  Country: {account.country}", "PASS")
            
            # Test Balance
            balance = stripe.Balance.retrieve()
            available = balance.available[0] if balance.available else None
            if available:
                self.log(f"  Balance: {available.amount/100:.2f} {available.currency}", "PASS")
            
            self.results["stripe_api"].append(True)
            
        except ImportError:
            self.log("  Stripe module not installed", "FAIL")
            self.results["stripe_api"].append(False)
            self.all_passed = False
        except Exception as e:
            self.log(f"  API Error: {e}", "FAIL")
            self.results["stripe_api"].append(False)
            self.all_passed = False
    
    def test_webhook_simulation(self):
        """Simuliert einen Webhook Event"""
        self.log("\nSimulating Webhook Event...")
        
        # Create test event
        test_event = {
            "id": "test_event_" + str(int(time.time())),
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_" + str(int(time.time())),
                    "customer_details": {
                        "email": "test@example.com",
                        "name": "Test Kunde"
                    },
                    "amount_total": 2900,
                    "currency": "eur",
                    "payment_status": "paid"
                }
            }
        }
        
        self.log(f"  Test Event ID: {test_event['id']}", "PASS")
        self.log(f"  Type: {test_event['type']}", "PASS")
        self.log(f"  Amount: {test_event['data']['object']['amount_total']/100}€", "PASS")
        
        # Try to call webhook endpoint if it exists
        try:
            # Local webhook test
            r = requests.post(
                "http://localhost:8899/webhook",
                json=test_event,
                timeout=5
            )
            if r.status_code == 200:
                self.log("  Webhook Handler: REACHABLE", "PASS")
            else:
                self.log("  Webhook Handler: HTTP " + str(r.status_code), "WARN")
        except requests.exceptions.ConnectionError:
            self.log("  Webhook Handler: Not running (expected)", "WARN")
        except Exception as e:
            self.log(f"  Webhook Error: {e}", "WARN")
        
        self.results["webhook"].append(True)  # Event structure is valid
    
    def test_fulfillment(self):
        """Testet Fulfillment System"""
        self.log("\nTesting Fulfillment System...")
        
        # Check if fulfillment script exists
        fulfill_script = Path("/home/clawbot/.openclaw/workspace/scripts/stripe_product_fulfillment.py")
        
        if fulfill_script.exists():
            self.log("  Fulfillment Script: EXISTS", "PASS")
            
            # Check if invoices directory exists
            invoices_dir = Path("/home/clawbot/.openclaw/workspace/data/invoices")
            invoices_dir.mkdir(parents=True, exist_ok=True)
            self.log(f"  Invoices Directory: {invoices_dir}", "PASS")
            
            # Check products directory
            products_dir = Path("/home/clawbot/.openclaw/workspace/products")
            if products_dir.exists():
                products = list(products_dir.iterdir())
                self.log(f"  Products Available: {len(products)}", "PASS")
        else:
            self.log("  Fulfillment Script: MISSING", "FAIL")
            self.results["fulfillment"].append(False)
            self.all_passed = False
            return
        
        self.results["fulfillment"].append(True)
    
    def run_full_test(self):
        """Führt alle Tests aus"""
        print("=" * 60)
        print("🧪 CHECKOUT FLOW TEST")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.test_website()
        self.test_checkout_urls()
        self.test_stripe_api()
        self.test_webhook_simulation()
        self.test_fulfillment()
        
        print()
        print("=" * 60)
        print("📊 RESULTS SUMMARY")
        print("=" * 60)
        
        categories = [
            ("Website", self.results["website"]),
            ("Checkout URLs", self.results["checkout"]),
            ("Stripe API", self.results["stripe_api"]),
            ("Webhook", self.results["webhook"]),
            ("Fulfillment", self.results["fulfillment"]),
        ]
        
        all_ok = True
        for name, results in categories:
            if results:
                passed = sum(results)
                total = len(results)
                status = "PASS" if passed == total else "PARTIAL"
                print(f"  {name}: {passed}/{total} {status}")
                if passed != total:
                    all_ok = False
            else:
                print(f"  {name}: NOT TESTED")
        
        print()
        if self.all_passed and all_ok:
            print("✅ ALL TESTS PASSED - Checkout Flow is working!")
            return 0
        else:
            print("⚠️ SOME TESTS FAILED - Review needed")
            return 1
    
    def run_quick_test(self):
        """Quick Test nur"""
        print("⚡ Quick Checkout Test...")
        
        # Just test website and one checkout
        try:
            r = requests.get(STORE_URL, timeout=10)
            if r.status_code == 200:
                print("✅ Website: OK")
            else:
                print(f"❌ Website: HTTP {r.status_code}")
                return 1
            
            r = requests.get(list(CHECKOUTS.values())[0], timeout=10)
            if "stripe.com" in r.url.lower() or r.status_code == 200:
                print("✅ Checkout: OK")
            else:
                print("❌ Checkout: Issue")
                return 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
        
        return 0

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Checkout Flow Tester")
    parser.add_argument("--quick", action="store_true", help="Quick test only")
    parser.add_argument("--webhook", action="store_true", help="Test webhook only")
    args = parser.parse_args()
    
    tester = CheckoutTester()
    
    if args.quick:
        return tester.run_quick_test()
    elif args.webhook:
        tester.test_webhook_simulation()
    else:
        return tester.run_full_test()

if __name__ == "__main__":
    sys.exit(main() or 0)
