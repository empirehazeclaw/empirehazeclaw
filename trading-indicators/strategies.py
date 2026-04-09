"""
Trading Strategies using Indicators
"""
from indicators import rsi, macd, bollinger_bands, sma

def strategy_rsi(prices: list) -> str:
    """RSI Strategy - Buy oversold, sell overbought"""
    current_rsi = rsi(prices)
    
    if current_rsi is None:
        return "HOLD"
    
    if current_rsi < 30:
        return "BUY"  # Oversold - potential buy
    elif current_rsi > 70:
        return "SELL"  # Overbought - potential sell
    else:
        return "HOLD"

def strategy_macd(prices: list) -> str:
    """MACD Strategy - Trend following"""
    macd_line, signal, hist = macd(prices)
    
    if macd_line is None or signal is None:
        return "HOLD"
    
    if hist > 0 and hist > hist * 0.1:  # Bullish crossover
        return "BUY"
    elif hist < 0 and hist < hist * 0.1:  # Bearish crossover
        return "SELL"
    else:
        return "HOLD"

def strategy_bollinger(prices: list) -> str:
    """Bollinger Bands Strategy - Mean reversion"""
    upper, middle, lower = bollinger_bands(prices)
    
    if upper is None:
        return "HOLD"
    
    current = prices[-1]
    
    if current <= lower:
        return "BUY"  # Price near lower band
    elif current >= upper:
        return "SELL"  # Price near upper band
    else:
        return "HOLD"

def strategy_ma_cross(prices: list, fast: int = 10, slow: int = 20) -> str:
    """Moving Average Crossover"""
    if len(prices) < slow:
        return "HOLD"
    
    ma_fast = sma(prices, fast)
    ma_slow = sma(prices, slow)
    
    if ma_fast is None or ma_slow is None:
        return "HOLD"
    
    # Check previous crossover
    prev_fast = sma(prices[:-1], fast)
    prev_slow = sma(prices[:-1], slow)
    
    if prev_fast is None or prev_slow is None:
        return "HOLD"
    
    # Golden Cross (Bullish)
    if prev_fast <= prev_slow and ma_fast > ma_slow:
        return "BUY"
    # Death Cross (Bearish)
    elif prev_fast >= prev_slow and ma_fast < ma_slow:
        return "SELL"
    else:
        return "HOLD"

# Combined strategy
def combined_strategy(prices: list) -> dict:
    """Combine multiple strategies"""
    return {
        "rsi": strategy_rsi(prices),
        "macd": strategy_macd(prices),
        "bollinger": strategy_bollinger(prices),
        "ma_cross": strategy_ma_cross(prices)
    }
