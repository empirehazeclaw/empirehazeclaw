import ccxt
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
import random

print("🚀 Starte 1-Jahres Backtest (1h Chart) MIT SIMULIERTEM SENTIMENT...")

exchange = ccxt.binance({'enableRateLimit': True})
coins = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
data = {}

start_date = datetime.now() - timedelta(days=365)
since_start = exchange.parse8601(start_date.strftime('%Y-%m-%dT00:00:00Z'))

for symbol in coins:
    print(f"  Lade historische 1h-Daten für {symbol}...")
    all_ohlcv = []
    current_since = since_start
    
    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, '1h', since=current_since, limit=1000)
            if not ohlcv or (all_ohlcv and ohlcv[-1][0] == all_ohlcv[-1][0]) or len(ohlcv) < 1000:
                all_ohlcv.extend(ohlcv)
                break
            all_ohlcv.extend(ohlcv)
            current_since = ohlcv[-1][0] + 1
        except: break
            
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    df.ta.rsi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    
    # 🌟 SIMULIERTES SENTIMENT (Der "News-Filter")
    # Wir können historische News nicht abrufen. Aber wir wissen: 
    # Wenn der Preis (close) über dem 50-Tage-Durchschnitt liegt (SMA 50),
    # ist das makro-ökonomische Sentiment tendenziell "bullisch" (gute News).
    # Fällt der Kurs darunter, sind die News meist "bärisch".
    df.ta.sma(length=50*24, append=True) # 50 Tage á 24 Stunden = 1200
    
    df.dropna(inplace=True)
    df.drop_duplicates(subset=['timestamp'], inplace=True)
    data[symbol] = df

initial_balance = 10000.0
balance = initial_balance
positions = []
trade_history = []
btc_dates = data['BTC/USDT']['timestamp'].tolist()

for current_date in btc_dates:
    # 1. RISK MANAGEMENT
    for pos in positions[:]:
        symbol = pos['symbol']
        coin_df = data[symbol]
        row_series = coin_df[coin_df['timestamp'] == current_date]
        if row_series.empty: continue
        
        row = row_series.iloc[0]
        current_price = row['close']
        
        if current_price > pos['highest_price']:
            pos['highest_price'] = current_price
            
        entry = pos['entry_price']
        highest = pos['highest_price']
        
        pnl_pct = ((current_price - entry) / entry) * 100
        drawdown_from_high = ((highest - current_price) / highest) * 100
        
        sell_reason = None
        if drawdown_from_high >= 5.0 and pnl_pct > 2.0:
            sell_reason = "Trailing Stop"
        elif pnl_pct <= -5.0:
            sell_reason = "Stop Loss (-5%)"
        elif pnl_pct >= 25.0:
            sell_reason = "Take Profit (+25%)"
            
        if sell_reason:
            revenue = pos['amount'] * current_price
            balance += revenue
            trade_history.append({"symbol": symbol, "pnl_pct": pnl_pct, "reason": sell_reason})
            positions.remove(pos)

    # 2. EINSTIEGE MIT SENTIMENT-FILTER
    if len(positions) < 3:
        for symbol in coins:
            if any(p['symbol'] == symbol for p in positions): continue
                
            coin_df = data[symbol]
            row_series = coin_df[coin_df['timestamp'] == current_date]
            if row_series.empty: continue
            
            row = row_series.iloc[0]
            rsi = row.get('RSI_14', 50)
            macd_hist = row.get('MACDh_12_26_9', 0)
            sma_50d = row.get('SMA_1200', row['close'])
            
            # 🌟 NEUE LOGIK: 
            # 1. RSI < 35 (Kurzfristiger Dip / Überverkauft)
            # 2. MACD > 0 (Momentum dreht hoch)
            # 3. Sentiment-Filter: Der aktuelle Preis MUSS über dem 50-Tage SMA liegen. 
            #    -> Das bedeutet: Wir kaufen nur Dips in einem Makro-Bullenmarkt (gute News-Lage)!
            
            sentiment_bullish = row['close'] > sma_50d
            
            if rsi < 35 and macd_hist > 0 and sentiment_bullish:
                trade_amount_usd = 1000.0
                if balance >= trade_amount_usd:
                    balance -= trade_amount_usd
                    positions.append({
                        "symbol": symbol,
                        "entry_price": row['close'],
                        "highest_price": row['close'],
                        "amount": trade_amount_usd / row['close']
                    })

for pos in positions:
    symbol = pos['symbol']
    last_price = data[symbol].iloc[-1]['close']
    revenue = pos['amount'] * last_price
    balance += revenue
    trade_history.append({"symbol": symbol, "pnl_pct": ((last_price - pos['entry_price']) / pos['entry_price']) * 100, "reason": "Backtest End"})

print("\n=== 📊 1-JAHRES BACKTEST MIT SENTIMENT-FILTER (1H CHART) ===")
print(f"Startkapital: ${initial_balance:,.2f}")
print(f"Endkapital:   ${balance:,.2f}")
profit = balance - initial_balance
profit_pct = (profit / initial_balance) * 100
print(f"Net Profit:   ${profit:,.2f} ({profit_pct:+.2f}%)")

if trade_history:
    wins = [t for t in trade_history if t['pnl_pct'] > 0]
    losses = [t for t in trade_history if t['pnl_pct'] <= 0]
    win_rate = len(wins) / len(trade_history) * 100
    print(f"\n📈 TRADING STATS:")
    print(f"Total Trades: {len(trade_history)}")
    print(f"Win Rate:     {win_rate:.2f}% ({len(wins)} Gewinne, {len(losses)} Verluste)")
    avg_win = sum(t['pnl_pct'] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t['pnl_pct'] for t in losses) / len(losses) if losses else 0
    print(f"Avg Win:      +{avg_win:.2f}%")
    print(f"Avg Loss:     {avg_loss:.2f}%")
else:
    print("\nKeine Trades ausgeführt.")
