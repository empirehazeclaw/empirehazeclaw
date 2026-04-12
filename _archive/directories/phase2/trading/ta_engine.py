import ccxt
import pandas as pd
import pandas_ta as ta

def get_market_data(symbol='BTC/USDT', timeframe='1h', limit=100):
    """Holt historische OHLCV Daten von Binance (Kostenlos, Public API)"""
    exchange = ccxt.binance()
    bars = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def analyze_trend(symbol='BTC/USDT'):
    """Berechnet RSI und MACD und gibt ein Signal zurück"""
    try:
        df = get_market_data(symbol)
        # Berechne Indikatoren
        df.ta.rsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)

        latest = df.iloc[-1]
        rsi = latest['RSI_14']
        macd_hist = latest['MACDh_12_26_9'] # Histogram

        signal = "NEUTRAL"
        # Überverkauft & Momentum dreht ins Positive
        if rsi < 30 and macd_hist > 0:
            signal = "STRONG_BUY"
        elif rsi < 45:
            signal = "BUY"
        # Überkauft & Momentum dreht ins Negative
        elif rsi > 70 and macd_hist < 0:
            signal = "STRONG_SELL"
        elif rsi > 65:
            signal = "SELL"

        return {
            "symbol": symbol,
            "price": latest['close'],
            "rsi": round(rsi, 2),
            "macd_hist": round(macd_hist, 2),
            "signal": signal
        }
    except Exception as e:
        print(f"TA Error: {e}")
        return {"signal": "ERROR"}
