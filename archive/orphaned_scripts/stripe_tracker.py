#!/usr/bin/env python3
"""
Stripe Revenue Tracker - Echte Conversions tracken
"""
import requests
import json
from datetime import datetime

STRIPE_KEY = "sk_live_REDACTED..."  # From .env

def get_recent_charges():
    """Hole letzte erfolgreiche Zahlungen"""
    url = "https://api.stripe.com/v1/charges"
    auth = (STRIPE_KEY, "")
    params = {"limit": 10, "status": "succeeded"}
    
    r = requests.get(url, auth=auth, params=params)
    return r.json().get('data', [])

def track_conversions():
    """Track alle Conversions"""
    charges = get_recent_charges()
    
    revenue = 0
    conversions = []
    
    for charge in charges:
        amount = charge.get('amount', 0) / 100
        currency = charge.get('currency', 'eur')
        created = datetime.fromtimestamp(charge.get('created', 0))
        
        revenue += amount
        conversions.append({
            'amount': amount,
            'currency': currency,
            'date': created.isoformat(),
            'id': charge.get('id', '')
        })
    
    return {'revenue': revenue, 'conversions': conversions}

if __name__ == "__main__":
    data = track_conversions()
    print(f"Revenue: €{data['revenue']:.2f}")
    print(f"Conversions: {len(data['conversions'])}")
