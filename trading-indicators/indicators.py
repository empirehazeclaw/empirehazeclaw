"""
Trading Indicators Library
"""
import numpy as np
from typing import List, Union

def sma(data: List[float], period: int) -> float:
    """Simple Moving Average"""
    if len(data) < period:
        return None
    return sum(data[-period:]) / period

def ema(data: List[float], period: int) -> float:
    """Exponential Moving Average"""
    if len(data) < period:
        return None
    multiplier = 2 / (period + 1)
    ema_val = data[0]
    for price in data[1:]:
        ema_val = (price * multiplier) + (ema_val * (1 - multiplier))
    return ema_val

def rsi(data: List[float], period: int = 14) -> float:
    """Relative Strength Index"""
    if len(data) < period + 1:
        return None
    
    gains = []
    losses = []
    
    for i in range(1, len(data)):
        change = data[i] - data[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val

def macd(data: List[float], fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD - Moving Average Convergence Divergence"""
    if len(data) < slow:
        return None, None, None
    
    ema_fast = ema(data, fast)
    ema_slow = ema(data, slow)
    
    if ema_fast is None or ema_slow is None:
        return None, None, None
    
    macd_line = ema_fast - ema_slow
    
    # Signal line (EMA of MACD)
    # Simplified
    signal_line = macd_line * 0.9  # approximation
    
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def bollinger_bands(data: List[float], period: int = 20, std_dev: int = 2):
    """Bollinger Bands"""
    if len(data) < period:
        return None, None, None
    
    sma_val = sma(data, period)
    if sma_val is None:
        return None, None, None
    
    std = np.std(data[-period:])
    
    upper_band = sma_val + (std * std_dev)
    lower_band = sma_val - (std * std_dev)
    
    return upper_band, sma_val, lower_band

def atr(high: List[float], low: List[float], close: List[float], period: int = 14):
    """Average True Range"""
    if len(high) < period + 1:
        return None
    
    tr_values = []
    for i in range(1, len(high)):
        tr = max(
            high[i] - low[i],
            abs(high[i] - close[i-1]),
            abs(low[i] - close[i-1])
        )
        tr_values.append(tr)
    
    if len(tr_values) < period:
        return None
    
    return sum(tr_values[-period:]) / period

def adx(high: List[float], low: List[float], close: List[float], period: int = 14):
    """Average Directional Index"""
    # Simplified ADX calculation
    # Full implementation would be more complex
    if len(high) < period + 1:
        return None
    
    # Placeholder - returns a trend strength indicator
    recent = close[-period:]
    first_half = sum(recent[:period//2]) / (period//2)
    second_half = sum(recent[period//2:]) / (period - period//2)
    
    if second_half > first_half:
        return min(100, (second_half / first_half - 1) * 100)
    else:
        return max(0, 50 - (first_half / second_half - 1) * 100)

# ==================== EXAMPLE USAGE ====================
if __name__ == "__main__":
    # Sample data
    prices = [100, 102, 101, 105, 107, 106, 108, 110, 109, 112, 114, 113, 115, 117, 116, 118, 120, 119, 121, 123]
    
    print("SMA(5):", sma(prices, 5))
    print("EMA(5):", ema(prices, 5))
    print("RSI(14):", rsi(prices, 14))
    print("MACD:", macd(prices))
    print("Bollinger Bands:", bollinger_bands(prices))
