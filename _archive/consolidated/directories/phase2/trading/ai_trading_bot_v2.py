#!/usr/bin/env python3
"""
AI Trading Bot V2 - Professional Edition
=========================================
Features:
- Multi-Indicator Signals (RSI, MACD, Bollinger, Stochastic, ADX, VWAP, Supertrend, Ichimoku)
- Risk Management (Position Sizing, Trailing Stop, Max Drawdown)
- Position Tracking mit SL/TP
- Backtesting
- Discord Alerts
- Portfolio Performance

Setup:
    pip install ccxt pandas numpy requests python-dotenv
"""

import os
import sys
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, field
from enum import Enum
from threading import Thread

# Third-party imports
import ccxt
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# ============================================================
# KONFIGURATION
# ============================================================

load_dotenv()

# API Keys
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_SECRET = os.getenv('BINANCE_SECRET', '')

# Discord Webhook
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')

# Trading Modus
TRADING_MODE = os.getenv('TRADING_MODE', 'SIGNAL').upper()

# Trading Parameter
SYMBOLS = os.getenv('SYMBOLS', 'BTC/USDT,ETH/USDT').split(',')
TRADE_AMOUNT = float(os.getenv('TRADE_AMOUNT', '10'))
GRID_SPACING = float(os.getenv('GRID_SPACING', '2'))
GRID_LEVELS = int(os.getenv('GRID_LEVELS', '5'))
DCA_MULTIPLIER = float(os.getenv('DCA_MULTIPLIER', '1.5'))
DCA_MAX_LEVELS = int(os.getenv('DCA_MAX_LEVELS', '3'))
TAKE_PROFIT = float(os.getenv('TAKE_PROFIT', '5'))
STOP_LOSS = float(os.getenv('STOP_LOSS', '10'))
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))

# Backtest Parameter
BACKTEST_START = os.getenv('BACKTEST_START', '2025-01-01')
BACKTEST_END = os.getenv('BACKTEST_END', '2025-12-31')
INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', '1000'))

# Dry Run
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'

# Risk Management
TRAILING_STOP_PCT = float(os.getenv('TRAILING_STOP_PCT', '2.0'))
RISK_PER_TRADE_PCT = float(os.getenv('RISK_PER_TRADE_PCT', '2.0'))
MAX_OPEN_POSITIONS = int(os.getenv('MAX_OPEN_POSITIONS', '3'))
MAX_DRAWDOWN_PCT = float(os.getenv('MAX_DRAWDOWN_PCT', '20'))
USE_POSITION_SIZING = os.getenv('USE_POSITION_SIZING', 'true').lower() == 'true'

# ============================================================
# SETUP
# ============================================================

os.makedirs('/home/clawbot/.openclaw/logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/clawbot/.openclaw/logs/trading_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Exchange
exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Trade:
    id: str
    symbol: str
    side: str
    amount: float
    price: float
    timestamp: datetime
    pnl: float = 0.0
    status: str = "open"

@dataclass
class Position:
    symbol: str
    side: str
    entry_price: float
    amount: float
    entry_time: datetime
    stop_loss: float = 0.0
    take_profit: float = 0.0
    trailing_stop: float = 0.0
    highest_price: float = 0.0
    lowest_price: float = 0.0
    
    def update_trailing(self, current_price: float, trail_pct: float = 0.02):
        if self.side == 'buy':
            if current_price > self.highest_price:
                self.highest_price = current_price
                self.trailing_stop = current_price * (1 - trail_pct)
        else:
            if current_price < self.lowest_price:
                self.lowest_price = current_price
                self.trailing_stop = current_price * (1 + trail_pct)
    
    def check_exit(self, current_price: float) -> Optional[str]:
        if self.side == 'buy':
            if self.stop_loss > 0 and current_price <= self.stop_loss:
                return 'STOP_LOSS'
            if self.take_profit > 0 and current_price >= self.take_profit:
                return 'TAKE_PROFIT'
            if self.trailing_stop > 0 and current_price <= self.trailing_stop:
                return 'TRAILING_STOP'
        else:
            if self.stop_loss > 0 and current_price >= self.stop_loss:
                return 'STOP_LOSS'
            if self.take_profit > 0 and current_price <= self.take_profit:
                return 'TAKE_PROFIT'
            if self.trailing_stop > 0 and current_price >= self.trailing_stop:
                return 'TRAILING_STOP'
        return None

@dataclass
class Portfolio:
    holdings: Dict[str, float] = field(default_factory=dict)
    trades: List[Trade] = field(default_factory=list)
    positions: Dict[str, Position] = field(default_factory=dict)
    initial_capital: float = INITIAL_CAPITAL
    current_capital: float = INITIAL_CAPITAL
    peak_capital: float = INITIAL_CAPITAL
    max_drawdown: float = 0.0
    
    def update_equity(self, current_value: float):
        self.current_capital = current_value
        if current_value > self.peak_capital:
            self.peak_capital = current_value
        drawdown = (self.peak_capital - current_value) / self.peak_capital * 100
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
    
    def calculate_position_size(self, price: float, risk_pct: float = 2.0) -> float:
        risk_amount = self.current_capital * (risk_pct / 100)
        return risk_amount / price

portfolio = Portfolio()

# ============================================================
# TECHNICAL ANALYSIS
# ============================================================

def get_ohlcv(symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[pd.DataFrame]:
    """Hole OHLCV Daten mit Timeout"""
    result = []
    error = []
    
    def fetch_data():
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            result.append(ohlcv)
        except Exception as e:
            error.append(str(e))
    
    t = Thread(target=fetch_data)
    t.daemon = True
    t.start()
    t.join(timeout=10)
    
    if error:
        logger.warning(f"API Fehler {symbol}: {error[0]}")
        return None
    
    if result:
        df = pd.DataFrame(result[0], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    return None

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_ema(df: pd.DataFrame, period: int = 20) -> pd.Series:
    return df['close'].ewm(span=period, adjust=False).mean()

def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std: float = 2.0):
    sma = df['close'].rolling(window=period).mean()
    std_dev = df['close'].rolling(window=period).std()
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    return upper, sma, lower

def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = df['close'].ewm(span=fast).mean()
    ema_slow = df['close'].ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def calculate_stochastic(df: pd.DataFrame, period: int = 14):
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()
    k = 100 * (df['close'] - low_min) / (high_max - low_min)
    d = k.rolling(window=3).mean()
    return k, d

def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df['high']
    low = df['low']
    close = df['close']
    
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = tr1.combine(tr2, max).combine(tr3, max)
    atr = tr.rolling(window=period).mean()
    
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()
    return adx

def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
    return vwap

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = tr1.combine(tr2, max).combine(tr3, max)
    return tr.rolling(window=period).mean()

def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0):
    atr = calculate_atr(df, period)
    upper_band = (df['high'] + df['low']) / 2 + multiplier * atr
    lower_band = (df['high'] + df['low']) / 2 - multiplier * atr
    
    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(1, index=df.index)
    
    for i in range(1, len(df)):
        if df['close'].iloc[i] > upper_band.iloc[i-1]:
            direction.iloc[i] = 1
        elif df['close'].iloc[i] < lower_band.iloc[i-1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i-1]
        
        supertrend.iloc[i] = lower_band.iloc[i] if direction.iloc[i] == 1 else upper_band.iloc[i]
    
    return supertrend, direction

def calculate_ichimoku(df: pd.DataFrame) -> Dict:
    nine_period_high = df['high'].rolling(window=9).max()
    nine_period_low = df['low'].rolling(window=9).min()
    tenkan_sen = (nine_period_high + nine_period_low) / 2
    
    twenty_six_period_high = df['high'].rolling(window=26).max()
    twenty_six_period_low = df['low'].rolling(window=26).min()
    kijun_sen = (twenty_six_period_high + twenty_six_period_low) / 2
    
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
    
    fifty_two_period_high = df['high'].rolling(window=52).max()
    fifty_two_period_low = df['low'].rolling(window=52).min()
    senkou_span_b = ((fifty_two_period_high + fifty_two_period_low) / 2).shift(26)
    
    return {
        'tenkan_sen': tenkan_sen.iloc[-1] if len(tenkan_sen) > 0 else 0,
        'kijun_sen': kijun_sen.iloc[-1] if len(kijun_sen) > 0 else 0,
        'senkou_a': senkou_span_a.iloc[-1] if len(senkou_span_a) > 0 else 0,
        'senkou_b': senkou_span_b.iloc[-1] if len(senkou_span_b) > 0 else 0,
        'cloud_green': senkou_span_a.iloc[-1] > senkou_span_b.iloc[-1] if len(senkou_span_a) > 0 and len(senkou_span_b) > 0 else False
    }

def calculate_obv(df: pd.DataFrame) -> pd.Series:
    obv = pd.Series(index=df.index, dtype=float)
    obv.iloc[0] = df['volume'].iloc[0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + df['volume'].iloc[i]
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - df['volume'].iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    return obv

# ============================================================
# SIGNAL GENERATION
# ============================================================

def get_signal(symbol: str) -> Dict:
    """Generiert Trading Signal mit professionellen Indikatoren"""
    logger.info(f"Loading data for {symbol}...")
    df = get_ohlcv(symbol)
    logger.info(f"Data loaded for {symbol}: {len(df) if df is not None else 0} rows")
    if df is None or df.empty:
        return {'signal': 'HOLD', 'reason': 'Keine Daten'}
    
    current_price = df['close'].iloc[-1]
    
    # Indicators
    rsi = calculate_rsi(df).iloc[-1]
    ema20 = calculate_ema(df, 20).iloc[-1]
    ema50 = calculate_ema(df, 50).iloc[-1]
    ema200 = calculate_ema(df, 200).iloc[-1] if len(df) >= 200 else ema50
    upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(df)
    macd, signal_line, hist = calculate_macd(df)
    stoch_k, stoch_d = calculate_stochastic(df)
    adx = calculate_adx(df).iloc[-1] if len(df) >= 14 else 0
    vwap = calculate_vwap(df).iloc[-1]
    atr = calculate_atr(df).iloc[-1]
    
    # Supertrend
    supertrend, direction = calculate_supertrend(df)
    supertrend_val = supertrend.iloc[-1] if len(supertrend) > 0 else current_price
    supertrend_dir = direction.iloc[-1] if len(direction) > 0 else 1
    
    # Ichimoku
    ichimoku = calculate_ichimoku(df)
    
    # OBV
    obv = calculate_obv(df).iloc[-1]
    obv_prev = calculate_obv(df).iloc[-2] if len(df) > 1 else obv
    
    # Signale
    signals = []
    weights = []
    
    # RSI
    if rsi < 30:
        signals.append('BUY'); weights.append(2)
    elif rsi > 70:
        signals.append('SELL'); weights.append(2)
    
    # EMA Crossover
    if ema20 > ema50:
        signals.append('BUY'); weights.append(1.5)
    elif ema20 < ema50:
        signals.append('SELL'); weights.append(1.5)
    
    # MACD
    if macd.iloc[-1] > signal_line.iloc[-1] and hist.iloc[-1] > 0:
        signals.append('BUY'); weights.append(1.5)
    elif macd.iloc[-1] < signal_line.iloc[-1] and hist.iloc[-1] < 0:
        signals.append('SELL'); weights.append(1.5)
    
    # Bollinger
    if current_price < lower_bb.iloc[-1]:
        signals.append('BUY'); weights.append(2)
    elif current_price > upper_bb.iloc[-1]:
        signals.append('SELL'); weights.append(2)
    
    # Stochastic
    if stoch_k.iloc[-1] < 20:
        signals.append('BUY'); weights.append(1)
    elif stoch_k.iloc[-1] > 80:
        signals.append('SELL'); weights.append(1)
    
    # Trend EMA200
    if current_price > ema200:
        signals.append('BUY'); weights.append(1)
    elif current_price < ema200:
        signals.append('SELL'); weights.append(1)
    
    # ADX Trend
    if adx > 25:
        if current_price > vwap:
            signals.append('BUY'); weights.append(1)
        else:
            signals.append('SELL'); weights.append(1)
    
    # VWAP
    if current_price > vwap:
        signals.append('BUY'); weights.append(0.5)
    else:
        signals.append('SELL'); weights.append(0.5)
    
    # Supertrend
    if supertrend_dir == 1 and current_price > supertrend_val:
        signals.append('BUY'); weights.append(2)
    elif supertrend_dir == -1 and current_price < supertrend_val:
        signals.append('SELL'); weights.append(2)
    
    # Ichimoku
    if ichimoku['cloud_green'] and current_price > ichimoku['senkou_a']:
        signals.append('BUY'); weights.append(1.5)
    elif not ichimoku['cloud_green'] and current_price < ichimoku['senkou_b']:
        signals.append('SELL'); weights.append(1.5)
    
    # Ichimoku Cross
    if ichimoku['tenkan_sen'] > ichimoku['kijun_sen']:
        signals.append('BUY'); weights.append(1)
    elif ichimoku['tenkan_sen'] < ichimoku['kijun_sen']:
        signals.append('SELL'); weights.append(1)
    
    # OBV
    if obv > obv_prev:
        signals.append('BUY'); weights.append(0.5)
    elif obv < obv_prev:
        signals.append('SELL'); weights.append(0.5)
    
    # Weighted Score
    buy_weight = sum(w for s, w in zip(signals, weights) if s == 'BUY')
    sell_weight = sum(w for s, w in zip(signals, weights) if s == 'SELL')
    
    if buy_weight > sell_weight + 2:
        final_signal = 'BUY'
    elif sell_weight > buy_weight + 2:
        final_signal = 'SELL'
    else:
        final_signal = 'HOLD'
    
    return {
        'signal': final_signal,
        'price': current_price,
        'rsi': rsi,
        'stoch_k': stoch_k.iloc[-1],
        'adx': adx,
        'ema20': ema20,
        'ema50': ema50,
        'ema200': ema200,
        'macd': macd.iloc[-1],
        'histogram': hist.iloc[-1],
        'vwap': vwap,
        'atr': atr,
        'bb_upper': upper_bb.iloc[-1],
        'bb_lower': lower_bb.iloc[-1],
        'supertrend': supertrend_val,
        'supertrend_dir': supertrend_dir,
        'ichimoku_tenkan': ichimoku['tenkan_sen'],
        'ichimoku_cloud': ichimoku['cloud_green'],
        'buy_score': buy_weight,
        'sell_score': sell_weight,
        'reason': f"RSI:{rsi:.0f} ADX:{adx:.0f} ST:{supertrend_dir}"
    }

# ============================================================
# TRADING FUNCTIONS
# ============================================================

def get_balance() -> Dict:
    if DRY_RUN and not BINANCE_API_KEY:
        return {
            'free': {'USDT': 1000, 'BTC': 0.01, 'ETH': 0.1},
            'used': {},
            'total': {'USDT': 1000, 'BTC': 0.01, 'ETH': 0.1}
        }
    
    try:
        balance = exchange.fetch_balance()
        return {'free': balance['free'], 'used': balance['used'], 'total': balance['total']}
    except Exception as e:
        logger.error(f"Balance Fehler: {e}")
        if DRY_RUN:
            return {
                'free': {'USDT': 1000, 'BTC': 0.01, 'ETH': 0.1},
                'used': {},
                'total': {'USDT': 1000, 'BTC': 0.01, 'ETH': 0.1}
            }
        return {}

def place_order(symbol: str, side: str, amount: float, price: float = None,
                stop_loss: float = None, take_profit: float = None) -> Optional[Dict]:
    current_price = price or get_signal(symbol)['price']
    
    if DRY_RUN:
        logger.info(f"[DRY RUN] {side.upper()} {amount} {symbol} @ {current_price}")
        if side == 'buy':
            pos = Position(
                symbol=symbol, side='buy', entry_price=current_price,
                amount=amount, entry_time=datetime.now(),
                stop_loss=stop_loss or current_price * (1 - STOP_LOSS/100),
                take_profit=take_profit or current_price * (1 + TAKE_PROFIT/100),
                highest_price=current_price
            )
            portfolio.positions[symbol] = pos
        return {'id': 'dry_run', 'status': 'filled', 'price': current_price}
    
    try:
        if price:
            order = exchange.create_limit_order(symbol, side, amount, price)
        else:
            order = exchange.create_market_order(symbol, side, amount)
        
        logger.info(f"Order: {side.upper()} {amount} {symbol}")
        send_discord(f"📈 **{side.upper()}** - {amount} {symbol} @ ${current_price:.2f}")
        
        if side == 'buy':
            pos = Position(
                symbol=symbol, side='buy', entry_price=current_price,
                amount=amount, entry_time=datetime.now(),
                stop_loss=stop_loss or current_price * (1 - STOP_LOSS/100),
                take_profit=take_profit or current_price * (1 + TAKE_PROFIT/100),
                highest_price=current_price
            )
            portfolio.positions[symbol] = pos
        
        return order
    except Exception as e:
        logger.error(f"Order Fehler: {e}")
        send_discord(f"❌ Order Fehler: {e}")
        return None

def check_positions(symbol: str) -> Optional[str]:
    if symbol not in portfolio.positions:
        return None
    
    pos = portfolio.positions[symbol]
    current_price = get_signal(symbol)['price']
    
    pos.update_trailing(current_price, TRAILING_STOP_PCT / 100)
    exit_reason = pos.check_exit(current_price)
    
    if exit_reason:
        logger.info(f"Position closed: {symbol} - {exit_reason} @ {current_price}")
        pnl = (current_price - pos.entry_price) * pos.amount if pos.side == 'buy' else 0
        portfolio.current_capital += pnl
        send_discord(f"🔴 **{exit_reason}** - {symbol} @ ${current_price:.2f} | PnL: ${pnl:.2f}")
        del portfolio.positions[symbol]
        return exit_reason
    return None

def get_performance_metrics() -> Dict:
    total_return = portfolio.current_capital - portfolio.initial_capital
    return_pct = (total_return / portfolio.initial_capital) * 100
    return {
        'initial_capital': portfolio.initial_capital,
        'current_capital': portfolio.current_capital,
        'total_return': total_return,
        'return_pct': return_pct,
        'max_drawdown': portfolio.max_drawdown,
        'open_positions': len(portfolio.positions),
        'total_trades': len(portfolio.trades)
    }

# ============================================================
# STRATEGIES
# ============================================================

def strategy_signal(symbol: str, balance: Dict) -> bool:
    """Enhanced Signal Strategy"""
    
    exit_result = check_positions(symbol)
    if exit_result:
        logger.info(f"Position closed: {exit_result}")
    
    if len(portfolio.positions) >= MAX_OPEN_POSITIONS:
        return False
    
    if portfolio.max_drawdown >= MAX_DRAWDOWN_PCT:
        logger.warning(f"Max Drawdown: {portfolio.max_drawdown:.1f}%")
        send_discord(f"⚠️ Max Drawdown ({portfolio.max_drawdown:.1f}%) - Trading paused")
        return False
    
    analysis = get_signal(symbol)
    price = analysis['price']
    
    usdt = balance['free'].get('USDT', 0)
    asset = balance['free'].get(symbol.split('/')[0], 0)
    
    trade_amount = portfolio.calculate_position_size(price, RISK_PER_TRADE_PCT) if USE_POSITION_SIZING else TRADE_AMOUNT
    
    if analysis['signal'] == 'BUY' and usdt >= trade_amount:
        stop_loss = price * (1 - STOP_LOSS / 100)
        take_profit = price * (1 + TAKE_PROFIT / 100)
        
        logger.info(f"SIGNAL BUY: {symbol} @ ${price:.2f}")
        logger.info(f"  RSI:{analysis['rsi']:.0f} ADX:{analysis['adx']:.0f} ST:{analysis['supertrend_dir']}")
        logger.info(f"  SL:${stop_loss:.2f} TP:${take_profit:.2f}")
        
        place_order(symbol, 'buy', trade_amount, price, stop_loss, take_profit)
        return True
    
    elif analysis['signal'] == 'SELL' and asset > 0.0001:
        sell_amount = asset * 0.1
        logger.info(f"SIGNAL SELL: {symbol} @ ${price:.2f}")
        place_order(symbol, 'sell', sell_amount)
        return True
    
    return False

# ============================================================
# NOTIFICATIONS
# ============================================================

def send_discord(message: str, embed: Dict = None):
    if not DISCORD_WEBHOOK_URL:
        return
    payload = {"content": message, "username": "TradingBot V2"}
    if embed:
        payload["embeds"] = [embed]
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Discord Fehler: {e}")

def send_daily_report():
    balance = get_balance()
    metrics = get_performance_metrics()
    portfolio.update_equity(balance.get('free', {}).get('USDT', 0))
    
    color = 3066993 if metrics['return_pct'] >= 0 else 15158332
    
    embed = {
        "title": "📊 Trading Bot V2 - Daily Report",
        "color": color,
        "fields": [
            {"name": "Mode", "value": TRADING_MODE, "inline": True},
            {"name": "Positions", "value": f"{metrics['open_positions']}/{MAX_OPEN_POSITIONS}", "inline": True},
            {"name": "Capital", "value": f"${metrics['current_capital']:.2f}", "inline": True},
            {"name": "Return", "value": f"{metrics['return_pct']:+.2f}%", "inline": True},
            {"name": "Max DD", "value": f"{metrics['max_drawdown']:.1f}%", "inline": True}
        ],
        "footer": {"text": f"Bot V2 • {datetime.now().strftime('%Y-%m-%d %H:%M')}"}
    }
    
    for symbol in SYMBOLS:
        analysis = get_signal(symbol)
        emoji = "🟢" if analysis['signal'] == 'BUY' else "🔴" if analysis['signal'] == 'SELL' else "⚪"
        embed["fields"].append({
            "name": f"{emoji} {symbol}",
            "value": f"{analysis['signal']} @ ${analysis['price']:.2f}\nRSI:{analysis['rsi']:.0f} ADX:{analysis['adx']:.0f}",
            "inline": False
        })
    
    send_discord("", embed)

# ============================================================
# MAIN
# ============================================================

def main():
    logger.info("=" * 50)
    logger.info("🚀 AI Trading Bot V2 - Professional")
    logger.info(f"Mode: {TRADING_MODE} | Symbols: {SYMBOLS}")
    logger.info(f"Dry Run: {DRY_RUN}")
    
    if not DRY_RUN and BINANCE_API_KEY:
        try:
            balance = exchange.fetch_balance()
            logger.info(f"✅ API OK | USDT: ${balance['free'].get('USDT', 0):.2f}")
        except Exception as e:
            logger.error(f"❌ API Fehler: {e}")
            return
    else:
        logger.info(f"✅ Dry Run | USDT: ${portfolio.initial_capital}")
    
    send_discord(f"🚀 **Trading Bot V2 gestartet!** Mode: {TRADING_MODE}")
    
    while True:
        try:
            balance = get_balance()
            
            for symbol in SYMBOLS:
                symbol = symbol.strip()
                if TRADING_MODE == 'SIGNAL':
                    strategy_signal(symbol, balance)
            
            if datetime.now().minute == 0:
                send_daily_report()
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Bot gestoppt!")
            send_discord("🛑 Bot gestoppt")
            break
        except Exception as e:
            logger.error(f"Loop Fehler: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
