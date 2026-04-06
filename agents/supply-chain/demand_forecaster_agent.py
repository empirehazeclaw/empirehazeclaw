#!/usr/bin/env python3
"""
Demand Forecaster Agent
=======================
Time-series demand forecasting with naive, moving-average, exponential
smoothing, and trend projection. Produces SKU-level forecasts, safety-stock
recommendations, and procurement alerts.

Usage:
    python3 demand_forecaster_agent.py --forecast SKU-001 --periods 12 --data data/sales_history.json
    python3 demand_forecaster_agent.py --simulate
    python3 demand_forecaster_agent.py --safety-stock
    python3 demand_forecaster_agent.py --report
"""

import argparse
import json
import logging
import math
import os
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("DemandForecaster")


# ── Data Models ───────────────────────────────────────────────────────────────
@dataclass
class SalesRecord:
    sku: str
    date: str          # YYYY-MM-DD
    quantity: int
    revenue: float = 0.0


@dataclass
class ForecastResult:
    sku: str
    method: str
    forecasts: list[dict]   # [{"period": "2026-04", "forecast": float, "lci": float, "uci": float}]
    mape: float             # Mean Absolute Percentage Error (%)
    mad: float              # Mean Absolute Deviation
    bias: float             # Forecast bias (systematic error)
    seasonal_factors: Optional[dict] = None
    trend_slope: Optional[float] = None


@dataclass
class SafetyStockResult:
    sku: str
    avg_demand: float
    std_demand: float
    lead_time_days: int
    service_level: float
    safety_stock: float
    reorder_point: float
    recommended_order_qty: float


# ── Data Store ────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "supply_chain")
SALES_FILE = os.path.join(DATA_DIR, "sales_history.json")
SKU_FILE = os.path.join(DATA_DIR, "sku_master.json")
FORECAST_FILE = os.path.join(DATA_DIR, "forecasts.json")


def load_json(path, default=None):
    if default is None:
        default = []
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            log.warning("Could not load %s: %s", path, e)
    return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ── Statistical Helpers ───────────────────────────────────────────────────────
def moving_average(series: list[float], window: int) -> list[Optional[float]]:
    result = []
    for i in range(len(series)):
        if i < window - 1:
            result.append(None)
        else:
            result.append(sum(series[i - window + 1:i + 1]) / window)
    return result


def exponential_smoothing(
    series: list[float], alpha: float = 0.3
) -> tuple[list[float], float]:
    """Simple exponential smoothing. Returns smoothed series and final level."""
    if not series:
        return [], 0.0
    smoothed = [series[0]]
    for i in range(1, len(series)):
        smoothed.append(alpha * series[i] + (1 - alpha) * smoothed[-1])
    return smoothed, smoothed[-1]


def holt_winters(
    series: list[float], alpha: float = 0.3, beta: float = 0.1,
    n_periods: int = 12
) -> tuple[list[float], float, float]:
    """
    Holt's linear trend method (no seasonality).
    Returns: (fitted_values, level, trend_slope)
    """
    if len(series) < 3:
        return series, series[-1] if series else 0.0, 0.0
    level = series[0]
    trend = (series[min(2, len(series)-1)] - series[0]) / min(2, len(series)-1)
    fitted = [level]
    for i in range(1, len(series)):
        prev_level = level
        level = alpha * series[i] + (1 - alpha) * (level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend
        fitted.append(level + trend)
    return fitted, level, trend


def seasonal_decomposition(series: list[float], period: int = 12):
    """
    Simple ratio-to-moving-average seasonal decomposition.
    Returns seasonal factors (multiplicative).
    """
    if len(series) < period * 2:
        return None
    n = len(series)
    ma = moving_average(series, period)
    ratios = []
    for i in range(n):
        if ma[i] and ma[i] > 0:
            ratios.append(series[i] / ma[i])
    if len(ratios) < period:
        return None
    seasonal = []
    for j in range(period):
        factors = [ratios[k] for k in range(j, len(ratios), period) if k < len(ratios)]
        seasonal.append(sum(factors) / len(factors) if factors else 1.0)
    s_sum = sum(seasonal)
    seasonal = [s / s_sum * period for s in seasonal]  # normalise
    return seasonal


def mape(actual: list[float], predicted: list[Optional[float]]) -> float:
    pairs = [(a, p) for a, p in zip(actual, predicted) if p is not None and p != 0]
    if not pairs:
        return 0.0
    return sum(abs(a - p) / a * 100 for a, p in pairs) / len(pairs)


def mad(actual: list[float], predicted: list[Optional[float]]) -> float:
    pairs = [(a, p) for a, p in zip(actual, predicted) if p is not None]
    if not pairs:
        return 0.0
    return sum(abs(a - p) for a, p in pairs) / len(pairs)


def bias(actual: list[float], predicted: list[Optional[float]]) -> float:
    pairs = [(a, p) for a, p in zip(actual, predicted) if p is not None]
    if not pairs:
        return 0.0
    return sum(p - a for a, p in pairs) / len(pairs)


# ── Core Logic ────────────────────────────────────────────────────────────────
class DemandForecaster:
    def __init__(self, service_level: float = 0.95):
        self.service_level = service_level
        self.sales_history: list[SalesRecord] = []
        self.sku_master: list[dict] = []
        self.forecasts: dict[str, dict] = {}

    # ── Data Loading ───────────────────────────────────────────────────────────
    def load_sales(self, path: Optional[str] = None):
        path = path or SALES_FILE
        raw = load_json(path, [])
        self.sales_history = [
            SalesRecord(**r) if isinstance(r, dict) else r for r in raw
        ]
        log.info("Loaded %d sales records", len(self.sales_history))

    def load_sku_master(self, path: Optional[str] = None):
        path = path or SKU_FILE
        self.sku_master = load_json(path, [])
        log.info("Loaded %d SKU master records", len(self.sku_master))

    def generate_sample_data(self):
        """Generate 2 years of monthly sales history for 6 SKUs."""
        import random
        random.seed(42)
        now = datetime.utcnow()
        skus = [
            ("SKU-101", "Widget-A", 200, 50, 12),   # base_demand, std, seasonality_period
            ("SKU-102", "Widget-B", 150, 30, 0),
            ("SKU-103", "Gadget-X", 500, 100, 6),
            ("SKU-104", "Part-Alpha", 80, 20, 0),
            ("SKU-105", "Assembly-Kit", 120, 40, 12),
            ("SKU-106", "Gizmo-Beta", 300, 80, 3),
        ]
        records = []
        base_date = now - timedelta(days=730)
        for sku_id, name, base, std, season_period in skus:
            for month in range(24):          # 24 months of history
                dt = base_date + timedelta(days=month * 30)
                # Trend: +0.5% per month
                trend_factor = 1 + 0.005 * month
                # Seasonal factor
                if season_period > 0:
                    seasonal = 1.0 + 0.3 * math.sin(2 * math.pi * month / season_period)
                else:
                    seasonal = 1.0
                qty = max(1, int(base * trend_factor * seasonal + random.gauss(0, std)))
                records.append(SalesRecord(
                    sku=sku_id,
                    date=dt.strftime("%Y-%m-01"),
                    quantity=qty,
                    revenue=round(qty * random.uniform(5, 50), 2),
                ))
        self.sales_history = records
        # SKU master
        self.sku_master = [
            {"sku": sku_id, "name": name,
             "lead_time_days": random.randint(7, 45),
             "reorder_interval_days": 30,
             "unit_cost": round(random.uniform(5, 100), 2)}
            for sku_id, name, *_ in skus
        ]
        log.info("Generated %d sample sales records", len(records))
        self._save_sales()
        self._save_sku_master()

    # ── Aggregation ───────────────────────────────────────────────────────────
    def get_monthly_series(self, sku: str) -> list[float]:
        """Aggregate daily sales into monthly totals for a SKU."""
        sku_records = [r for r in self.sales_history if r.sku == sku]
        if not sku_records:
            return []
        # Group by month
        by_month: dict[str, int] = {}
        for r in sku_records:
            month_key = r.date[:7]   # "YYYY-MM"
            by_month[month_key] = by_month.get(month_key, 0) + r.quantity
        sorted_months = sorted(by_month.items())
        return [v for _, v in sorted_months]

    # ── Forecasting Methods ───────────────────────────────────────────────────
    def forecast_naive(self, series: list[float], periods: int) -> list[float]:
        """Naive: repeat last value."""
        if not series:
            return [0.0] * periods
        return [series[-1]] * periods

    def forecast_ma(self, series: list[float], window: int, periods: int) -> list[float]:
        ma = moving_average(series, window)
        last_ma = [v for v in ma if v is not None]
        base = last_ma[-1] if last_ma else (sum(series) / len(series) if series else 0)
        return [base] * periods

    def forecast_ema(self, series: list[float], alpha: float,
                     periods: int) -> list[float]:
        _, level = exponential_smoothing(series, alpha)
        return [level] * periods

    def forecast_holt(self, series: list[float], alpha: float,
                       beta: float, periods: int):
        _, level, trend = holt_winters(series, alpha, beta)
        return [level + trend * (i + 1) for i in range(periods)]

    def forecast_ses_with_confidence(
        self, series: list[float], alpha: float, periods: int, confidence: float = 0.95
    ) -> tuple[list[dict], float, float]:
        """Forecast with confidence intervals using historical forecast errors."""
        smoothed, level = exponential_smoothing(series, alpha)
        # Compute standard error from residuals
        residuals = [
            series[i] - smoothed[i]
            for i in range(len(series)) if smoothed[i] is not None
        ]
        std_err = (sum(r * r for r in residuals) / max(1, len(residuals))) ** 0.5
        # Z-score for confidence level
        z = 1.96 if confidence >= 0.95 else 1.65 if confidence >= 0.90 else 1.28

        forecasts = []
        for i in range(periods):
            fc = level
            margin = z * std_err * math.sqrt(i + 1)
            forecasts.append({
                "forecast": round(fc, 2),
                "lci": round(max(0, fc - margin), 2),
                "uci": round(fc + margin, 2),
            })
        return forecasts, round(std_err, 2), level

    # ── Main Forecast ───────────────────────────────────────────────────────────
    def forecast(
        self,
        sku: str,
        periods: int = 12,
        method: str = "auto",
        alpha: float = 0.3,
        beta: float = 0.1,
    ) -> ForecastResult:
        series = self.get_monthly_series(sku)
        if not series:
            raise ValueError(f"No sales history for SKU {sku}")

        log.info("Forecasting %s (%d periods, method=%s)", sku, periods, method)

        if method == "naive":
            fc = self.forecast_naive(series, periods)
            forecasts = [{"forecast": round(v, 2), "lci": None, "uci": None} for v in fc]
            method_label = "Naive (last value)"
        elif method == "ma":
            window = min(3, len(series))
            fc = self.forecast_ma(series, window, periods)
            forecasts = [{"forecast": round(v, 2), "lci": None, "uci": None} for v in fc]
            method_label = f"MA-{window}"
        elif method == "ema":
            forecasts, std_err, level = self.forecast_ses_with_confidence(
                series, alpha, periods
            )
            method_label = f"EMA (α={alpha})"
        elif method == "holt":
            fc = self.forecast_holt(series, alpha, beta, periods)
            forecasts = [{"forecast": round(v, 2), "lci": None, "uci": None} for v in fc]
            method_label = f"Holt (α={alpha}, β={beta})"
        else:  # auto
            # Pick best by lowest MAPE on last 6 periods
            best_method = "ema"
            best_mape = float("inf")
            for m, label in [("naive", "Naive"), ("ma", "MA-3"), ("ema", f"EMA-{alpha}"),
                              ("holt", f"Holt-{alpha}-{beta}")]:
                fc_method = self.forecast
                series_copy = series.copy()
                # hold out last 6 periods
                if len(series_copy) > 6:
                    train = series_copy[:-6]
                    test = series_copy[-6:]
                else:
                    train = series_copy
                    test = series_copy
                if m == "naive":
                    pred = self.forecast_naive(train, len(test))
                elif m == "ma":
                    pred = self.forecast_ma(train, 3, len(test))
                elif m == "ema":
                    _, level_e = exponential_smoothing(train, alpha)
                    pred = [level_e] * len(test)
                else:
                    _, _, trend = holt_winters(train, alpha, beta)
                    pred = [level_e + trend * (i + 1) for i in range(len(test))]
                m_val = sum(abs(a - p) for a, p in zip(test, pred) if a != 0) / len(test) * 100 / max(sum(test) / len(test), 1)
                if m_val < best_mape:
                    best_mape = m_val
                    best_method = m
            method = best_method
            return self.forecast(sku, periods, method, alpha, beta)

        # Calculate accuracy metrics on fitted values (last n periods)
        fc_values = [f["forecast"] for f in forecasts]
        full_fc = fc_values + series[len(series) - len(fc_values):] if len(series) > len(fc_values) else series
        actual_slice = series[-len(fc_values):] if len(series) >= len(fc_values) else series

        result = ForecastResult(
            sku=sku,
            method=method_label,
            forecasts=forecasts,
            mape=mape(actual_slice, forecasts[:len(actual_slice)]["forecast"]
                       if len(forecasts) >= len(actual_slice) else [f["forecast"] for f in forecasts]),
            mad=mad(actual_slice, [f["forecast"] for f in forecasts[:len(actual_slice)]]),
            bias=0.0,
        )
        return result

    # ── Safety Stock ──────────────────────────────────────────────────────────
    def calculate_safety_stock(self, sku: str,
                                lead_time_days: Optional[int] = None,
                                service_level: Optional[float] = None
                                ) -> SafetyStockResult:
        series = self.get_monthly_series(sku)
        if not series:
            raise ValueError(f"No sales history for SKU {sku}")

        sl = service_level or self.service_level
        avg_demand = sum(series) / len(series)
        variance = sum((x - avg_demand) ** 2 for x in series) / max(1, len(series) - 1)
        std_demand = math.sqrt(variance)

        # Monthly → daily
        daily_avg = avg_demand / 30.0
        daily_std = std_demand / math.sqrt(30.0)

        lt = lead_time_days or 14
        # Safety stock using z-score for service level
        z = {0.90: 1.28, 0.95: 1.65, 0.97: 1.88, 0.99: 2.33}.get(sl, 1.65)
        ss = z * daily_std * math.sqrt(lt)
        rop = daily_avg * lt + ss  # reorder point

        return SafetyStockResult(
            sku=sku,
            avg_demand=round(avg_demand, 2),
            std_demand=round(std_demand, 2),
            lead_time_days=lt,
            service_level=sl,
            safety_stock=round(ss, 2),
            reorder_point=round(rop, 2),
            recommended_order_qty=round(rop * 1.5, 2),  # typical: 1.5×ROP
        )

    # ── Save / Report ─────────────────────────────────────────────────────────
    def _save_sales(self):
        save_json(SALES_FILE, [r.__dict__ for r in self.sales_history])

    def _save_sku_master(self):
        save_json(SKU_FILE, self.sku_master)

    def save_forecast(self, result: ForecastResult):
        data = load_json(FORECAST_FILE, {})
        data[result.sku] = {
            "method": result.method,
            "forecasts": result.forecasts,
            "mape": result.mape,
            "mad": result.mad,
            "saved_at": datetime.utcnow().isoformat(),
        }
        save_json(FORECAST_FILE, data)

    # ── Print Methods ──────────────────────────────────────────────────────────
    def print_forecast_table(self, result: ForecastResult, periods: int = 12):
        print(f"\n📈 DEMAND FORECAST — {result.sku} ───────────────────────────────────────────")
        print(f"  Method : {result.method}")
        print(f"  MAPE   : {result.mape:.2f}%")
        print(f"  MAD    : {result.mad:.2f}")
        print()
        print(f"  {'Period':<10} {'Forecast':>10} {'Lower 95%':>12} {'Upper 95%':>12}")
        print("  " + "-" * 46)
        now = datetime.utcnow()
        for i, fc in enumerate(result.forecasts[:periods]):
            period = (now + timedelta(days=30 * (i + 1))).strftime("%Y-%m")
            lci = str(fc.get("lci", "—") or "—")
            uci = str(fc.get("uci", "—") or "—")
            print(f"  {period:<10} {fc['forecast']:>10.1f} {lci:>12} {uci:>12}")
        print("  " + "-" * 46)

    def print_safety_stock(self, sku: Optional[str] = None):
        skus_to_check = [sku] if sku else [s["sku"] for s in self.sku_master]
        print(f"\n📦 SAFETY STOCK & REORDER ANALYSIS ───────────────────────────────────")
        print(f"  {'SKU':<12} {'Avg/Mo':>10} {'StdDev':>8} {'LT':>4} "
              f"{'Safety Stk':>12} {'ROP':>10} {'Order Qty':>11} {'SL':>5}")
        print("  " + "-" * 76)
        for s in skus_to_check:
            sku_info = next((k for k in self.sku_master if k["sku"] == s), None)
            lt = sku_info.get("lead_time_days", 14) if sku_info else 14
            try:
                ss = self.calculate_safety_stock(s, lead_time_days=lt)
                sl_str = f"{ss.service_level:.0%}"
                print(
                    f"  {ss.sku:<12} {ss.avg_demand:>10.1f} {ss.std_demand:>8.1f} "
                    f"{ss.lead_time_days:>4} {ss.safety_stock:>12.1f} "
                    f"{ss.reorder_point:>10.1f} {ss.recommended_order_qty:>11.1f} {sl_str:>5}"
                )
            except ValueError as e:
                log.warning("%s", e)

    def print_all_forecasts(self, periods: int = 12, methods_override: str = "auto"):
        print(f"\n{'='*70}")
        print(f"  DEMAND FORECAST SUMMARY — All SKUs ({periods} periods, method={methods_override})")
        print(f"{'='*70}")
        for sku_info in self.sku_master:
            sku = sku_info["sku"]
            try:
                result = self.forecast(sku, periods, methods_override)
                self.print_forecast_table(result, periods)
                self.save_forecast(result)
            except ValueError as e:
                log.warning("Skipping %s: %s", sku, e)


# ── CLI ───────────────────────────────────────────────────────────────────────
def build_parser():
    parser = argparse.ArgumentParser(
        prog="demand_forecaster_agent.py",
        description="Demand Forecaster — time-series forecasting, safety stock, reorder points.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --simulate                     Generate sample sales history
  %(prog)s --forecast SKU-101 --periods 12
  %(prog)s --forecast SKU-101 --method ema --alpha 0.4
  %(prog)s --forecast SKU-101 --method holt
  %(prog)s --safety-stock                All SKUs
  %(prog)s --report                       Full forecast summary for all SKUs
  %(prog)s --data data/sales.json         Load sales from file
        """,
    )
    parser.add_argument("--forecast", dest="sku",
                        help="SKU to forecast")
    parser.add_argument("--periods", type=int, default=12,
                        help="Number of periods to forecast (default: 12 months)")
    parser.add_argument("--method", dest="method",
                        choices=["auto", "naive", "ma", "ema", "holt"],
                        default="auto",
                        help="Forecasting method")
    parser.add_argument("--alpha", type=float, default=0.3,
                        help="EMA/Holt smoothing alpha (default: 0.3)")
    parser.add_argument("--beta", type=float, default=0.1,
                        help="Holt trend beta (default: 0.1)")
    parser.add_argument("--safety-stock", dest="safety_stock",
                        const="__all__", nargs="?",
                        help="Calculate safety stock (optionally for a specific SKU)")
    parser.add_argument("--service-level", type=float, dest="service_level",
                        default=0.95,
                        help="Service level for safety stock (default: 0.95)")
    parser.add_argument("--report", action="store_true",
                        help="Full forecast report for all SKUs")
    parser.add_argument("--simulate", action="store_true",
                        help="Generate sample sales history")
    parser.add_argument("--data", dest="data_file",
                        help="Path to sales history JSON")
    parser.add_argument("--sku-file", dest="sku_file",
                        help="Path to SKU master JSON")
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    fc = DemandForecaster(service_level=args.service_level)

    try:
        if args.simulate:
            fc.generate_sample_data()
        else:
            fc.load_sales(args.data_file)
            fc.load_sku_master(args.sku_file)

        if getattr(args, "sku", None):
            result = fc.forecast(
                args.sku, periods=args.periods,
                method=args.method, alpha=args.alpha, beta=args.beta
            )
            fc.print_forecast_table(result, args.periods)
            fc.save_forecast(result)
            print()
            fc.print_safety_stock(args.sku)
            return

        if args.safety_stock is not None:
            sku = None if args.safety_stock == "__all__" else args.safety_stock
            fc.print_safety_stock(sku)
            return

        if args.report:
            fc.print_all_forecasts(args.periods, args.method)
            return

        # Default help or summary
        parser.print_help()

    except KeyboardInterrupt:
        log.info("Interrupted.")
        sys.exit(130)
    except ValueError as e:
        log.error("%s", e)
        sys.exit(1)
    except Exception as e:
        log.exception("Fatal error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
