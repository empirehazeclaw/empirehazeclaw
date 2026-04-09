#!/usr/bin/env python3
import sys
import os
import json
import requests
import subprocess
from datetime import datetime

sys.path.insert(0, '/home/clawbot/.openclaw/workspace')
from scripts.trading.ta_engine import analyze_trend
from scripts.trading.sentiment_engine import analyze_sentiment

PORTFOLIO_URL = "http://127.0.0.1:8001/portfolio"
ORDER_URL = "http://127.0.0.1:8001/order"
STATE_FILE = "/home/clawbot/.openclaw/workspace/data/trading_state.json"

COINS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']

def send_telegram(message):
    """Sendet Live-Alerts via OpenClaw an Nico"""
    try:
        subprocess.run([
            "openclaw", "message", "send", 
            "--channel", "telegram", 
            "--target", "5392634979", 
            "--message", message
        ], capture_output=True)
    except:
        pass

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"active_trades": []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def execute():
    print(f"[{datetime.now().isoformat()}] 🤖 TRADING AGENT INITIATED (LEVEL MAX)")
    state = load_state()
    
    # 1. Globale Sentiment-Analyse (Gilt für gesamten Krypto-Markt)
    sentiment_data = analyze_sentiment()
    print(f"📰 Markt-Sentiment: Score {sentiment_data['score']}, Signal: {sentiment_data['signal']}")

    # 2. Risk Management & Trailing Stop-Loss für offene Trades
    trades_to_keep = []
    sold_something = False
    
    for trade in state['active_trades']:
        symbol = trade['symbol']
        entry = trade['entry_price']
        amount = trade['amount']
        
        # Hole aktuellen Preis
        try:
            ta_current = analyze_trend(symbol)
            current_price = ta_current['price']
        except:
            trades_to_keep.append(trade)
            continue
            
        # Trailing Stop Logik: Höchsten Preis updaten
        highest = trade.get('highest_price', entry)
        if current_price > highest:
            trade['highest_price'] = current_price
            highest = current_price
            
        pnl_pct = ((current_price - entry) / entry) * 100
        drawdown_from_high = ((highest - current_price) / highest) * 100
        
        print(f"🛡️ [{symbol}] Entry: ${entry} | Aktuell: ${current_price} | PnL: {pnl_pct:.2f}% | Drawdown v. High: {drawdown_from_high:.2f}%")
        
        sell_reason = None
        # Trailing Stop (Sichere Gewinne ab, wenn er 5% vom Hoch fällt UND im Plus ist)
        if drawdown_from_high >= 5.0 and pnl_pct > 2.0:
            sell_reason = f"Trailing Stop-Loss (+{pnl_pct:.2f}% Profit gesichert)"
        # Hard Stop-Loss
        elif pnl_pct <= -5.0:
            sell_reason = f"Hard Stop-Loss ({pnl_pct:.2f}% Verlust begrenzt)"
        # Hard Take-Profit (Sicherheitshalber bei extremen Spikes)
        elif pnl_pct >= 25.0:
            sell_reason = f"Max Take-Profit (+{pnl_pct:.2f}%)"
            
        if sell_reason:
            print(f"🚨 VERKAUFE {symbol}: {sell_reason}")
            try:
                res = requests.post(ORDER_URL, json={"pair": symbol, "side": "sell", "amount": amount})
                if res.status_code == 200:
                    msg = f"📉 *SELL ALERT ({symbol})*\nGrund: {sell_reason}\nVerkaufspreis: ${current_price}"
                    send_telegram(msg)
                    sold_something = True
                else:
                    trades_to_keep.append(trade) # Behalten wenn API fehlschlägt
            except:
                trades_to_keep.append(trade)
        else:
            trades_to_keep.append(trade)
            
    state['active_trades'] = trades_to_keep
    save_state(state)

    # 3. Multi-Coin Scanner für neue Einstiege (Nur wenn wir noch nicht voll investiert sind)
    if len(state['active_trades']) < 3: # Max 3 offene Positionen
        print("\n🔍 Scanne nach neuen Trade-Setups (Multi-Coin)...")
        best_trade = None
        best_score = -999
        
        for symbol in COINS:
            # Skip if already holding this coin
            if any(t['symbol'] == symbol for t in state['active_trades']):
                continue
                
            ta_data = analyze_trend(symbol)
            if ta_data.get("signal") == "ERROR": continue
            
            print(f"   📊 {symbol}: RSI {ta_data['rsi']} | MACD {ta_data['macd_hist']} | Signal: {ta_data['signal']}")
            
            # Strategie: Nur Kaufen bei starken TA-Signalen und positiven/neutralen News
            if "BUY" in ta_data['signal'] and sentiment_data['signal'] in ["BULLISH", "NEUTRAL"]:
                # Bewerte die Qualität des Setups (je niedriger RSI, desto besser der "Buy the Dip")
                score = (40 - ta_data['rsi']) + (sentiment_data['score'] * 0.2)
                if score > best_score:
                    best_score = score
                    best_trade = ta_data

        if best_trade:
            symbol = best_trade['symbol']
            price = best_trade['price']
            print(f"🎯 BESTES SETUP GEFUNDEN: {symbol} (Score: {best_score:.2f})")
            
            # Execute Buy
            try:
                # Berechne Amount (Simuliere $1000 Einsatz pro Trade)
                amount_to_buy = round(1000.0 / price, 4)
                
                res = requests.post(ORDER_URL, json={"pair": symbol, "side": "buy", "amount": amount_to_buy})
                if res.status_code == 200 and res.json().get("status") == "success":
                    print(f"✅ KAUF {symbol} erfolgreich!")
                    state['active_trades'].append({
                        "symbol": symbol,
                        "entry_price": price,
                        "highest_price": price,
                        "amount": amount_to_buy,
                        "timestamp": datetime.now().isoformat()
                    })
                    save_state(state)
                    
                    msg = f"📈 *BUY ALERT ({symbol})*\nRSI: {best_trade['rsi']} | Sentiment: {sentiment_data['score']}\nKaufpreis: ${price}\nEinsatz: $1000"
                    send_telegram(msg)
            except Exception as e:
                print(f"❌ Buy Error: {e}")
        else:
            print("⏳ Keine idealen Kauf-Setups aktuell.")
    else:
        print("💼 Portfolio ist voll (Max 3 Trades). Scanne nicht nach neuen Einstiegen.")

if __name__ == "__main__":
    execute()
