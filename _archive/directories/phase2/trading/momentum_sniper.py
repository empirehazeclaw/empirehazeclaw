#!/usr/bin/env python3
"""
Momentum-Sniper Agent
Automatische Trading-Signal Erkennung
"""

import yfinance as yf
import json
from datetime import datetime
import os

# Configuration
YAHOO_URL = "https://query1.finance.yahoofinance.com/v8/finance/chart/"
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

# Watchlist - Symbols to monitor
WATCHLIST = [
    "AAPL", "TSLA", "NVDA", "AMD", "MSFT",  # Tech
    "SPY", "QQQ", "IWM",  # Indices
    "BTC-USD", "ETH-USD"  # Crypto
]

def get_stock_data(symbol):
    """Hole Stock Data von Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1mo", interval="1d")
        
        if data.empty:
            return None
        
        return {
            "close": data["Close"].tolist(),
            "open": data["Open"].tolist(),
            "high": data["High"].tolist(),
            "low": data["Low"].tolist(),
            "volume": data["Volume"].tolist()
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def calculate_rsi(prices, period=14):
    """Berechne RSI"""
    if len(prices) < period:
        return None
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def detect_pin_bar(prices,opens,closes, highs, lows):
    """Erkenne Pin Bar Pattern"""
    signals = []
    
    for i in range(-5, 0):
        body = abs(closes[i] - opens[i])
        upper_wick = highs[i] - max(closes[i], opens[i])
        lower_wick = min(closes[i], opens[i]) - lows[i]
        
        # Bullish Pin Bar: long lower wick, small body at top
        if lower_wick > body * 2 and upper_wick < body:
            signals.append({
                "pattern": "Bullish Pin Bar",
                "direction": "LONG",
                "price": closes[i],
                "confidence": min(100, int(lower_wick/body * 30))
            })
        
        # Bearish Pin Bar: long upper wick, small body at bottom
        if upper_wick > body * 2 and lower_wick < body:
            signals.append({
                "pattern": "Bearish Pin Bar",
                "direction": "SHORT",
                "price": closes[i],
                "confidence": min(100, int(upper_wick/body * 30))
            })
    
    return signals

def analyze_symbol(symbol):
    """Analysiere ein Symbol"""
    data = get_stock_data(symbol)
    if not data or not data.get("close"):
        return None
    
    try:
        closes = [c for c in data["close"] if c is not None]
        opens = [o for o in data["open"] if o is not None]
        highs = [h for h in data["high"] if h is not None]
        lows = [l for l in data["low"] if l is not None]
        
        if not closes or len(closes) < 15:
            return None
        
        current_price = closes[-1]
        
        # Calculate RSI
        rsi = calculate_rsi(closes)
        
        # Detect patterns
        patterns = detect_pin_bar(closes, opens, closes, highs, lows)
        
        result = {
            "symbol": symbol,
            "price": current_price,
            "rsi": round(rsi, 2) if rsi else None,
            "patterns": patterns,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

def generate_report():
    """Generiere täglichen Report"""
    report = []
    report.append("📊 Momentum Sniper - Daily Report")
    report.append(f"Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    
    for symbol in WATCHLIST:
        result = analyze_symbol(symbol)
        if result and result.get("patterns"):
            report.append(f"🎯 **{result['symbol']}** (${result['price']})")
            for p in result["patterns"]:
                report.append(f"  {p['pattern']}: {p['direction']} @ ${p['price']} (Conf: {p['confidence']}%)")
            report.append("")
    
    return "\n".join(report) if len(report) > 3 else "Keine Signale heute."

if __name__ == "__main__":
    print(generate_report())
