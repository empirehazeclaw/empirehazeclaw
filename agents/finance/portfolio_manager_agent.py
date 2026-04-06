#!/usr/bin/env python3
"""
Portfolio Manager Agent - Finance
Manages investment portfolios: allocation, rebalancing, performance tracking.
"""

import argparse
import json
import logging
import math
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
        logging.FileHandler(LOG_DIR / "portfolio_manager.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("PortfolioManager")


class AssetClass(Enum):
    CASH = "cash"
    BONDS = "bonds"
    STOCKS = "stocks"
    COMMODITIES = "commodities"
    REAL_ESTATE = "real_estate"
    CRYPTO = "crypto"
    ETFs = "etfs"
    OPTIONS = "options"
    FOREX = "forex"
    OTHER = "other"


class TransactionType(Enum):
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    INTEREST = "interest"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    FEE = "fee"
    TRANSFER = "transfer"


@dataclass
class Asset:
    asset_id: str
    symbol: str
    name: str
    asset_class: str
    quantity: float
    avg_cost: float
    current_price: float
    currency: str = "USD"
    last_updated: str = ""


@dataclass
class Transaction:
    tx_id: str
    portfolio_id: str
    symbol: str
    tx_type: str
    quantity: float
    price: float
    total: float
    fee: float
    date: str
    notes: str = ""


@dataclass
class AllocationTarget:
    asset_class: str
    target_pct: float
    min_pct: float = 0.0
    max_pct: float = 100.0


@dataclass
class Portfolio:
    portfolio_id: str
    name: str
    owner_id: str
    created_at: str
    currency: str
    assets: list = field(default_factory=list)
    transactions: list = field(default_factory=list)
    allocation_targets: list = field(default_factory=list)
    cash_balance: float = 0.0
    notes: list = field(default_factory=list)


class PortfolioManager:
    """Core portfolio management engine."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or (Path(__file__).parent / "data")
        self.data_dir.mkdir(exist_ok=True)
        self.portfolios_file = self.data_dir / "portfolios.json"
        self.portfolios: dict[str, Portfolio] = {}
        self._load()

    def _load(self):
        if self.portfolios_file.exists():
            try:
                raw = json.loads(self.portfolios_file.read_text())
                for pid, p in raw.items():
                    p["assets"] = [Asset(**a) for a in p.get("assets", [])]
                    p["transactions"] = [Transaction(**t) for t in p.get("transactions", [])]
                    p["allocation_targets"] = [AllocationTarget(**t) for t in p.get("allocation_targets", [])]
                    self.portfolios[pid] = Portfolio(**p)
                log.info(f"Loaded {len(self.portfolios)} portfolios.")
            except Exception as e:
                log.error(f"Failed to load portfolios: {e}")

    def _save(self):
        try:
            data = {}
            for pid, p in self.portfolios.items():
                d = p.__dict__.copy()
                d["assets"] = [a.__dict__ for a in p.assets]
                d["transactions"] = [t.__dict__ for t in p.transactions]
                d["allocation_targets"] = [t.__dict__ for t in p.allocation_targets]
                data[pid] = d
            self.portfolios_file.write_text(json.dumps(data, indent=2, default=str))
        except Exception as e:
            log.error(f"Failed to save portfolios: {e}")

    def _asset_value(self, asset: Asset) -> float:
        return asset.quantity * asset.current_price

    def _total_value(self, portfolio: Portfolio) -> float:
        return portfolio.cash_balance + sum(self._asset_value(a) for a in portfolio.assets)

    def _class_value(self, portfolio: Portfolio, asset_class: str) -> float:
        return sum(self._asset_value(a) for a in portfolio.assets if a.asset_class == asset_class)

    def create_portfolio(
        self,
        name: str,
        owner_id: str,
        currency: str = "USD",
        initial_cash: float = 0.0,
        allocation_targets: Optional[list[AllocationTarget]] = None,
    ) -> Portfolio:
        portfolio_id = f"PF-{uuid.uuid4().hex[:8].upper()}"
        portfolio = Portfolio(
            portfolio_id=portfolio_id,
            name=name,
            owner_id=owner_id,
            created_at=datetime.now().isoformat(),
            currency=currency,
            cash_balance=initial_cash,
            allocation_targets=allocation_targets or [],
        )
        self.portfolios[portfolio_id] = portfolio
        self._save()
        log.info(f"Created portfolio {portfolio_id}: {name}")
        return portfolio

    def add_asset(
        self,
        portfolio_id: str,
        symbol: str,
        name: str,
        asset_class: str,
        quantity: float,
        avg_cost: float,
        current_price: float,
        currency: str = "USD",
    ) -> Optional[Asset]:
        portfolio = self.portfolios.get(portfolio_id)
        if not portfolio:
            return None
        for a in portfolio.assets:
            if a.symbol == symbol:
                # Update existing position (average in)
                total_cost = a.avg_cost * a.quantity + avg_cost * quantity
                new_qty = a.quantity + quantity
                a.avg_cost = round(total_cost / new_qty, 4) if new_qty > 0 else 0
                a.quantity = new_qty
                a.current_price = current_price
                a.last_updated = datetime.now().isoformat()
                self._save()
                log.info(f"Updated position {symbol} in portfolio {portfolio_id}")
                return a

        asset = Asset(
            asset_id=f"AST-{uuid.uuid4().hex[:6].upper()}",
            symbol=symbol,
            name=name,
            asset_class=asset_class,
            quantity=quantity,
            avg_cost=avg_cost,
            current_price=current_price,
            currency=currency,
            last_updated=datetime.now().isoformat(),
        )
        portfolio.assets.append(asset)
        self._save()
        log.info(f"Added {quantity} {symbol} to portfolio {portfolio_id}")
        return asset

    def update_prices(self, portfolio_id: str, prices: dict[str, float]) -> bool:
        portfolio = self.portfolios.get(portfolio_id)
        if not portfolio:
            return False
        for asset in portfolio.assets:
            if asset.symbol in prices:
                asset.current_price = prices[asset.symbol]
                asset.last_updated = datetime.now().isoformat()
        self._save()
        log.info(f"Updated prices for {len(prices)} assets in {portfolio_id}")
        return True

    def buy_asset(
        self,
        portfolio_id: str,
        symbol: str,
        quantity: float,
        price: float,
        fee: float = 0.0,
        notes: str = "",
    ) -> Optional[Transaction]:
        portfolio = self.portfolios.get(portfolio_id)
        if not portfolio:
            return None
        total_cost = quantity * price + fee
        if total_cost > portfolio.cash_balance:
            log.warning(f"Insufficient cash in portfolio {portfolio_id}: need €{total_cost:,.2f}, have €{portfolio.cash_balance:,.2f}")
            return None

        portfolio.cash_balance -= total_cost

        tx = Transaction(
            tx_id=f"TX-{uuid.uuid4().hex[:8].upper()}",
            portfolio_id=portfolio_id,
            symbol=symbol,
            tx_type=TransactionType.BUY.value,
            quantity=quantity,
            price=price,
            total=total_cost,
            fee=fee,
            date=datetime.now().isoformat(),
            notes=notes,
        )
        portfolio.transactions.append(tx)
        self._save()
        log.info(f"BUY {quantity} {symbol} @ €{price:,.2f} in {portfolio_id}")
        return tx

    def sell_asset(
        self,
        portfolio_id: str,
        symbol: str,
        quantity: float,
        price: float,
        fee: float = 0.0,
        notes: str = "",
    ) -> Optional[Transaction]:
        portfolio = self.portfolios.get(portfolio_id)
        if not portfolio:
            return None
        for asset in portfolio.assets:
            if asset.symbol == symbol:
                if quantity > asset.quantity:
                    log.warning(f"Insufficient {symbol} in portfolio {portfolio_id}")
                    return None
                asset.quantity -= quantity
                if asset.quantity <= 0:
                    portfolio.assets.remove(asset)

        proceeds = quantity * price - fee
        portfolio.cash_balance += proceeds

        tx = Transaction(
            tx_id=f"TX-{uuid.uuid4().hex[:8].upper()}",
            portfolio_id=portfolio_id,
            symbol=symbol,
            tx_type=TransactionType.SELL.value,
            quantity=quantity,
            price=price,
            total=proceeds,
            fee=fee,
            date=datetime.now().isoformat(),
            notes=notes,
        )
        portfolio.transactions.append(tx)
        self._save()
        log.info(f"SELL {quantity} {symbol} @ €{price:,.2f} in {portfolio_id}")
        return tx

    def deposit_cash(self, portfolio_id: str, amount: float, notes: str = "") -> bool:
        portfolio = self.portfolios.get(portfolio_id)
        if not portfolio:
            return False
        portfolio.cash_balance += amount
        tx = Transaction(
            tx_id=f"TX-{uuid.uuid4().hex[:8].upper()}",
            portfolio_id=portfolio_id,
            symbol="CASH",
            tx_type=TransactionType.DEPOSIT.value,
            quantity=1,
            price=amount,
            total=amount,
            fee=0.0,
            date=datetime.now().isoformat(),
            notes=notes,
        )
        portfolio.transactions.append(tx)
        self._save()
        log.info(f"Deposited €{amount:,.2f} to portfolio {portfolio_id}")
        return True

    def withdraw_cash(self, portfolio_id: str, amount: float, notes: str = "") -> bool:
        portfolio = self.portfolios.get(portfolio_id)
        if not portfolio or amount > portfolio.cash_balance:
            return False
        portfolio.cash_balance -= amount
        tx = Transaction(
            tx_id=f"TX-{uuid.uuid4().hex[:8].upper()}",
            portfolio_id=portfolio_id,
            symbol="CASH",
            tx_type=TransactionType.WITHDRAWAL.value,
            quantity=1,
            price=amount,
            total=-amount,
            fee=0.0,
            date=datetime.now().isoformat(),
            notes=notes,
        )
        portfolio.transactions.append(tx)
        self._save()
        log.info(f"Withdrew €{amount:,.2f} from portfolio {portfolio_id}")
        return True

    def get_allocation(self, portfolio_id: str) -> list[dict]:
        portfolio = self.portfolios.get(portfolio_id)
        if not portfolio:
            return []
        total = self._total_value(portfolio)
        if total == 0:
            return []

        allocations = []
        class_values: dict[str, float] = {}
        for a in portfolio.assets:
            class_values[a.asset_class] = class_values.get(a.asset_class, 0.0) + self._asset_value(a)
        class_values["cash"] = portfolio.cash_balance

        for cls, val in class_values.items():
            pct = (val / total) * 100 if total > 0 else 0.0
            target = next((t.target_pct for t in portfolio.allocation_targets if t.asset_class == cls), None)
            drift = pct - target if target is not None else None
            allocations.append({
                "asset_class": cls,
                "value": round(val, 2),
                "percentage": round(pct, 2),
                "target_pct": target,
                "drift_pct": round(drift, 2) if drift is not None else None,
            })
        return sorted(allocations, key=lambda x: x["percentage"], reverse=True)

    def get_performance(self, portfolio_id: str) -> dict:
        portfolio = self.portfolios.get(portfolio_id)
        if not portfolio:
            return {}

        total_value = self._total_value(portfolio)
        total_cost = portfolio.cash_balance + sum(a.avg_cost * a.quantity for a in portfolio.assets)
        total_gain = total_value - total_cost
        total_return_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0.0

        # Unrealized P&L per asset
        unrealized = []
        for a in portfolio.assets:
            cost_basis = a.avg_cost * a.quantity
            market_val = a.current_price * a.quantity
            gain = market_val - cost_basis
            gain_pct = (gain / cost_basis * 100) if cost_basis > 0 else 0.0
            unrealized.append({
                "symbol": a.symbol,
                "quantity": a.quantity,
                "avg_cost": a.avg_cost,
                "current_price": a.current_price,
                "cost_basis": round(cost_basis, 2),
                "market_value": round(market_val, 2),
                "gain_loss": round(gain, 2),
                "gain_loss_pct": round(gain_pct, 2),
            })

        return {
            "portfolio_id": portfolio_id,
            "total_value": round(total_value, 2),
            "total_cost_basis": round(total_cost, 2),
            "total_gain_loss": round(total_gain, 2),
            "total_return_pct": round(total_return_pct, 2),
            "cash_balance": round(portfolio.cash_balance, 2),
            "unrealized_positions": unrealized,
        }

    def rebalance_suggestions(self, portfolio_id: str) -> list[dict]:
        portfolio = self.portfolios.get(portfolio_id)
        if not portfolio or not portfolio.allocation_targets:
            return []
        suggestions = []
        total = self._total_value(portfolio)
        allocations = self.get_allocation(portfolio_id)

        for target in portfolio.allocation_targets:
            current = next((a["percentage"] for a in allocations if a["asset_class"] == target.asset_class), 0.0)
            drift = current - target.target_pct
            abs_drift = abs(drift)

            if abs_drift > target.max_pct - target.target_pct + 5.0:
                current_val = (current / 100) * total if current > 0 else 0
                target_val = (target.target_pct / 100) * total
                diff_val = target_val - current_val
                action = "BUY" if diff_val > 0 else "SELL"
                suggestions.append({
                    "asset_class": target.asset_class,
                    "current_pct": round(current, 2),
                    "target_pct": target.target_pct,
                    "drift_pct": round(drift, 2),
                    "action": action,
                    "amount_eur": round(abs(diff_val), 2),
                    "priority": "HIGH" if abs_drift > 15 else "MEDIUM" if abs_drift > 8 else "LOW",
                })
        return suggestions

    def get_portfolio(self, portfolio_id: str) -> Optional[Portfolio]:
        return self.portfolios.get(portfolio_id)

    def list_portfolios(self, owner_id: Optional[str] = None) -> list[Portfolio]:
        results = list(self.portfolios.values())
        if owner_id:
            results = [p for p in results if p.owner_id == owner_id]
        return sorted(results, key=lambda p: p.created_at, reverse=True)


def _portfolio_to_dict(p: Portfolio) -> dict:
    d = p.__dict__.copy()
    d["assets"] = [a.__dict__ for a in p.assets]
    d["transactions"] = [t.__dict__ for t in p.transactions]
    d["allocation_targets"] = [t.__dict__ for t in p.allocation_targets]
    return d


def main():
    parser = argparse.ArgumentParser(
        prog="portfolio-manager",
        description="Finance Portfolio Manager - allocate, trade, rebalance, track performance.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create", help="Create a new portfolio")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--owner-id", required=True)
    p_create.add_argument("--currency", default="USD")
    p_create.add_argument("--initial-cash", type=float, default=0.0)

    p_add = sub.add_parser("add-asset", help="Add or update an asset in a portfolio")
    p_add.add_argument("--portfolio-id", required=True)
    p_add.add_argument("--symbol", required=True)
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--class", dest="asset_class", required=True)
    p_add.add_argument("--quantity", type=float, required=True)
    p_add.add_argument("--avg-cost", type=float, required=True)
    p_add.add_argument("--current-price", type=float, required=True)

    p_prices = sub.add_parser("update-prices", help="Update asset prices")
    p_prices.add_argument("--portfolio-id", required=True)
    p_prices.add_argument("--prices", required=True, help="JSON dict: {'AAPL': 150.0, 'BTC': 50000}")

    p_buy = sub.add_parser("buy", help="Buy an asset")
    p_buy.add_argument("--portfolio-id", required=True)
    p_buy.add_argument("--symbol", required=True)
    p_buy.add_argument("--quantity", type=float, required=True)
    p_buy.add_argument("--price", type=float, required=True)
    p_buy.add_argument("--fee", type=float, default=0.0)

    p_sell = sub.add_parser("sell", help="Sell an asset")
    p_sell.add_argument("--portfolio-id", required=True)
    p_sell.add_argument("--symbol", required=True)
    p_sell.add_argument("--quantity", type=float, required=True)
    p_sell.add_argument("--price", type=float, required=True)
    p_sell.add_argument("--fee", type=float, default=0.0)

    p_deposit = sub.add_parser("deposit", help="Deposit cash")
    p_deposit.add_argument("--portfolio-id", required=True)
    p_deposit.add_argument("--amount", type=float, required=True)

    p_withdraw = sub.add_parser("withdraw", help="Withdraw cash")
    p_withdraw.add_argument("--portfolio-id", required=True)
    p_withdraw.add_argument("--amount", type=float, required=True)

    p_alloc = sub.add_parser("allocation", help="Show allocation breakdown")
    p_alloc.add_argument("--portfolio-id", required=True)

    p_perf = sub.add_parser("performance", help="Show portfolio performance")
    p_perf.add_argument("--portfolio-id", required=True)

    p_rebalance = sub.add_parser("rebalance", help="Get rebalancing suggestions")
    p_rebalance.add_argument("--portfolio-id", required=True)

    p_get = sub.add_parser("get", help="Get portfolio details")
    p_get.add_argument("--portfolio-id", required=True)

    p_list = sub.add_parser("list", help="List all portfolios")
    p_list.add_argument("--owner-id")

    args = parser.parse_args()
    mgr = PortfolioManager()

    if args.cmd == "create":
        p = mgr.create_portfolio(args.name, args.owner_id, args.currency, args.initial_cash)
        print(json.dumps(_portfolio_to_dict(p), indent=2, default=str))

    elif args.cmd == "add-asset":
        a = mgr.add_asset(args.portfolio_id, args.symbol, args.name, args.asset_class,
                          args.quantity, args.avg_cost, args.current_price)
        if a:
            print(json.dumps(a.__dict__, indent=2, default=str))
        else:
            print(f"Portfolio {args.portfolio_id} not found.", file=sys.stderr)
            sys.exit(1)

    elif args.cmd == "update-prices":
        prices = json.loads(args.prices)
        ok = mgr.update_prices(args.portfolio_id, prices)
        print(f"Prices updated: {ok}")

    elif args.cmd == "buy":
        tx = mgr.buy_asset(args.portfolio_id, args.symbol, args.quantity, args.price, args.fee)
        if tx:
            print(json.dumps(tx.__dict__, indent=2, default=str))
        else:
            print("Buy failed. Check cash balance.", file=sys.stderr)
            sys.exit(1)

    elif args.cmd == "sell":
        tx = mgr.sell_asset(args.portfolio_id, args.symbol, args.quantity, args.price, args.fee)
        if tx:
            print(json.dumps(tx.__dict__, indent=2, default=str))
        else:
            print("Sell failed. Check position size.", file=sys.stderr)
            sys.exit(1)

    elif args.cmd == "deposit":
        ok = mgr.deposit_cash(args.portfolio_id, args.amount)
        print(f"Deposited: {ok}")

    elif args.cmd == "withdraw":
        ok = mgr.withdraw_cash(args.portfolio_id, args.amount)
        print(f"Withdrawn: {ok}")

    elif args.cmd == "allocation":
        alloc = mgr.get_allocation(args.portfolio_id)
        for a in alloc:
            target_str = f" → {a['target_pct']}%" if a["target_pct"] else ""
            drift_str = f" (drift {a['drift_pct']:+.1f}%)" if a["drift_pct"] is not None else ""
            print(f"  {a['asset_class']:15s} {a['percentage']:6.2f}%{target_str}{drift_str}  €{a['value']:>12,.2f}")

    elif args.cmd == "performance":
        perf = mgr.get_performance(args.portfolio_id)
        print(json.dumps(perf, indent=2, default=str))

    elif args.cmd == "rebalance":
        suggestions = mgr.rebalance_suggestions(args.portfolio_id)
        if not suggestions:
            print("Portfolio is within tolerance. No rebalancing needed.")
        for s in suggestions:
            print(f"  [{s['priority']}] {s['action']} €{s['amount_eur']:,.2f} of {s['asset_class']} "
                  f"(current {s['current_pct']}% → target {s['target_pct']}%, drift {s['drift_pct']:+.1f}%)")

    elif args.cmd == "get":
        p = mgr.get_portfolio(args.portfolio_id)
        if p:
            print(json.dumps(_portfolio_to_dict(p), indent=2, default=str))
        else:
            print(f"Portfolio {args.portfolio_id} not found.", file=sys.stderr)
            sys.exit(1)

    elif args.cmd == "list":
        portfolios = mgr.list_portfolios(args.owner_id)
        for p in portfolios:
            val = mgr._total_value(p)
            print(f"[{p.portfolio_id}] {p.name:30s} | {p.owner_id:15s} | €{val:>12,.2f}")


if __name__ == "__main__":
    main()
