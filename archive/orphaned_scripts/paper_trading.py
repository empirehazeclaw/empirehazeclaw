#!/usr/bin/env python3
"""
Paper Trading Script - Live Simulation
Simulates trades based on Strategy v3 without real money
"""
import requests
import time
import json
from datetime import datetime

# ==================== CONFIG ====================
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
INTERVAL = "4h"
PAPER_CAPITAL = 10000  # Virtuelles Kapital
RISK_PER_TRADE = 0.02  # 2%
TAKE_PROFIT = 0.04     # 4%
STOP_LOSS = 0.02       # 2%
CHECK_INTERVAL = 300   # 5 Minuten

# ==================== STATE ====================
STATE_FILE = "/home/clawbot/.openclaw/workspace/data/paper_trading_state.json"

def load_state():
    """Load paper trading state."""
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {
            "capital": PAPER_CAPITAL,
            "positions": {},  # {symbol: {entry, size, time}}
            "trades": [],
            "start_time": datetime.now().isoformat()
        }

def save_state(state):
    """Save paper trading state."""
    import os
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ==================== DATA ====================
def get_binance_klines(symbol, interval, limit=100):
    """Fetch recent klines from Binance."""
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    
    resp = requests.get(url, params=params, timeout=30)
    data = resp.json()
    
    candles = []
    for d in data:
        candles.append({
            "time": d[0] // 1000,
            "open": float(d[1]),
            "high": float(d[2]),
            "low": float(d[3]),
            "close": float(d[4]),
            "volume": float(d[5])
        })
    return candles

def get_current_price(symbol):
    """Get current price."""
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": symbol}
    resp = requests.get(url, params=params, timeout=10)
    return float(resp.json()["price"])

# ==================== INDICATORS ====================
def sma(data, period):
    if len(data) < period:
        return None
    return sum(data[-period:]) / period

def ema(data, period):
    if len(data) < period:
        return None
    multiplier = 2 / (period + 1)
    ema_val = data[0]
    for price in data[1:]:
        ema_val = (price * multiplier) + (ema_val * (1 - multiplier))
    return ema_val

def rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def macd(prices, fast=12, slow=26):
    if len(prices) < slow:
        return None, None, None
    fast_ema = ema(prices, fast)
    slow_ema = ema(prices, slow)
    if fast_ema is None or slow_ema is None:
        return None, None, None
    macd_line = fast_ema - slow_ema
    signal_line = macd_line * 0.9
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

# ==================== STRATEGY ====================
def check_entry(symbol):
    """Check if we should enter a position."""
    candles = get_binance_klines(symbol, INTERVAL)
    closes = [c["close"] for c in candles]
    volumes = [c["volume"] for c in candles]
    
    if len(closes) < 50:
        return False, "Warming up"
    
    # 1. Trend Filter
    ma24 = sma(closes, 24)
    if closes[-1] < ma24:
        return False, f"Price ${closes[-1]:.2f} < MA24 ${ma24:.2f}"
    
    # Last 4 candles green
    green_count = sum(1 for i in range(-4, 0) if candles[i]["close"] > candles[i-1]["close"])
    if green_count < 3:
        return False, f"Only {green_count}/4 green candles"
    
    # 2. Volume (relaxed to 0.8x)
    vol_ma = sma(volumes, 24)
    if volumes[-1] < vol_ma * 0.8:
        return False, "Volume low"
    
    # 3. RSI (30-70)
    rsi_val = rsi(closes, 14)
    if rsi_val is None:
        return False, "RSI unavailable"
    if rsi_val > 70:
        return False, f"RSI {rsi_val:.1f} overbought"
    if rsi_val < 30:
        return False, f"RSI {rsi_val:.1f} oversold"
    
    # 4. MACD
    macd_line, signal, hist = macd(closes)
    if macd_line and macd_line < signal:
        return False, f"MACD bearisch"
    
    # 5. Session check
    hour = datetime.now().hour
    if hour < 2 or hour >= 23:
        return False, f"Bad hour {hour}"
    
    return True, f"READY - RSI:{rsi_val:.1f} MACD:{macd_line:.2f}"

def check_exit(symbol, entry_price, entry_time):
    """Check if we should exit position."""
    current_price = get_current_price(symbol)
    pnl_pct = (current_price - entry_price) / entry_price
    
    # Stop Loss
    if pnl_pct <= -STOP_LOSS:
        return True, "STOP_LOSS", pnl_pct
    
    # Take Profit
    if pnl_pct >= TAKE_PROFIT:
        return True, "TAKE_PROFIT", pnl_pct
    
    # Time Stop (48 candles = 8 days)
    candles = get_binance_klines(symbol, INTERVAL)
    if len(candles) > 48:
        time_passed = (candles[-1]["time"] - entry_time) / (1000 * 3600)
        if time_passed > 192:  # 8 days
            return True, "TIME_STOP", pnl_pct
    
    # RSI Overbought exit
    closes = [c["close"] for c in candles]
    rsi_val = rsi(closes, 14)
    if rsi_val and rsi_val > 75:
        return True, "RSI_OVERBOUGHT", pnl_pct
    
    return False, "HOLD", 0

# ==================== MAIN ====================
def run_paper_trading():
    state = load_state()
    print(f"📄 Paper Trading Started")
    print(f"💰 Capital: ${state['capital']:,.2f}")
    print(f"📊 Monitoring: {', '.join(SYMBOLS)}")
    print("-" * 40)
    
    while True:
        try:
            for symbol in SYMBOLS:
                # Check for existing position
                if symbol in state["positions"]:
                    pos = state["positions"][symbol]
                    current_price = get_current_price(symbol)
                    
                    should_exit, reason, pnl = check_exit(
                        symbol, pos["entry"], pos["time"]
                    )
                    
                    if should_exit:
                        # Calculate PnL
                        pnl_amount = state["capital"] * pnl
                        state["capital"] += pnl_amount
                        
                        trade = {
                            "symbol": symbol,
                            "entry": pos["entry"],
                            "exit": current_price,
                            "pnl": pnl,
                            "pnl_amount": pnl_amount,
                            "reason": reason,
                            "time": datetime.now().isoformat()
                        }
                        state["trades"].append(trade)
                        
                        print(f"🔴 EXIT {symbol} | ${current_price:,.2f} | {reason} | {pnl*100:+.2f}% | ${pnl_amount:+,.2f}")
                        
                        del state["positions"][symbol]
                        save_state(state)
                
                # Check for entry (if no position)
                else:
                    if len(state["positions"]) >= 2:
                        continue  # Max 2 positions
                    
                    can_enter, reason = check_entry(symbol)
                    
                    if can_enter:
                        current_price = get_current_price(symbol)
                        position_size = state["capital"] * RISK_PER_TRADE / STOP_LOSS
                        
                        state["positions"][symbol] = {
                            "entry": current_price,
                            "size": position_size,
                            "time": int(datetime.now().timestamp() * 1000)
                        }
                        
                        print(f"🟢 ENTER {symbol} | ${current_price:,.2f} | {reason}")
                        save_state(state)
            
            # Status every loop
            if state["positions"]:
                positions = ", ".join([f"{s}: ${p['entry']:.2f}" for s, p in state["positions"].items()])
                print(f"⏰ {datetime.now().strftime('%H:%M')} | Open: {positions} | Capital: ${state['capital']:,.2f}")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n🛑 Paper Trading Stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        state = load_state()
        print(f"💰 Capital: ${state['capital']:,.2f}")
        print(f"📂 Positions: {len(state['positions'])}")
        print(f"📜 Trades: {len(state['trades'])}")
        wins = sum(1 for t in state["trades"] if t["pnl"] > 0)
        if state["trades"]:
            print(f"🏆 Win Rate: {wins/len(state['trades'])*100:.1f}%")
    else:
        run_paper_trading()
