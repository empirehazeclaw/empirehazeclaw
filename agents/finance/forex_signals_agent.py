#!/usr/bin/env python3
"""
Forex Signals Agent - Finance
Generates and manages forex trading signals with multi-timeframe analysis,
currency strength indicators, and signal performance tracking.
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
        logging.FileHandler(LOG_DIR / "forex_signals.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("ForexSignals")


class SignalStrength(Enum):
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class SignalDirection(Enum):
    BUY = "buy"
    SELL = "sell"
    NEUTRAL = "neutral"


class TimeFrame(Enum):
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"
    W1 = "W1"


class TradeStatus(Enum):
    ACTIVE = "active"
    HIT_TP = "hit_tp"
    HIT_SL = "hit_sl"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


# Major forex pairs with base prices
FOREX_PAIRS = {
    "EUR/USD": 1.0850,
    "GBP/USD": 1.2650,
    "USD/JPY": 149.50,
    "USD/CHF": 0.8750,
    "AUD/USD": 0.6550,
    "USD/CAD": 1.3650,
    "NZD/USD": 0.6050,
    "EUR/GBP": 0.8580,
    "EUR/JPY": 162.20,
    "GBP/JPY": 189.10,
    "AUD/JPY": 97.90,
    "EUR/CHF": 0.9495,
    "EUR/AUD": 1.6570,
    "GBP/CHF": 1.1070,
    "AUD/NZD": 1.0830,
    "GBP/AUD": 1.9330,
    "EUR/CAD": 1.4820,
    "USD/SGD": 1.3420,
    "USD/HKD": 7.8150,
    "USD/MXN": 17.1500,
}

CURRENCIES = ["EUR", "GBP", "USD", "JPY", "CHF", "AUD", "CAD", "NZD", "SGD", "HKD", "MXN"]


@dataclass
class Candle:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class ForexSignal:
    signal_id: str
    pair: str
    direction: str
    entry_price: float
    stop_loss: float
    take_profit1: float
    take_profit2: float
    take_profit3: float
    risk_reward: float
    timeframe: str
    strength: str
    confidence: float
    created_at: str
    expires_at: str
    status: str
    pips_risk: float
    notes: str = ""
    closed_at: str = ""
    result_pips: float = 0.0


@dataclass
class CurrencyStrength:
    currency: str
    strength_score: float
    trend: str
    changed_at: str


class ForexSignalsEngine:
    """Forex signal generation and management engine."""

    PIP_DECIMAL_PLACES = {
        "JPY": 3,  # JPY pairs have 2 decimal pips (e.g. 0.01)
        "default": 4,
    }

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or (Path(__file__).parent / "data")
        self.data_dir.mkdir(exist_ok=True)
        self.signals_file = self.data_dir / "forex_signals.json"
        self.strength_file = self.data_dir / "currency_strength.json"
        self.signals: list[ForexSignal] = []
        self.currency_strength: dict[str, CurrencyStrength] = {}
        self._load()

    def _load(self):
        if self.signals_file.exists():
            try:
                data = json.loads(self.signals_file.read_text())
                self.signals.extend([ForexSignal(**s) for s in data])
                log.info(f"Loaded {len(self.signals)} forex signals.")
            except Exception as e:
                log.error(f"Failed to load signals: {e}")

        if self.strength_file.exists():
            try:
                data = json.loads(self.strength_file.read_text())
                self.currency_strength = {k: CurrencyStrength(**v) for k, v in data.items()}
            except Exception:
                pass

    def _save(self):
        try:
            self.signals_file.write_text(json.dumps([s.__dict__ for s in self.signals], indent=2, default=str))
            self.strength_file.write_text(json.dumps({k: v.__dict__ for k, v in self.currency_strength.items()}, indent=2))
        except Exception as e:
            log.error(f"Failed to save: {e}")

    def _get_pip_size(self, pair: str) -> float:
        quote = pair.split("/")[1]
        if pair in ("USD/JPY", "EUR/JPY", "GBP/JPY", "AUD/JPY"):
            return 0.01
        return 0.0001

    def _price_to_pips(self, pair: str, price_diff: float) -> float:
        return round(price_diff / self._get_pip_size(pair), 1)

    def _simulate_candles(self, pair: str, count: int = 100, timeframe: str = "H1") -> list[Candle]:
        """Generate simulated OHLC candles for a forex pair."""
        candles = []
        price = FOREX_PAIRS.get(pair, 1.0)
        now = datetime.now()

        minutes_map = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440, "W1": 10080}
        offset_minutes = minutes_map.get(timeframe, 60)

        for i in range(count):
            ts = (now - timedelta(minutes=offset_minutes * (count - i))).isoformat()
            volatility = 0.0003 if pair in ("USD/JPY", "EUR/JPY", "GBP/JPY") else 0.0002
            o = round(price * (1 + random.uniform(-volatility, volatility)), 5)
            c = round(price * (1 + random.uniform(-volatility * 1.5, volatility * 1.5)), 5)
            h = round(max(o, c) * (1 + random.uniform(0, volatility)), 5)
            l = round(min(o, c) * (1 - random.uniform(0, volatility)), 5)
            v = round(random.uniform(5000, 50000), 2)
            candles.append(Candle(timestamp=ts, open=o, high=h, low=l, close=c, volume=v))
            price = c
        return candles

    def calculate_rsi(self, candles: list[Candle], period: int = 14) -> float:
        if len(candles) < period + 1:
            return 50.0
        closes = [c.close for c in candles]
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d for d in deltas[-period:] if d > 0]
        losses = [-d for d in deltas[-period:] if d < 0]
        avg_gain = sum(gains) / period if gains else 0.0001
        avg_loss = sum(losses) / period if losses else 0.0001
        rs = avg_gain / avg_loss if avg_loss else 100
        return round(100 - (100 / (1 + rs)), 2)

    def calculate_sma(self, candles: list[Candle], period: int) -> float:
        if len(candles) < period:
            return candles[-1].close
        return sum(c.close for c in candles[-period:]) / period

    def calculate_ema(self, candles: list[Candle], period: int) -> float:
        if len(candles) < period:
            return candles[-1].close
        closes = [c.close for c in candles]
        sma = sum(closes[:period]) / period
        mult = 2 / (period + 1)
        ema = sma
        for price in closes[period:]:
            ema = (price - ema) * mult + ema
        return ema

    def calculate_atr(self, candles: list[Candle], period: int = 14) -> float:
        if len(candles) < period + 1:
            return 0.0005
        trs = []
        for i in range(1, len(candles)):
            tr = max(
                candles[i].high - candles[i].low,
                abs(candles[i].high - candles[i-1].close),
                abs(candles[i].low - candles[i-1].close),
            )
            trs.append(tr)
        return sum(trs[-period:]) / period

    def calculate_currency_strength(self) -> dict[str, CurrencyStrength]:
        """Calculate relative strength for each currency based on recent pairs."""
        currency_scores: dict[str, list[float]] = {c: [] for c in CURRENCIES}

        for pair, price in FOREX_PAIRS.items():
            if "/" not in pair:
                continue
            base, quote = pair.split("/")

            candles = self._simulate_candles(pair, 50, "H4")
            if len(candles) < 20:
                continue

            sma20 = self.calculate_sma(candles, 20)
            current = candles[-1].close
            deviation = (current - sma20) / sma20  # positive = uptrend

            if base in currency_scores:
                currency_scores[base].append(deviation * 100)
            if quote in currency_scores:
                currency_scores[quote].append(-deviation * 100)  # opposite for quote

        for currency, scores in currency_scores.items():
            if not scores:
                continue
            avg = sum(scores) / len(scores)
            score = max(-100, min(100, avg * 50 + 50))  # 0-100 scale
            trend = "STRONG" if score > 60 else "WEAK" if score < 40 else "NEUTRAL"
            self.currency_strength[currency] = CurrencyStrength(
                currency=currency,
                strength_score=round(score, 2),
                trend=trend,
                changed_at=datetime.now().isoformat(),
            )

        self._save()
        return self.currency_strength

    def analyze_pair(self, pair: str, timeframe: str = "H1") -> dict:
        """Multi-indicator analysis for a forex pair."""
        candles = self._simulate_candles(pair, 100, timeframe)
        current = candles[-1].close

        ema8 = self.calculate_ema(candles, 8)
        ema21 = self.calculate_ema(candles, 21)
        ema50 = self.calculate_ema(candles, 50)
        ema200 = self.calculate_ema(candles, 200)
        rsi = self.calculate_rsi(candles, 14)
        atr = self.calculate_atr(candles, 14)

        # Trend detection
        if ema8 > ema21 > ema50 > ema200:
            trend = "STRONG_UP"
        elif ema8 < ema21 < ema50 < ema200:
            trend = "STRONG_DOWN"
        elif ema8 > ema21:
            trend = "UP"
        elif ema8 < ema21:
            trend = "DOWN"
        else:
            trend = "NEUTRAL"

        # RSI analysis
        rsi_signal = "OVERBOUGHT" if rsi > 70 else "OVERSOLD" if rsi < 30 else "NEUTRAL"

        # Signal generation
        signal_strength = SignalStrength.MEDIUM.value
        confidence = 0.60
        direction = SignalDirection.NEUTRAL.value
        pip_size = self._get_pip_size(pair)

        if trend.startswith("UP") and rsi < 65:
            direction = SignalDirection.BUY.value
            confidence = 0.70
            signal_strength = SignalStrength.STRONG.value if trend == "STRONG_UP" else SignalStrength.MEDIUM.value
        elif trend.startswith("DOWN") and rsi > 35:
            direction = SignalDirection.SELL.value
            confidence = 0.70
            signal_strength = SignalStrength.STRONG.value if trend == "STRONG_DOWN" else SignalStrength.MEDIUM.value
        elif rsi_signal == "OVERSOLD" and ema8 > ema21:
            direction = SignalDirection.BUY.value
            confidence = 0.65
            signal_strength = SignalStrength.MEDIUM.value
        elif rsi_signal == "OVERBOUGHT" and ema8 < ema21:
            direction = SignalDirection.SELL.value
            confidence = 0.65
            signal_strength = SignalStrength.MEDIUM.value

        # Use currency strength to filter signals
        if pair.split("/")[0] in self.currency_strength:
            cs = self.currency_strength[pair.split("/")[0]]
            if direction == SignalDirection.BUY.value and cs.trend == "WEAK":
                confidence -= 0.10
            elif direction == SignalDirection.SELL.value and cs.trend == "STRONG":
                confidence -= 0.10

        # Levels
        recent_high = max(c.high for c in candles[-14:])
        recent_low = min(c.low for c in candles[-14:])
        atr_value = atr

        if direction == SignalDirection.BUY.value:
            entry = round(current + pip_size * 5, 5)
            sl = round(entry - atr_value * 1.5, 5)
            tp1 = round(entry + atr_value * 3, 5)
            tp2 = round(entry + atr_value * 5, 5)
            tp3 = round(entry + atr_value * 8, 5)
        elif direction == SignalDirection.SELL.value:
            entry = round(current - pip_size * 5, 5)
            sl = round(entry + atr_value * 1.5, 5)
            tp1 = round(entry - atr_value * 3, 5)
            tp2 = round(entry - atr_value * 5, 5)
            tp3 = round(entry - atr_value * 8, 5)
        else:
            entry = sl = tp1 = tp2 = tp3 = round(current, 5)

        risk_pips = self._price_to_pips(pair, abs(entry - sl))
        reward_pips = self._price_to_pips(pair, abs(tp2 - entry))
        rr = round(reward_pips / risk_pips, 1) if risk_pips > 0 else 0

        return {
            "pair": pair,
            "timeframe": timeframe,
            "current_price": current,
            "trend": trend,
            "rsi": rsi,
            "rsi_signal": rsi_signal,
            "ema8": round(ema8, 5),
            "ema21": round(ema21, 5),
            "ema50": round(ema50, 5),
            "ema200": round(ema200, 5),
            "atr": round(atr, 5),
            "direction": direction,
            "confidence": round(confidence, 2),
            "signal_strength": signal_strength,
            "entry_price": entry,
            "stop_loss": sl,
            "take_profit1": tp1,
            "take_profit2": tp2,
            "take_profit3": tp3,
            "risk_reward": rr,
            "pips_risk": risk_pips,
            "recent_high": recent_high,
            "recent_low": recent_low,
            "timestamp": datetime.now().isoformat(),
        }

    def generate_signal(self, pair: str, timeframe: str = "H1", ttl_hours: int = 24) -> Optional[ForexSignal]:
        analysis = self.analyze_pair(pair, timeframe)

        if analysis["direction"] == SignalDirection.NEUTRAL.value:
            log.info(f"No signal for {pair}: neutral market conditions")
            return None

        expires = (datetime.now() + timedelta(hours=ttl_hours)).isoformat()
        signal = ForexSignal(
            signal_id=f"FX-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            pair=pair,
            direction=analysis["direction"],
            entry_price=analysis["entry_price"],
            stop_loss=analysis["stop_loss"],
            take_profit1=analysis["take_profit1"],
            take_profit2=analysis["take_profit2"],
            take_profit3=analysis["take_profit3"],
            risk_reward=analysis["risk_reward"],
            timeframe=timeframe,
            strength=analysis["signal_strength"],
            confidence=analysis["confidence"],
            created_at=datetime.now().isoformat(),
            expires_at=expires,
            status=TradeStatus.ACTIVE.value,
            pips_risk=analysis["pips_risk"],
            notes=f"{analysis['trend']} | RSI {analysis['rsi']} | RR {analysis['risk_reward']}:1",
        )
        self.signals.append(signal)
        self._save()
        log.info(f"Generated {signal.direction.upper()} signal for {pair} @ {signal.entry_price} "
                 f"(SL: {signal.stop_loss}, TP2: {signal.take_profit2}, RR: {signal.risk_reward}:1)")
        return signal

    def scan_all_pairs(
        self,
        timeframes: Optional[list[str]] = None,
        min_confidence: float = 0.60,
        min_strength: str = "medium",
    ) -> list[ForexSignal]:
        """Scan all forex pairs and generate signals."""
        strength_order = {"weak": 0, "medium": 1, "strong": 2, "very_strong": 3}
        tf_map = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}
        timeframes = timeframes or ["H1", "H4", "D1"]

        self.calculate_currency_strength()
        signals: list[ForexSignal] = []

        for pair in FOREX_PAIRS:
            for tf in timeframes:
                analysis = self.analyze_pair(pair, tf)
                if analysis["direction"] == SignalDirection.NEUTRAL.value:
                    continue
                if analysis["confidence"] < min_confidence:
                    continue
                if strength_order.get(analysis["signal_strength"], 0) < strength_order.get(min_strength, 1):
                    continue
                sig = self.generate_signal(pair, tf)
                if sig:
                    signals.append(sig)

        # Sort by confidence descending
        signals.sort(key=lambda s: s.confidence, reverse=True)
        log.info(f"Scanned {len(FOREX_PAIRS)} pairs across {len(timeframes)} timeframes → {len(signals)} signals")
        return signals

    def simulate_signal_result(self, signal: ForexSignal) -> ForexSignal:
        """Simulate whether a signal hits SL or TP."""
        pip_size = self._get_pip_size(signal.pair)
        current = signal.entry_price

        # Simulate a random walk for price
        steps = random.randint(10, 100)
        direction = 1 if signal.direction == SignalDirection.BUY.value else -1

        tp_hit = sl_hit = False
        for _ in range(steps):
            move = random.gauss(0, pip_size * 2) * direction
            current += move

            if direction == 1:
                if current <= signal.stop_loss:
                    sl_hit = True
                    break
                if current >= signal.take_profit2:
                    tp_hit = True
                    break
            else:
                if current >= signal.stop_loss:
                    sl_hit = True
                    break
                if current <= signal.take_profit2:
                    tp_hit = True
                    break

        if tp_hit:
            signal.status = TradeStatus.HIT_TP.value
            signal.result_pips = signal.pips_risk * signal.risk_reward
        elif sl_hit:
            signal.status = TradeStatus.HIT_SL.value
            signal.result_pips = -signal.pips_risk
        else:
            signal.status = TradeStatus.EXPIRED.value
            signal.result_pips = 0.0

        signal.closed_at = datetime.now().isoformat()
        self._save()
        return signal

    def get_signal_performance(self, days: int = 30) -> dict:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        recent = [s for s in self.signals if s.created_at >= cutoff]

        total = len(recent)
        hit_tp = len([s for s in recent if s.status == TradeStatus.HIT_TP.value])
        hit_sl = len([s for s in recent if s.status == TradeStatus.HIT_SL.value])
        active = len([s for s in recent if s.status == TradeStatus.ACTIVE.value])
        expired = len([s for s in recent if s.status == TradeStatus.EXPIRED.value])

        total_pips = sum(s.result_pips for s in recent)
        win_rate = (hit_tp / (hit_tp + hit_sl) * 100) if (hit_tp + hit_sl) > 0 else 0.0

        by_pair: dict[str, dict] = {}
        for s in recent:
            if s.pair not in by_pair:
                by_pair[s.pair] = {"signals": 0, "pips": 0.0, "wins": 0, "losses": 0}
            by_pair[s.pair]["signals"] += 1
            by_pair[s.pair]["pips"] += s.result_pips
            if s.result_pips > 0:
                by_pair[s.pair]["wins"] += 1
            elif s.result_pips < 0:
                by_pair[s.pair]["losses"] += 1

        return {
            "period_days": days,
            "total_signals": total,
            "hit_tp": hit_tp,
            "hit_sl": hit_sl,
            "active": active,
            "expired": expired,
            "win_rate_pct": round(win_rate, 2),
            "total_pips": round(total_pips, 1),
            "avg_pips_per_signal": round(total_pips / total, 1) if total > 0 else 0.0,
            "by_pair": {k: {kk: round(vv, 1) if isinstance(vv, float) else vv for kk, vv in v.items()}
                        for k, v in by_pair.items()},
        }

    def list_signals(
        self,
        pair: Optional[str] = None,
        status: Optional[str] = None,
        direction: Optional[str] = None,
        limit: int = 50,
    ) -> list[ForexSignal]:
        results = list(self.signals)
        if pair:
            results = [s for s in results if s.pair == pair]
        if status:
            results = [s for s in results if s.status == status]
        if direction:
            results = [s for s in results if s.direction == direction]
        return sorted(results, key=lambda s: s.created_at, reverse=True)[:limit]


def main():
    parser = argparse.ArgumentParser(
        prog="forex-signals",
        description="Forex Signals Agent - multi-timeframe analysis, signal generation, performance tracking.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_analyze = sub.add_parser("analyze", help="Analyze a forex pair")
    p_analyze.add_argument("--pair", required=True)
    p_analyze.add_argument("--timeframe", default="H1",
                           choices=["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"])

    p_signal = sub.add_parser("signal", help="Generate a signal for a pair")
    p_signal.add_argument("--pair", required=True)
    p_signal.add_argument("--timeframe", default="H1")
    p_signal.add_argument("--ttl", type=int, default=24, help="Signal TTL in hours")

    p_scan = sub.add_parser("scan", help="Scan all pairs for signals")
    p_scan.add_argument("--timeframes", nargs="+", default=["H1", "H4"],
                        choices=["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"])
    p_scan.add_argument("--min-confidence", type=float, default=0.60)
    p_scan.add_argument("--min-strength", default="medium", choices=["weak", "medium", "strong", "very_strong"])

    p_simulate = sub.add_parser("simulate", help="Simulate result for a signal")
    p_simulate.add_argument("--signal-id", required=True)

    p_perf = sub.add_parser("performance", help="Show signal performance")
    p_perf.add_argument("--days", type=int, default=30)

    p_strength = sub.add_parser("strength", help="Show currency strength")

    p_list = sub.add_parser("list", help="List signals")
    p_list.add_argument("--pair")
    p_list.add_argument("--status")
    p_list.add_argument("--direction")
    p_list.add_argument("--limit", type=int, default=20)

    p_markets = sub.add_parser("markets", help="List available forex pairs")
    p_get = sub.add_parser("get", help="Get a specific signal")
    p_get.add_argument("--signal-id", required=True)

    args = parser.parse_args()
    engine = ForexSignalsEngine()

    if args.cmd == "analyze":
        result = engine.analyze_pair(args.pair, args.timeframe)
        print(json.dumps(result, indent=2, default=str))

    elif args.cmd == "signal":
        sig = engine.generate_signal(args.pair, args.timeframe, args.ttl)
        if sig:
            print(json.dumps(sig.__dict__, indent=2, default=str))
        else:
            print(f"No signal generated for {args.pair} (neutral conditions).")

    elif args.cmd == "scan":
        signals = engine.scan_all_pairs(args.timeframes, args.min_confidence, args.min_strength)
        if not signals:
            print("No signals found matching criteria.")
        for s in signals:
            print(f"  [{s.signal_id}] {s.direction.upper()} {s.pair} {s.timeframe:3s} "
                  f"@ {s.entry_price}  SL:{s.stop_loss}  TP2:{s.take_profit2}  "
                  f"RR:{s.risk_reward}:1  conf:{s.confidence:.0%}  {s.strength}")

    elif args.cmd == "simulate":
        sig = next((s for s in engine.signals if s.signal_id == args.signal_id), None)
        if not sig:
            print(f"Signal {args.signal_id} not found.", file=sys.stderr)
            sys.exit(1)
        result = engine.simulate_signal_result(sig)
        pips_str = f"+{result.result_pips:.1f}" if result.result_pips > 0 else f"{result.result_pips:.1f}"
        print(f"Signal {result.signal_id}: {result.status} → {pips_str} pips")

    elif args.cmd == "performance":
        perf = engine.get_signal_performance(args.days)
        print(json.dumps(perf, indent=2, default=str))

    elif args.cmd == "strength":
        strength = engine.calculate_currency_strength()
        sorted_currencies = sorted(strength.values(), key=lambda x: x.strength_score, reverse=True)
        print("Currency Strength (H4 timeframe):")
        for cs in sorted_currencies:
            bar_len = int(cs.strength_score / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            trend_icon = "📈" if cs.trend == "STRONG" else "📉" if cs.trend == "WEAK" else "➡️"
            print(f"  {cs.currency:4s} {bar} {cs.strength_score:5.2f}  {trend_icon} {cs.trend}")

    elif args.cmd == "list":
        signals = engine.list_signals(args.pair, args.status, args.direction, args.limit)
        if not signals:
            print("No signals found.")
        for s in signals:
            pips_str = f"+{s.result_pips:.1f}pips" if s.result_pips > 0 else f"{s.result_pips:.1f}pips"
            result_str = f" ({pips_str})" if s.status != "active" else ""
            print(f"  [{s.signal_id}] {s.direction.upper()} {s.pair:10s} {s.timeframe:3s} "
                  f"conf={s.confidence:.0%} {s.strength:12s} {s.status:10s}{result_str}")

    elif args.cmd == "markets":
        for pair, price in FOREX_PAIRS.items():
            print(f"  {pair:10s} {price:>10.5f}")

    elif args.cmd == "get":
        sig = next((s for s in engine.signals if s.signal_id == args.signal_id), None)
        if sig:
            print(json.dumps(sig.__dict__, indent=2, default=str))
        else:
            print(f"Signal {args.signal_id} not found.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
