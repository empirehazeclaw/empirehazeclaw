#!/usr/bin/env python3
"""
Paper Trading Tracker - Simulated Trading ohne echtes Geld
"""

import os
import json
from datetime import datetime, date

TRACKER_FILE = "/home/clawbot/.openclaw/data/paper_trading.json"

# Initial balance
INITIAL_BALANCE = 1000

def load_tracker():
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {
        "balance": INITIAL_BALANCE,
        "trades": [],
        "started": str(date.today())
    }

def save_tracker(data):
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def buy(symbol, amount, price):
    """Simulate buying a stock"""
    data = load_tracker()
    cost = amount * price
    
    if cost > data["balance"]:
        return f"❌ Nicht genug Geld! Balance: {data['balance']}€"
    
    data["balance"] -= cost
    data["trades"].append({
        "type": "BUY",
        "symbol": symbol,
        "amount": amount,
        "price": price,
        "cost": cost,
        "date": str(date.today())
    })
    save_tracker(data)
    return f"✅ GEKAUFT: {amount} x {symbol} @ {price}€ = {cost}€"

def sell(symbol, amount, price):
    """Simulate selling"""
    data = load_tracker()
    
    # Check if we have it
    owned = 0
    for t in data["trades"]:
        if t["symbol"] == symbol and t["type"] == "BUY":
            owned += t["amount"]
    for t in data["trades"]:
        if t["symbol"] == symbol and t["type"] == "SELL":
            owned -= t["amount"]
    
    if amount > owned:
        return f"❌ Du hast nur {owned} {symbol}!"
    
    revenue = amount * price
    data["balance"] += revenue
    data["trades"].append({
        "type": "SELL",
        "symbol": symbol,
        "amount": amount,
        "price": price,
        "revenue": revenue,
        "date": str(date.today())
    })
    save_tracker(data)
    return f"✅ VERKAUFT: {amount} x {symbol} @ {price}€ = {revenue}€"

def status():
    """Show current portfolio"""
    data = load_tracker()
    
    # Calculate holdings
    holdings = {}
    for t in data["trades"]:
        sym = t["symbol"]
        if sym not in holdings:
            holdings[sym] = 0
        if t["type"] == "BUY":
            holdings[sym] += t["amount"]
        else:
            holdings[sym] -= t["amount"]
    
    # Calculate current value (simplified - using last buy price)
    current_value = data["balance"]
    for sym, amt in holdings.items():
        if amt > 0:
            # Find last price
            last_price = 100  # default
            for t in reversed(data["trades"]):
                if t["symbol"] == sym:
                    last_price = t["price"]
                    break
            current_value += amt * last_price
    
    profit = current_value - INITIAL_BALANCE
    profit_pct = (profit / INITIAL_BALANCE) * 100
    
    text = f"📊 Paper Trading Status\n"
    text += f"💰 Balance: {data['balance']:.2f}€\n"
    text += f"📈 Gesamt portfolio: {current_value:.2f}€\n"
    text += f"{'📈' if profit >= 0 else '📉'} P/L: {profit:+.2f}€ ({profit_pct:+.2f}%)\n\n"
    
    if holdings:
        text += "📦 Holdings:\n"
        for sym, amt in holdings.items():
            if amt > 0:
                text += f"  {sym}: {amt}\n"
    
    return text

def reset():
    data = {
        "balance": INITIAL_BALANCE,
        "trades": [],
        "started": str(date.today())
    }
    save_tracker(data)
    return f"🔄 Reset! Neues Paper Trading mit {INITIAL_BALANCE}€"

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print(status())
    elif sys.argv[1] == "buy":
        if len(sys.argv) != 4:
            print("Usage: paper_trading.py buy SYMBOL AMOUNT PRICE")
        else:
            print(buy(sys.argv[2], float(sys.argv[3]), float(sys.argv[4])))
    elif sys.argv[1] == "sell":
        if len(sys.argv) != 4:
            print("Usage: paper_trading.py sell SYMBOL AMOUNT PRICE")
        else:
            print(sell(sys.argv[2], float(sys.argv[3]), float(sys.argv[4])))
    elif sys.argv[1] == "reset":
        print(reset())
    else:
        print("Usage: paper_trading.py [buy|sell|reset] [symbol] [amount] [price]")
