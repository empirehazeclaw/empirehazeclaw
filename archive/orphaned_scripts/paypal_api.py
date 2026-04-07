#!/usr/bin/env python3
"""
🅿️ PAYPAL INTEGRATION
=====================
Automatisiere PayPal Verkäufe.

API Docs: https://developer.paypal.com/api/rest/
"""

import requests
import json
import os
from datetime import datetime, timedelta

class PayPalClient:
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.environ.get("PAYPAL_CLIENT_ID", "")
        self.client_secret = client_secret or os.environ.get("PAYPAL_CLIENT_SECRET", "")
        self.base_url = "https://api-m.paypal.com"  # Production
        self.access_token = None
    
    def get_access_token(self):
        """Get OAuth access token"""
        if not self.client_id or not self.client_secret:
            return None
        
        try:
            auth = (self.client_id, self.client_secret)
            data = {"grant_type": "client_credentials"}
            
            r = requests.post(
                f"{self.base_url}/v1/oauth2/token",
                auth=auth,
                data=data
            )
            
            if r.status_code == 200:
                self.access_token = r.json().get("access_token")
                return self.access_token
        except Exception as e:
            print(f"Auth error: {e}")
        
        return None
    
    def test_connection(self):
        """Test if API works"""
        if not self.client_id:
            return {"status": "no_creds", "message": "PAYPAL_CLIENT_ID not set"}
        
        token = self.get_access_token()
        if not token:
            return {"status": "error", "message": "Failed to get access token"}
        
        return {"status": "ok", "token": token[:20] + "..."}
    
    def get_orders(self, start_date=None, limit=100):
        """Get orders/transactions"""
        if not self.access_token:
            self.get_access_token()
        
        if not self.access_token:
            return {"error": "Not authenticated"}
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Get transactions
        params = {
            "page_size": min(limit, 100),
            "fields": "all"
        }
        
        if start_date:
            params["start_date"] = start_date
        
        try:
            r = requests.get(
                f"{self.base_url}/v1/reporting/transactions",
                headers=headers,
                params=params
            )
            
            if r.status_code == 200:
                return r.json()
            else:
                return {"error": r.text}
        except Exception as e:
            return {"error": str(e)}
    
    def get_balance(self):
        """Get PayPal balance"""
        if not self.access_token:
            self.get_access_token()
        
        if not self.access_token:
            return {"error": "Not authenticated"}
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            r = requests.get(
                f"{self.base_url}/v1/reporting/balances",
                headers=headers
            )
            
            if r.status_code == 200:
                return r.json()
            else:
                return {"error": r.text}
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_revenue(self, days=30):
        """Calculate total revenue from transactions"""
        
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        result = self.get_orders(start_date=start_date)
        
        if "error" in result:
            return {"error": result["error"]}
        
        transactions = result.get("transaction_details", [])
        
        total = 0
        count = 0
        
        for txn in transactions:
            info = txn.get("transaction_info", {})
            amount = info.get("transaction_event_code", "")
            
            # Get gross amount
            gross = txn.get("amount_with_breakdown", {}).get("gross_amount", {})
            if gross.get("currency_code") == "EUR":
                total += float(gross.get("value", 0))
                count += 1
        
        return {
            "total": total,
            "currency": "EUR",
            "transactions": count,
            "period_days": days
        }


# CLI
if __name__ == "__main__":
    import sys
    
    client = PayPalClient()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 paypal.py test       - Test connection")
        print("  python3 paypal.py balance   - Get balance")
        print("  python3 paypal.py revenue   - Get revenue")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "test":
        print(json.dumps(client.test_connection(), indent=2))
    elif cmd == "balance":
        print(json.dumps(client.get_balance(), indent=2))
    elif cmd == "revenue":
        print(json.dumps(client.calculate_revenue(), indent=2))
    else:
        print(f"Unknown command: {cmd}")
