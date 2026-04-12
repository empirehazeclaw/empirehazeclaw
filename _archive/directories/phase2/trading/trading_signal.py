#!/usr/bin/env python3
"""
Trading Signal - Generiert tägliche BTC Signale
"""

import json
import os
from datetime import datetime

def get_btc_price():
    """Holt BTC Preis von CoinGecko"""
    import urllib.request
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
        response = urllib.request.urlopen(url, timeout=10)
        data = json.loads(response.read())
        return data['bitcoin']['usd'], data['bitcoin']['usd_24h_change']
    except:
        return None, None

def create_signal():
    """Erstellt tägliches Trading Signal"""
    
    price, change = get_btc_price()
    
    if not price:
        signal = "❌ BTC Preis konnte nicht abgerufen werden"
        return signal
    
    # Simple signal logic
    if change > 2:
        action = "📈 STRONG BUY"
    elif change > 0:
        action = "🟢 BUY"
    elif change < -2:
        action = "📉 STRONG SELL"
    elif change < 0:
        action = "🔴 SELL"
    else:
        action = "⚪ HOLD"
    
    signal = f"""
📊 BTC Daily Signal - {datetime.now().strftime('%Y-%m-%d')}

💰 Preis: ${price:,}
📈 24h: {change:+.2f}%

🎯 Signal: {action}

📊 Support: ~${int(price * 0.95):,}
📊 Resistance: ~${int(price * 1.05):,}

*Paper Trading only - kein finanzielles Risiko*
"""
    
    # Save signal
    os.makedirs('/home/clawbot/.openclaw/workspace/memory', exist_ok=True)
    with open('/home/clawbot/.openclaw/workspace/memory/trading_signal.md', 'w') as f:
        f.write(signal)
    
    print(signal)
    return signal

if __name__ == "__main__":
    create_signal()
