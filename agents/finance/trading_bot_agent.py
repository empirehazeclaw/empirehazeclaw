#!/usr/bin/env python3
"""
Trading Bot Agent - Finance
Automated trading bot with strategy management, order execution simulation,
position tracking, and performance metrics.
"""

import argparse
import json
import logging
import math
import random
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "trading_bot.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("TradingBot")


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class StrategyType(Enum):
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    BREAKOUT = "breakout"
    DCA = "dollar_cost_averaging"
    GRID = "grid"
    SARAH = "sarah"


@dataclass
class OHLCV:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Order:
    order_id: str
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float
    stop_price: float = 0.0
    filled_quantity: float = 0.0
    avg_fill_price: float = 0.0
    status: str = OrderStatus.PENDING.value
    created_at: str = ""
    filled_at: str = ""
    strategy: str = ""
    notes: str = ""


@dataclass
class Position:
    symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    opened_at: str


@dataclass
class TradeSignal:
    signal_id: str
    timestamp: str
    symbol: str
    side: str
    price: float
    quantity: float
    strategy: str
    confidence: float
    stop_loss: float
    take_profit: float
    executed: bool = False


class TradingBot:
    """Automated trading bot engine."""

    # Simulated market data (seeded for reproducibility)
    SIM_MARKETS = {
        "EUR/USD": 1.0850,
        "GBP/USD": 1.2650,
        "BTC/USD": 43500.0,
        "ETH/USD": 2280.0,
        "AAPL": 178.50,
        "TSLA": 245.00,
        "GOOGL": 141.80,
        "NVDA": 495.20,
        "SPY": 478.50,
        "QQQ": 405.30,
    }

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or (Path(__file__).parent / "data")
        self.data_dir.mkdir(exist_ok=True)
        self.orders_file = self.data_dir / "orders.json"
        self.positions_file = self.data_dir / "positions.json"
        self.signals_file = self.data_dir / "signals.json"
        self.balance_file = self.data_dir / "balance.json"

        self.orders: dict[str, Order] = {}
        self.positions: dict[str, Position] = {}
        self.signals: list[TradeSignal] = []
        self.balance = 10000.0
        self.currency = "USD"
        self._load()

    def _load(self):
        for fname, container in [
            (self.orders_file, self.orders),
            (self.positions_file, self.positions),
            (self.signals_file, self.signals),
        ]:
            if fname.exists():
                try:
                    data = json.loads(fname.read_text())
                    if fname == self.signals_file:
                        container.extend([TradeSignal(**s) for s in data])
                    else:
                        container.update({k: (Position if fname == self.positions_file else Order)(**v)
                                         for k, v in data.items()})
                    log.info(f"Loaded {fname.name}: {len(data)} items.")
                except Exception as e:
                    log.error(f"Failed to load {fname.name}: {e}")

        bal_file = self.data_dir / "balance.json"
        if bal_file.exists():
            try:
                d = json.loads(bal_file.read_text())
                self.balance = d.get("balance", 10000.0)
                self.currency = d.get("currency", "USD")
            except Exception:
                pass

    def _save(self):
        def save_json(f, d):
            try:
                f.write(json.dumps(d, indent=2, default=str))
            except Exception as e:
                log.error(f"Failed to save {f.name}: {e}")

        save_json(self.orders_file, {k: v.__dict__ for k, v in self.orders.items()})
        save_json(self.positions_file, {k: v.__dict__ for k, v in self.positions.items()})
        save_json(self.signals_file, [s.__dict__ for s in self.signals])
        save_json(self.balance_file, {"balance": self.balance, "currency": self.currency})

    def _price(self, symbol: str) -> float:
        return self.SIM_MARKETS.get(symbol, 100.0)

    def _simulate_price_move(self, symbol: str) -> float:
        """Simulate a small price change."""
        base = self.SIM_MARKETS.get(symbol, 100.0)
        change_pct = random.uniform(-0.005, 0.005)
        new_price = round(base * (1 + change_pct), 4)
        self.SIM_MARKETS[symbol] = new_price
        return new_price

    def generate_market_data(self, symbol: str, periods: int = 100, interval: str = "1h") -> list[OHLCV]:
        """Generate simulated OHLCV data."""
        data = []
        price = self._price(symbol)
        now = datetime.now()

        for i in range(periods):
            ts = (now - timedelta(hours=periods - i)).isoformat()
            o = round(price * random.uniform(0.995, 1.005), 4)
            c = round(price * random.uniform(0.990, 1.010), 4)
            h = round(max(o, c) * random.uniform(1.000, 1.008), 4)
            l = round(min(o, c) * random.uniform(0.992, 1.000), 4)
            v = round(random.uniform(1000, 50000), 2)
            data.append(OHLCV(timestamp=ts, open=o, high=h, low=l, close=c, volume=v))
            price = c
        return data

    def analyze_market(self, symbol: str, strategy: str = "momentum") -> dict:
        """Technical analysis of market data."""
        data = self.generate_market_data(symbol, 50)
        closes = [d.close for d in data]
        highs = [d.high for d in data]
        lows = [d.low for d in data]

        # SMA
        sma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else sum(closes) / len(closes)
        sma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sma20

        # RSI (simplified)
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d for d in deltas[-14:] if d > 0]
        losses = [-d for d in deltas[-14:] if d < 0]
        avg_gain = sum(gains) / 14 if gains else 0.001
        avg_loss = sum(losses) / 14 if losses else 0.001
        rs = avg_gain / avg_loss if avg_loss else 100
        rsi = round(100 - (100 / (1 + rs)), 2)

        # Bollinger Bands
        recent = closes[-20:]
        mean = sum(recent) / len(recent)
        std = math.sqrt(sum((x - mean) ** 2 for x in recent) / len(recent))
        bb_upper = round(mean + 2 * std, 4)
        bb_lower = round(mean - 2 * std, 4)

        current = closes[-1]
        trend = "BULLISH" if sma20 > sma50 else "BEARISH"
        if abs(sma20 - sma50) / sma50 < 0.005:
            trend = "NEUTRAL"

        signal = "HOLD"
        confidence = 0.5

        if strategy == "momentum":
            if rsi < 30 and current < bb_lower:
                signal = "BUY"
                confidence = round(min(0.95, (30 - rsi) / 30 + 0.5), 2)
            elif rsi > 70 and current > bb_upper:
                signal = "SELL"
                confidence = round(min(0.95, (rsi - 70) / 30 + 0.5), 2)
            elif trend == "BULLISH" and rsi < 55:
                signal = "BUY"
                confidence = 0.65
            elif trend == "BEARISH" and rsi > 45:
                signal = "SELL"
                confidence = 0.65

        elif strategy == "mean_reversion":
            if current < bb_lower:
                signal = "BUY"
                confidence = round(min(0.9, (bb_lower - current) / bb_lower * 10), 2)
            elif current > bb_upper:
                signal = "SELL"
                confidence = round(min(0.9, (current - bb_upper) / bb_upper * 10), 2)

        elif strategy == "breakout":
            high_20 = max(highs[-20:])
            low_20 = min(lows[-20:])
            if current > high_20:
                signal = "BUY"
                confidence = 0.75
            elif current < low_20:
                signal = "SELL"
                confidence = 0.75

        atr = round(sum(h - l for h, l in zip(highs[-14:], lows[-14:])) / 14, 4)
        stop_loss = round(current - 1.5 * atr if signal == "BUY" else current + 1.5 * atr, 4)
        take_profit = round(current + 2 * atr if signal == "BUY" else current - 2 * atr, 4)

        return {
            "symbol": symbol,
            "strategy": strategy,
            "current_price": current,
            "sma20": round(sma20, 4),
            "sma50": round(sma50, 4),
            "rsi": rsi,
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "atr": atr,
            "trend": trend,
            "signal": signal,
            "confidence": confidence,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "timestamp": datetime.now().isoformat(),
        }

    def generate_signal(self, symbol: str, strategy: str = "momentum") -> TradeSignal:
        analysis = self.analyze_market(symbol, strategy)
        signal = TradeSignal(
            signal_id=f"SIG-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            side=analysis["signal"].lower(),
            price=analysis["current_price"],
            quantity=1.0,
            strategy=strategy,
            confidence=analysis["confidence"],
            stop_loss=analysis["stop_loss"],
            take_profit=analysis["take_profit"],
        )
        self.signals.append(signal)
        self._save()
        log.info(f"Generated {signal.side.upper()} signal for {symbol} @ {signal.price} (conf: {signal.confidence})")
        return signal

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str = OrderType.MARKET.value,
        quantity: float = 1.0,
        price: float = 0.0,
        stop_price: float = 0.0,
        strategy: str = "",
        simulate: bool = True,
    ) -> Optional[Order]:
        price = price or self._price(symbol)
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            created_at=datetime.now().isoformat(),
            status=OrderStatus.OPEN.value if order_type == OrderType.MARKET.value else OrderStatus.PENDING.value,
            strategy=strategy,
        )

        if simulate:
            if side == OrderSide.BUY.value:
                cost = quantity * price
                if cost > self.balance:
                    order.status = OrderStatus.REJECTED.value
                    log.warning(f"Order rejected: insufficient balance €{self.balance:,.2f} < €{cost:,.2f}")
                    self.orders[order_id] = order
                    self._save()
                    return order
                self.balance -= cost

                if symbol in self.positions:
                    pos = self.positions[symbol]
                    total_qty = pos.quantity + quantity
                    pos.avg_entry_price = round((pos.avg_entry_price * pos.quantity + price * quantity) / total_qty, 4)
                    pos.quantity = total_qty
                    pos.current_price = price
                    pos.unrealized_pnl = round((price - pos.avg_entry_price) * pos.quantity, 2)
                    pos.unrealized_pnl_pct = round((pos.unrealized_pnl / (pos.avg_entry_price * pos.quantity)) * 100, 2)
                else:
                    self.positions[symbol] = Position(
                        symbol=symbol,
                        quantity=quantity,
                        avg_entry_price=price,
                        current_price=price,
                        unrealized_pnl=0.0,
                        unrealized_pnl_pct=0.0,
                        opened_at=datetime.now().isoformat(),
                    )

                order.filled_quantity = quantity
                order.avg_fill_price = price
                order.status = OrderStatus.FILLED.value
                order.filled_at = datetime.now().isoformat()
                log.info(f"ORDER FILLED: BUY {quantity} {symbol} @ €{price:,.4f}")

            elif side == OrderSide.SELL.value:
                if symbol not in self.positions or self.positions[symbol].quantity < quantity:
                    order.status = OrderStatus.REJECTED.value
                    log.warning(f"Order rejected: insufficient position in {symbol}")
                    self.orders[order_id] = order
                    self._save()
                    return order

                self.balance += quantity * price
                pos = self.positions[symbol]
                pos.quantity -= quantity
                realized_pnl = round((price - pos.avg_entry_price) * quantity, 2)
                self.balance += realized_pnl

                if pos.quantity <= 0:
                    del self.positions[symbol]

                order.filled_quantity = quantity
                order.avg_fill_price = price
                order.status = OrderStatus.FILLED.value
                order.filled_at = datetime.now().isoformat()
                log.info(f"ORDER FILLED: SELL {quantity} {symbol} @ €{price:,.4f}, PnL: €{realized_pnl:,.2f}")

        self.orders[order_id] = order
        self._save()
        return order

    def execute_signal(self, signal: TradeSignal) -> Optional[Order]:
        if signal.executed:
            log.warning(f"Signal {signal.signal_id} already executed")
            return None
        order = self.place_order(
            symbol=signal.symbol,
            side=signal.side,
            quantity=signal.quantity,
            price=signal.price,
            strategy=signal.strategy,
            simulate=True,
        )
        if order and order.status == OrderStatus.FILLED.value:
            signal.executed = True
            self._save()
        return order

    def update_positions(self):
        """Update current prices and P&L for all positions."""
        for symbol, pos in self.positions.items():
            pos.current_price = self._price(symbol)
            pos.unrealized_pnl = round((pos.current_price - pos.avg_entry_price) * pos.quantity, 2)
            cost = pos.avg_entry_price * pos.quantity
            pos.unrealized_pnl_pct = round((pos.unrealized_pnl / cost) * 100, 2) if cost > 0 else 0.0
        self._save()

    def get_performance_summary(self) -> dict:
        self.update_positions()
        total_unrealized = sum(p.unrealized_pnl for p in self.positions.values())
        total_value = self.balance + sum(p.current_price * p.quantity for p in self.positions.values())

        winning_positions = [p for p in self.positions.values() if p.unrealized_pnl > 0]
        losing_positions = [p for p in self.positions.values() if p.unrealized_pnl <= 0]

        filled_orders = [o for o in self.orders.values() if o.status == OrderStatus.FILLED.value]
        buy_orders = [o for o in filled_orders if o.side == OrderSide.BUY.value]
        sell_orders = [o for o in filled_orders if o.side == OrderSide.SELL.value]

        return {
            "balance": round(self.balance, 2),
            "currency": self.currency,
            "total_value": round(total_value, 2),
            "total_unrealized_pnl": round(total_unrealized, 2),
            "open_positions": len(self.positions),
            "winning_positions": len(winning_positions),
            "losing_positions": len(losing_positions),
            "total_orders": len(self.orders),
            "filled_orders": len(filled_orders),
            "buy_orders": len(buy_orders),
            "sell_orders": len(sell_orders),
            "pending_orders": len([o for o in self.orders.values() if o.status == OrderStatus.OPEN.value]),
            "signals_generated": len(self.signals),
            "signals_executed": len([s for s in self.signals if s.executed]),
        }

    def run_strategy(
        self,
        symbols: list[str],
        strategy: str = "momentum",
        interval_seconds: int = 5,
        max_iterations: int = 3,
    ) -> list[dict]:
        """Run a trading strategy simulation for given symbols."""
        results = []
        for symbol in symbols:
            if symbol not in self.SIM_MARKETS:
                log.warning(f"Unknown symbol: {symbol}, skipping")
                continue

            log.info(f"Running {strategy} on {symbol}...")
            signal = self.generate_signal(symbol, strategy)
            analysis = self.analyze_market(symbol, strategy)

            if signal.side != "hold" and signal.confidence >= 0.60:
                order = self.execute_signal(signal)
                results.append({
                    "symbol": symbol,
                    "strategy": strategy,
                    "signal": signal.__dict__,
                    "analysis": analysis,
                    "order": order.__dict__ if order else None,
                    "balance_after": round(self.balance, 2),
                })
            else:
                results.append({
                    "symbol": symbol,
                    "strategy": strategy,
                    "signal": signal.__dict__,
                    "analysis": analysis,
                    "order": None,
                    "balance_after": round(self.balance, 2),
                })

        return results

    def cancel_order(self, order_id: str) -> bool:
        order = self.orders.get(order_id)
        if not order:
            return False
        if order.status in (OrderStatus.FILLED.value, OrderStatus.CANCELLED.value):
            return False
        order.status = OrderStatus.CANCELLED.value
        self._save()
        log.info(f"Cancelled order {order_id}")
        return True

    def get_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)

    def get_position(self, symbol: str) -> Optional[Position]:
        return self.positions.get(symbol)


def main():
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Finance Trading Bot - analyze markets, generate signals, execute orders.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_analyze = sub.add_parser("analyze", help="Analyze a market with technical indicators")
    p_analyze.add_argument("--symbol", required=True)
    p_analyze.add_argument("--strategy", default="momentum",
                           choices=["momentum", "mean_reversion", "breakout"])

    p_signal = sub.add_parser("signal", help="Generate a trade signal")
    p_signal.add_argument("--symbol", required=True)
    p_signal.add_argument("--strategy", default="momentum")

    p_order = sub.add_parser("order", help="Place an order")
    p_order.add_argument("--symbol", required=True)
    p_order.add_argument("--side", required=True, choices=["buy", "sell"])
    p_order.add_argument("--type", dest="order_type", default="market", choices=["market", "limit", "stop"])
    p_order.add_argument("--quantity", type=float, required=True)
    p_order.add_argument("--price", type=float, default=0.0)
    p_order.add_argument("--stop-price", type=float, default=0.0)

    p_cancel = sub.add_parser("cancel", help="Cancel an open order")
    p_cancel.add_argument("--order-id", required=True)

    p_run = sub.add_parser("run", help="Run strategy on symbols (simulation)")
    p_run.add_argument("--symbols", nargs="+", required=True)
    p_run.add_argument("--strategy", default="momentum")
    p_run.add_argument("--iterations", type=int, default=3)

    p_perf = sub.add_parser("performance", help="Show performance summary")
    p_positions = sub.add_parser("positions", help="Show open positions")
    p_orders = sub.add_parser("orders", help="Show all orders")
    p_signals = sub.add_parser("signals", help="Show trade signals")
    p_balance = sub.add_parser("balance", help="Show current balance")
    p_markets = sub.add_parser("markets", help="List available markets")

    args = parser.parse_args()
    bot = TradingBot()

    if args.cmd == "analyze":
        result = bot.analyze_market(args.symbol, args.strategy)
        print(json.dumps(result, indent=2, default=str))

    elif args.cmd == "signal":
        sig = bot.generate_signal(args.symbol, args.strategy)
        print(json.dumps(sig.__dict__, indent=2, default=str))

    elif args.cmd == "order":
        order = bot.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
        print(json.dumps(order.__dict__, indent=2, default=str))

    elif args.cmd == "cancel":
        ok = bot.cancel_order(args.order_id)
        print(f"Order cancelled: {ok}")

    elif args.cmd == "run":
        results = bot.run_strategy(args.symbols, args.strategy, max_iterations=args.iterations)
        for r in results:
            sig = r["signal"]
            order_str = f" → ORDER {r['order']['order_id']} FILLED" if r["order"] else " → NO ORDER (low confidence)"
            print(f"  {r['symbol']}: {sig['side'].upper()} @ €{sig['price']:,.4f} "
                  f"(conf {sig['confidence']:.0%}){order_str}")
        print(f"\nBalance after: €{bot.balance:,.2f}")

    elif args.cmd == "performance":
        perf = bot.get_performance_summary()
        print(json.dumps(perf, indent=2, default=str))

    elif args.cmd == "positions":
        bot.update_positions()
        if not bot.positions:
            print("No open positions.")
        for pos in bot.positions.values():
            pnl_str = f"+€{pos.unrealized_pnl:,.2f}" if pos.unrealized_pnl > 0 else f"€{pos.unrealized_pnl:,.2f}"
            print(f"  {pos.symbol:10s} qty={pos.quantity:8.4f}  entry=€{pos.avg_entry_price:>10.4f}  "
                  f"current=€{pos.current_price:>10.4f}  PnL={pnl_str} ({pos.unrealized_pnl_pct:+.2f}%)")

    elif args.cmd == "orders":
        if not bot.orders:
            print("No orders.")
        for order in sorted(bot.orders.values(), key=lambda o: o.created_at, reverse=True):
            print(f"  [{order.order_id}] {order.side.upper():4s} {order.symbol:10s} qty={order.quantity} "
                  f"@ €{order.price:>10.4f}  {order.status}")

    elif args.cmd == "signals":
        if not bot.signals:
            print("No signals.")
        for s in bot.signals[-20:]:
            exec_str = "✓ EXECUTED" if s.executed else "✗ PENDING"
            print(f"  [{s.signal_id}] {s.side.upper()} {s.symbol:10s} @ €{s.price:>10.4f} "
                  f"(conf {s.confidence:.0%}) {s.strategy:15s} {exec_str}")

    elif args.cmd == "balance":
        print(f"Balance: €{bot.balance:,.2f} {bot.currency}")

    elif args.cmd == "markets":
        for sym, price in bot.SIM_MARKETS.items():
            print(f"  {sym:12s} €{price:>12,.4f}")


if __name__ == "__main__":
    main()
