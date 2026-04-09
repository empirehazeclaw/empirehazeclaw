#!/usr/bin/env python3
"""
Portfolio Tracker - Track dein Trading Portfolio
"""

import json
import os
from datetime import datetime

PORTFOLIO_FILE = "/home/clawbot/.openclaw/workspace/memory/portfolio.json"

def load_portfolio():
    """Lädt Portfolio"""
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    return {"positions": [], "cash": 10000, "history": []}

def save_portfolio(portfolio):
    """Speichert Portfolio"""
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2)

def add_position(coin, amount, price):
    """Fügt Position hinzu"""
    portfolio = load_portfolio()
    portfolio["positions"].append({
        "coin": coin,
        "amount": amount,
        "buy_price": price,
        "date": datetime.now().isoformat()
    })
    save_portfolio(portfolio)
    return f"✅ {amount} {coin} zu ${price} gekauft"

def portfolio_value():
    """Zeigt Portfolio Wert"""
    portfolio = load_portfolio()
    
    # Get current prices
    import urllib.request
    coins = list(set([p['coin'] for p in portfolio['positions']]))
    if not coins:
        return "📊 Portfolio ist leer"
    
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(coins)}&vs_currencies=usd"
        response = urllib.request.urlopen(url, timeout=10)
        prices = json.loads(response.read())
    except:
        return "❌ Preise konnten nicht geladen werden"
    
    total = portfolio["cash"]
    positions_text = "\n📊 Positionen:"
    
    for pos in portfolio['positions']:
        coin = pos['coin']
        current_price = prices.get(coin, {}).get('usd', 0)
        value = pos['amount'] * current_price
        cost = pos['amount'] * pos['buy_price']
        pnl = ((value - cost) / cost * 100) if cost > 0 else 0
        total += value
        positions_text += f"\n  {coin.upper()}: {pos['amount']} @ ${current_price:,} ({pnl:+.1f}%)"
    
    result = f"""
💼 Portfolio - {datetime.now().strftime('%Y-%m-%d %H:%M')}

🎵 Cash: ${portfolio['cash']:,.2f}
{positions_text}

💰 Gesamt Wert: ${total:,.2f}
"""
    print(result)
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print(portfolio_value())
    elif sys.argv[1] == "add" and len(sys.argv) == 5:
        print(add_position(sys.argv[2], float(sys.argv[3]), float(sys.argv[4])))
    else:
        print("Usage: python3 portfolio.py [add COIN AMOUNT PRICE]")
