#!/usr/bin/env python3
"""
💰 Revenue Forecaster - Skill
Prognostiziert Revenue basierend auf 30-Tage-Daten

Integration: Fügt sich in daily_report ein
Nutzung: python3 scripts/revenue_forecaster.py
"""
import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict

STRIPE_KEY = "${STRIPE_SECRET_KEY}"

DATA_DIR = "/home/clawbot/.openclaw/workspace/data"
REVENUE_HISTORY_FILE = f"{DATA_DIR}/revenue_history.json"
FORECAST_FILE = f"{DATA_DIR}/revenue_forecast.json"

def get_stripe_balance():
    """Hole Stripe Balance (tatsächliches Guthaben)"""
    url = "https://api.stripe.com/v1/balance"
    auth = (STRIPE_KEY, "")
    try:
        r = requests.get(url, auth=auth, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def get_stripe_charges(days=30):
    """Hole Stripe Charges der letzten X Tage"""
    url = "https://api.stripe.com/v1/charges"
    auth = (STRIPE_KEY, "")
    since = int((datetime.now() - timedelta(days=days)).timestamp())
    params = {"limit": 100, "created": {"gte": since}, "status": "succeeded"}
    
    try:
        r = requests.get(url, auth=auth, params=params, timeout=15)
        if r.status_code == 200:
            return r.json().get('data', [])
    except Exception as e:
        print(f"Stripe API Error: {e}")
    return []

def get_stripe_subscriptions():
    """Hole aktive Subscriptions"""
    url = "https://api.stripe.com/v1/subscriptions"
    auth = (STRIPE_KEY, "")
    params = {"limit": 100, "status": "active"}
    
    try:
        r = requests.get(url, auth=auth, params=params, timeout=15)
        if r.status_code == 200:
            return r.json().get('data', [])
    except:
        pass
    return []

def calculate_daily_revenue(charges, days=30):
    """Berechne täglichen Revenue"""
    daily = defaultdict(float)
    cutoff = datetime.now() - timedelta(days=days)
    
    for charge in charges:
        created = datetime.fromtimestamp(charge.get('created', 0))
        if created >= cutoff:
            amount = charge.get('amount', 0) / 100
            daily[created.date().isoformat()] += amount
    
    return dict(daily)

def calculate_mrr(subscriptions):
    """Berechne Monthly Recurring Revenue"""
    mrr = 0
    for sub in subscriptions:
        amount = sub.get('items', {}).get('data', [{}])[0].get('price', {}).get('unit_amount', 0)
        if amount:
            mrr += amount / 100
    return mrr

def forecast_next_month(daily_revenue):
    """Prognostiziere Revenue für nächsten Monat"""
    if not daily_revenue:
        return {"predicted": 0, "trend": "no_data"}
    
    values = list(daily_revenue.values())
    
    # Einfacher Trend: Durchschnitt der letzten 7 Tage vs 30 Tage
    recent_7 = sum(values[-7:]) / min(7, len(values)) if len(values) >= 7 else sum(values) / len(values)
    recent_30 = sum(values) / len(values)
    
    # Trend-Analyse
    if len(values) >= 14:
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        trend_pct = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0
    else:
        trend_pct = 0
    
    # Predicted = Recent Average * 30 days, angepasst um Trend
    predicted = recent_7 * 30 * (1 + trend_pct/100)
    
    return {
        "predicted": round(predicted, 2),
        "trend_pct": round(trend_pct, 1),
        "trend": "up" if trend_pct > 5 else "down" if trend_pct < -5 else "stable",
        "avg_daily_last_7": round(recent_7, 2),
        "avg_daily_last_30": round(recent_30, 2)
    }

def generate_report():
    """Generiere vollständigen Report"""
    print("💰 Revenue Forecaster")
    print("=" * 50)
    
    # Get Stripe data
    charges = get_stripe_charges(days=30)
    subscriptions = get_stripe_subscriptions()
    balance = get_stripe_balance()
    
    # Calculate metrics
    daily_revenue = calculate_daily_revenue(charges, days=30)
    mrr = calculate_mrr(subscriptions)
    forecast = forecast_next_month(daily_revenue)
    
    # Current balance
    available = 0
    if balance:
        available = balance.get('available', [{}])[0].get('amount', 0) / 100
    
    # Total last 30 days
    total_30d = sum(daily_revenue.values())
    
    # Print report
    print(f"\n📊 AKTUELLER STAND")
    print(f"   Verfügbares Guthaben: €{available:.2f}")
    print(f"   MRR (Subs): €{mrr:.2f}/Monat")
    print(f"   Revenue (30 Tage): €{total_30d:.2f}")
    
    print(f"\n📈 TREND")
    trend = forecast.get('trend', 'unknown')
    trend_icon = '📈' if trend == 'up' else '📉' if trend == 'down' else '➡️'
    print(f"   Trend: {trend_icon} {forecast.get('trend_pct', 0):+.1f}%")
    print(f"   Ø Tag (7 Tage): €{forecast.get('avg_daily_last_7', 0):.2f}")
    print(f"   Ø Tag (30 Tage): €{forecast.get('avg_daily_last_30', 0):.2f}")
    
    print(f"\n🔮 PROGNOSE (nächster Monat)")
    print(f"   Vorhergesagt: €{forecast.get('predicted', 0):.2f}")
    
    # Prepare data for storage
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "period": "30_days",
        "metrics": {
            "available_balance": available,
            "mrr": mrr,
            "total_30d": total_30d,
            "daily_avg_7": forecast.get('avg_daily_last_7', 0),
            "daily_avg_30": forecast.get('avg_daily_last_30', 0)
        },
        "forecast": {
            "predicted_revenue": forecast.get('predicted', 0),
            "trend_pct": forecast.get('trend_pct', 0),
            "trend_direction": forecast.get('trend', 'unknown')
        },
        "daily_breakdown": daily_revenue
    }
    
    # Save to files
    import os
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(REVENUE_HISTORY_FILE, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    with open(FORECAST_FILE, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n💾 Daten gespeichert:")
    print(f"   {REVENUE_HISTORY_FILE}")
    print(f"   {FORECAST_FILE}")
    
    return report_data

def get_quick_forecast():
    """Schnelle Prognose für daily_report Integration"""
    try:
        with open(REVENUE_HISTORY_FILE) as f:
            data = json.load(f)
        
        m = data.get('metrics', {})
        f = data.get('forecast', {})
        
        return (
            f"💰 Revenue: €{m.get('total_30d', 0):.2f} (30 Tage) | "
            f"📊 MRR: €{m.get('mrr', 0):.2f} | "
            f"🔮 Prognose: €{f.get('predicted_revenue', 0):.2f} ({f.get('trend_direction', '?')})"
        )
    except:
        return "💰 Revenue: Keine Daten verfügbar"

if __name__ == "__main__":
    generate_report()
