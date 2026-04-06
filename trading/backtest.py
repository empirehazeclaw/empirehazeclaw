import ccxt
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta

print("🚀 Starte 2-Jahres Backtest (TA + Risk Management)...")

exchange = ccxt.binance()
coins = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
data = {}

# Hole 2 Jahre Daten (Tages-Kerzen = 730 Kerzen)
since = exchange.parse8601((datetime.now() - timedelta(days=730)).strftime('%Y-%m-%dT00:00:00Z'))

for symbol in coins:
    print(f"  Lade historische Daten für {symbol}...")
    ohlcv = exchange.fetch_ohlcv(symbol, '4h', since=since, limit=1000)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Indikatoren berechnen
    df.ta.rsi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    
    df.dropna(inplace=True)
    data[symbol] = df

# Backtest Setup
initial_balance = 10000.0
balance = initial_balance
positions = []
trade_history = []

# Nutze BTC-Zeitachse als Master
btc_dates = data['BTC/USDT']['timestamp'].tolist()

for current_date in btc_dates:
    # 1. RISK MANAGEMENT: Offene Trades prüfen
    for pos in positions[:]:
        symbol = pos['symbol']
        coin_df = data[symbol]
        row_series = coin_df[coin_df['timestamp'] == current_date]
        if row_series.empty: continue
        
        row = row_series.iloc[0]
        current_price = row['close']
        
        # Trailing Stop Logik
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
            trade_history.append({
                "symbol": symbol,
                "pnl_pct": pnl_pct,
                "reason": sell_reason
            })
            positions.remove(pos)

    # 2. EINSTIEGE: Scanne nach Signalen
    if len(positions) < 3: # Max 3 Trades
        for symbol in coins:
            if any(p['symbol'] == symbol for p in positions):
                continue
                
            coin_df = data[symbol]
            row_series = coin_df[coin_df['timestamp'] == current_date]
            if row_series.empty: continue
            
            row = row_series.iloc[0]
            rsi = row.get('RSI_14', 50)
            macd_hist = row.get('MACDh_12_26_9', 0)
            
            # Strategie: RSI unter 35 (leicht entspannt für Tageschart) & MACD dreht hoch
            if rsi < 35 and macd_hist > 0:
                trade_amount_usd = 1000.0 # $1000 pro Trade
                if balance >= trade_amount_usd:
                    balance -= trade_amount_usd
                    positions.append({
                        "symbol": symbol,
                        "entry_price": row['close'],
                        "highest_price": row['close'],
                        "amount": trade_amount_usd / row['close']
                    })

# Am Ende des Backtests offene Positionen schließen
for pos in positions:
    symbol = pos['symbol']
    last_price = data[symbol].iloc[-1]['close']
    revenue = pos['amount'] * last_price
    balance += revenue
    trade_history.append({
        "symbol": symbol,
        "pnl_pct": ((last_price - pos['entry_price']) / pos['entry_price']) * 100,
        "reason": "Backtest End"
    })

print("\n=== 📊 2-JAHRES BACKTEST ERGEBNISSE ===")
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
    
    reasons = {}
    for t in trade_history:
        reasons[t['reason']] = reasons.get(t['reason'], 0) + 1
    print(f"\n🛡️ EXIT GRÜNDE:")
    for r, c in reasons.items():
        print(f"- {r}: {c}x")
else:
    print("\nKeine Trades ausgeführt (Bedingungen wurden nie erfüllt).")
