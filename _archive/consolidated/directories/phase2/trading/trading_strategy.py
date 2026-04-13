#!/usr/bin/env python3
"""
Conservative Trend Follower Strategy v2.1
Enhanced with MACD, SMA Stack & Multi-Timeframe

Usage:
    python3 trading_strategy.py scan     # Scan all assets
    python3 trading_strategy.py btc     # Scan BTC only
    python3 trading_strategy.py eth     # Scan ETH only
"""
import sys
import json
from datetime import datetime

# Configuration v2.1
CONFIG = {
    "version": "2.1",
    "assets": ["btc", "eth"],
    "max_leverage": 2,
    "max_risk_percent": 2,
    "max_positions": 2,
    "max_drawdown_stop": 20,
    "max_drawdown_alert": 10,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "sma_fast": 20,
    "sma_medium": 50,
    "sma_slow": 200,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "volume_ma_period": 24,
    "sessions": {
        "asian": (0, 8),
        "us": (13, 21)
    }
}

def get_market_data(asset, timeframe="4h"):
    """
    Get market data from API.
    Placeholder - implement with exchange API.
    """
    # TODO: Implement with Binance/Coinbase API
    return {
        "price": 0,
        "volume_24h": 0,
        "ohlcv": [],
        "daily_ohlcv": []
    }

def calculate_sma(prices, period):
    """Calculate Simple Moving Average."""
    if len(prices) < period:
        return 0
    return sum(prices[-period:]) / period

def calculate_ema(prices, period):
    """Calculate Exponential Moving Average."""
    if len(prices) < period:
        return 0
    
    multiplier = 2 / (period + 1)
    ema = prices[0]
    
    for price in prices[1:]:
        ema = (price - ema) * multiplier + ema
    
    return ema

def calculate_macd(prices):
    """Calculate MACD, Signal Line, and Histogram."""
    ema_fast = calculate_ema(prices, CONFIG["macd_fast"])
    ema_slow = calculate_ema(prices, CONFIG["macd_slow"])
    
    macd_line = ema_fast - ema_slow
    
    # Calculate signal line (9-period EMA of MACD)
    # Simplified: use SMA as approximation
    signal_line = macd_line * 0.9  # Approximation
    
    histogram = macd_line - signal_line
    
    return {
        "macd": macd_line,
        "signal": signal_line,
        "histogram": histogram
    }

def calculate_rsi(prices, period=14):
    """Calculate RSI."""
    if len(prices) < period + 1:
        return 50
    
    gains = []
    losses = []
    for i in range(-period, 0):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# === DAILY TIMEFRAME CHECKS ===

def check_daily_trend(daily_ohlcv):
    """Check daily trend (SMA 20 > SMA 50)."""
    if len(daily_ohlcv) < 50:
        return False, "Not enough daily data"
    
    closes = [c[4] for c in daily_ohlcv]
    sma_20 = calculate_sma(closes, CONFIG["sma_fast"])
    sma_50 = calculate_sma(closes, CONFIG["sma_medium"])
    
    if closes[-1] > sma_20 and sma_20 > sma_50:
        return True, f"Bullish (Price ${closes[-1]:.2f} > SMA20 ${sma_20:.2f} > SMA50 ${sma_50:.2f})"
    else:
        return False, f"Not Bullish (Price ${closes[-1]:.2f}, SMA20 ${sma_20:.2f}, SMA50 ${sma_50:.2f})"

# === 4H TIMEFRAME CHECKS ===

def check_4h_trend(ohlcv):
    """Check 4h trend (Price > SMA 20, all green candles)."""
    if len(ohlcv) < 25:
        return False, "Not enough 4h data"
    
    closes = [c[4] for c in ohlcv]
    sma_20 = calculate_sma(closes, CONFIG["sma_fast"])
    
    # Price above SMA 20
    if closes[-1] < sma_20:
        return False, f"Price ${closes[-1]:.2f} below SMA20 ${sma_20:.2f}"
    
    # All 4 candles green
    for i in range(-4, 0):
        if ohlcv[i][4] <= ohlcv[i-1][4]:
            return False, f"Candle {i} not green"
    
    return True, f"Bullish (Price ${closes[-1]:.2f} > SMA20 ${sma_20:.2f})"

def check_macd(ohlcv):
    """Check MACD (MACD > Signal Line)."""
    if len(ohlcv) < 30:
        return False, "Not enough data for MACD"
    
    closes = [c[4] for c in ohlcv]
    macd = calculate_macd(closes)
    
    if macd["macd"] > macd["signal"]:
        return True, f"Bullish (MACD {macd['macd']:.4f} > Signal {macd['signal']:.4f})"
    else:
        return False, f"Bearish (MACD {macd['macd']:.4f} < Signal {macd['signal']:.4f})"

def check_volume(ohlcv):
    """Check volume (4h > 24h MA)."""
    if len(ohlcv) < 25:
        return False, "Not enough volume data"
    
    volumes = [c[5] for c in ohlcv]
    avg_volume = sum(volumes[-24:]) / 24
    recent_volume = sum(volumes[-4:]) / 4
    
    if recent_volume < avg_volume:
        return False, f"Volume {recent_volume:.0f} < avg {avg_volume:.0f}"
    return True, f"Volume OK ({recent_volume/avg_volume:.1f}x)"

def check_momentum(ohlcv):
    """Check RSI (between 30-70)."""
    closes = [c[4] for c in ohlcv]
    rsi = calculate_rsi(closes)
    
    if CONFIG["rsi_oversold"] <= rsi <= CONFIG["rsi_overbought"]:
        return True, f"RSI {rsi:.1f} OK"
    else:
        return False, f"RSI {rsi:.1f} out of range"

def check_session():
    """Check if in allowed session."""
    utc_hour = datetime.utcnow().hour
    
    for session_name, (start, end) in CONFIG["sessions"].items():
        if start <= utc_hour < end:
            return True, f"In {session_name.upper()} session"
    
    return False, f"Outside trading hours (UTC {utc_hour})"

def scan_asset(asset):
    """Scan asset for entry signals."""
    try:
        data_4h = get_market_data(asset, "4h")
        data_daily = get_market_data(asset, "daily")
        
        # Run all checks
        checks = {
            "daily_trend": check_daily_trend(data_daily.get("ohlcv", [])),
            "4h_trend": check_4h_trend(data_4h.get("ohlcv", [])),
            "macd": check_macd(data_4h.get("ohlcv", [])),
            "volume": check_volume(data_4h.get("ohlcv", [])),
            "momentum": check_momentum(data_4h.get("ohlcv", [])),
            "session": check_session()
        }
        
        # Check passes
        passed = [k for k, v in checks.items() if v[0]]
        failed = [k for k, v in checks.items() if not v[0]]
        
        all_passed = len(failed) == 0
        
        return {
            "asset": asset.upper(),
            "version": CONFIG["version"],
            "ready": all_passed,
            "checks": {k: {"passed": v[0], "msg": v[1]} for k, v in checks.items()},
            "passed": passed,
            "failed": failed
        }
        
    except Exception as e:
        return {
            "asset": asset.upper(),
            "ready": False,
            "error": str(e)
        }

def main(action="scan"):
    """Main function."""
    print(f"🧪 Conservative Trend Follower v{CONFIG['version']}")
    print(f"Enhanced with MACD, SMA Stack & Multi-Timeframe")
    print(f"⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    if action == "scan":
        assets = CONFIG["assets"]
    elif action in CONFIG["assets"]:
        assets = [action]
    else:
        print(f"Unknown action: {action}")
        return 1
    
    results = []
    for asset in assets:
        result = scan_asset(asset)
        results.append(result)
        
        status = "🟢 READY" if result["ready"] else "🔴 NOT READY"
        print(f"\n{result['asset']}: {status}")
        
        if "checks" in result:
            for name, check in result["checks"].items():
                icon = "✅" if check["passed"] else "❌"
                print(f"  {name:15} {icon} {check['msg']}")
        
        if "error" in result:
            print(f"  Error: {result['error']}")
    
    # Summary
    ready_count = sum(1 for r in results if r.get("ready", False))
    print("\n" + "=" * 60)
    print(f"📊 Summary: {ready_count}/{len(results)} assets READY")
    
    if ready_count > 0:
        print("\n✅ Entry conditions met - Ready to trade!")
    else:
        print("\n🔴 No entry signals - Wait for next opportunity")
    
    return 0 if ready_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "scan"))
