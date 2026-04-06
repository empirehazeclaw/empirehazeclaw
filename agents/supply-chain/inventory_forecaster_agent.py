#!/usr/bin/env python3
"""
Inventory Forecaster Agent
===========================
Forecast inventory needs based on historical data and trends.

Usage:
    python3 inventory_forecaster_agent.py --forecast --sku <sku> --days <days>
    python3 inventory_forecaster_agent.py --add-sale --sku <sku> --quantity <qty>
    python3 inventory_forecaster_agent.py --list-skus
    python3 inventory_forecaster_agent.py --report
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "inventory_forecaster.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Data paths
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/agents/supply-chain")
DATA_DIR.mkdir(parents=True, exist_ok=True)
INVENTORY_FILE = DATA_DIR / "inventory.json"
SALES_FILE = DATA_DIR / "sales_history.json"
FORECASTS_FILE = DATA_DIR / "forecasts.json"


def load_json(filepath: Path, default: dict = {}) -> dict:
    """Load JSON data from file."""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return default


def save_json(filepath: Path, data: dict) -> bool:
    """Save JSON data to file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def initialize_data():
    """Initialize data files if they don't exist."""
    if not INVENTORY_FILE.exists():
        save_json(INVENTORY_FILE, {
            "items": {
                "SKU-001": {
                    "name": "Widget A",
                    "current_stock": 150,
                    "min_stock": 50,
                    "max_stock": 500,
                    "lead_time_days": 7,
                    "reorder_point": 100,
                    "cost_per_unit": 12.50,
                    "category": "electronics"
                },
                "SKU-002": {
                    "name": "Gadget B",
                    "current_stock": 75,
                    "min_stock": 30,
                    "max_stock": 300,
                    "lead_time_days": 14,
                    "reorder_point": 60,
                    "cost_per_unit": 45.00,
                    "category": "electronics"
                },
                "SKU-003": {
                    "name": "Component C",
                    "current_stock": 200,
                    "min_stock": 100,
                    "max_stock": 1000,
                    "lead_time_days": 3,
                    "reorder_point": 150,
                    "cost_per_unit": 5.25,
                    "category": "components"
                }
            },
            "last_updated": datetime.now().isoformat()
        })
        logger.info("Initialized inventory data")
    
    if not SALES_FILE.exists():
        save_json(SALES_FILE, {"sales": []})
        logger.info("Initialized sales history")
    
    if not FORECASTS_FILE.exists():
        save_json(FORECASTS_FILE, {"forecasts": []})
        logger.info("Initialized forecasts")


def add_sale(sku: str, quantity: int, date: Optional[str] = None) -> bool:
    """Add a sale record."""
    inventory = load_json(INVENTORY_FILE)
    
    if sku not in inventory.get("items", {}):
        logger.error(f"SKU {sku} not found")
        return False
    
    sales = load_json(SALES_FILE)
    sale_date = date or datetime.now().isoformat()
    
    sale_record = {
        "sku": sku,
        "quantity": quantity,
        "date": sale_date,
        "timestamp": datetime.now().isoformat()
    }
    sales["sales"].append(sale_record)
    
    # Update current stock
    inventory["items"][sku]["current_stock"] = max(0, inventory["items"][sku]["current_stock"] - quantity)
    inventory["last_updated"] = datetime.now().isoformat()
    
    save_json(SALES_FILE, sales)
    save_json(INVENTORY_FILE, inventory)
    
    logger.info(f"Added sale: {quantity} units of {sku}")
    return True


def calculate_moving_average(sku: str, days: int = 30) -> float:
    """Calculate moving average sales rate."""
    sales = load_json(SALES_FILE)
    cutoff = datetime.now() - timedelta(days=days)
    
    total_sold = 0
    for sale in sales.get("sales", []):
        if sale["sku"] == sku:
            sale_date = datetime.fromisoformat(sale["date"].replace("Z", "+00:00"))
            if sale_date >= cutoff:
                total_sold += sale["quantity"]
    
    return total_sold / days if days > 0 else 0


def forecast_demand(sku: str, days: int = 30) -> dict:
    """Forecast demand for a SKU."""
    inventory = load_json(INVENTORY_FILE)
    
    if sku not in inventory.get("items", {}):
        raise ValueError(f"SKU {sku} not found")
    
    item = inventory["items"][sku]
    
    # Calculate average daily sales
    avg_daily_sales_7 = calculate_moving_average(sku, 7)
    avg_daily_sales_30 = calculate_moving_average(sku, 30)
    
    # Weighted average (recent sales weighted more)
    avg_daily_sales = (avg_daily_sales_7 * 0.4 + avg_daily_sales_30 * 0.6)
    
    # Calculate days until stockout
    current_stock = item["current_stock"]
    if avg_daily_sales > 0:
        days_until_stockout = current_stock / avg_daily_sales
    else:
        days_until_stockout = float('inf')
    
    # Calculate recommended order quantity
    lead_time_days = item["lead_time_days"]
    safety_stock = item["min_stock"]
    max_stock = item["max_stock"]
    
    # Forecast for lead time + buffer
    forecast_period = lead_time_days + 7  # 7 day buffer
    forecasted_demand = avg_daily_sales * forecast_period
    recommended_order = max(0, int(forecasted_demand + safety_stock - current_stock))
    recommended_order = min(recommended_order, max_stock - current_stock)
    
    # Determine status
    if days_until_stockout <= lead_time_days:
        status = "CRITICAL - Order immediately"
    elif days_until_stockout <= lead_time_days + 7:
        status = "LOW - Order soon"
    else:
        status = "OK - Stock sufficient"
    
    forecast = {
        "sku": sku,
        "item_name": item["name"],
        "current_stock": current_stock,
        "avg_daily_sales_7d": round(avg_daily_sales_7, 2),
        "avg_daily_sales_30d": round(avg_daily_sales_30, 2),
        "avg_daily_sales_weighted": round(avg_daily_sales, 2),
        "days_until_stockout": round(days_until_stockout, 1) if days_until_stockout != float('inf') else "N/A",
        "lead_time_days": lead_time_days,
        "recommended_order_quantity": recommended_order,
        "status": status,
        "forecast_date": datetime.now().isoformat(),
        "forecast_period_days": days
    }
    
    return forecast


def generate_forecast_report(days: int = 30) -> dict:
    """Generate forecast report for all SKUs."""
    inventory = load_json(INVENTORY_FILE)
    forecasts = []
    
    for sku, item in inventory.get("items", {}).items():
        try:
            forecast = forecast_demand(sku, days)
            forecasts.append(forecast)
        except Exception as e:
            logger.error(f"Error forecasting {sku}: {e}")
    
    # Sort by urgency
    forecasts.sort(key=lambda x: x.get("days_until_stockout", 999) if isinstance(x.get("days_until_stockout"), (int, float)) else 999)
    
    # Save forecasts
    save_json(FORECASTS_FILE, {"forecasts": forecasts, "generated": datetime.now().isoformat()})
    
    return {"forecasts": forecasts, "total_skus": len(forecasts)}


def list_skus() -> list:
    """List all SKUs."""
    inventory = load_json(INVENTORY_FILE)
    skus = []
    for sku, item in inventory.get("items", {}).items():
        skus.append({
            "sku": sku,
            "name": item["name"],
            "current_stock": item["current_stock"],
            "category": item.get("category", "unknown")
        })
    return skus


def display_forecast(forecast: dict):
    """Display a forecast nicely."""
    print("\n" + "=" * 60)
    print(f"📦 FORECAST: {forecast['sku']} - {forecast['item_name']}")
    print("=" * 60)
    print(f"  Current Stock:     {forecast['current_stock']} units")
    print(f"  Avg Daily Sales:   {forecast['avg_daily_sales_weighted']} units/day")
    print(f"  Days Until Stockout: {forecast['days_until_stockout']}")
    print(f"  Lead Time:         {forecast['lead_time_days']} days")
    print(f"  Recommended Order: {forecast['recommended_order_quantity']} units")
    print(f"  Status:            {forecast['status']}")
    print("=" * 60)


def display_report(report: dict):
    """Display a forecast report."""
    print("\n" + "=" * 70)
    print("📊 INVENTORY FORECAST REPORT")
    print("=" * 70)
    print(f"Total SKUs analyzed: {report['total_skus']}")
    print()
    
    critical = []
    low = []
    ok = []
    
    for f in report['forecasts']:
        if "CRITICAL" in f['status']:
            critical.append(f)
        elif "LOW" in f['status']:
            low.append(f)
        else:
            ok.append(f)
    
    if critical:
        print("🚨 CRITICAL ITEMS (Order Immediately):")
        for f in critical:
            print(f"   - {f['sku']}: {f['item_name']} | Stock: {f['current_stock']} | Days left: {f['days_until_stockout']} | Order: {f['recommended_order_quantity']}")
        print()
    
    if low:
        print("⚠️  LOW ITEMS (Order Soon):")
        for f in low:
            print(f"   - {f['sku']}: {f['item_name']} | Stock: {f['current_stock']} | Days left: {f['days_until_stockout']} | Order: {f['recommended_order_quantity']}")
        print()
    
    if ok:
        print("✅ OK ITEMS:")
        for f in ok:
            print(f"   - {f['sku']}: {f['item_name']} | Stock: {f['current_stock']} | Days left: {f['days_until_stockout']}")
    
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Inventory Forecaster Agent - Forecast inventory needs based on sales trends",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --forecast --sku SKU-001 --days 30
  %(prog)s --add-sale --sku SKU-001 --quantity 5
  %(prog)s --list-skus
  %(prog)s --report
  %(prog)s --init  # Initialize sample data
        """
    )
    
    parser.add_argument("--forecast", action="store_true", help="Generate forecast for a SKU")
    parser.add_argument("--sku", type=str, help="SKU to forecast")
    parser.add_argument("--days", type=int, default=30, help="Forecast period in days (default: 30)")
    parser.add_argument("--add-sale", action="store_true", help="Add a sale record")
    parser.add_argument("--quantity", type=int, help="Quantity sold")
    parser.add_argument("--date", type=str, help="Sale date (ISO format)")
    parser.add_argument("--list-skus", action="store_true", help="List all SKUs")
    parser.add_argument("--report", action="store_true", help="Generate full forecast report")
    parser.add_argument("--init", action="store_true", help="Initialize sample data")
    
    args = parser.parse_args()
    
    try:
        initialize_data()
        
        if args.init:
            print("✅ Sample data initialized")
            return
        
        if args.list_skus:
            skus = list_skus()
            print("\n📦 INVENTORY SKUs:")
            print("-" * 50)
            for sku in skus:
                print(f"  {sku['sku']}: {sku['name']} | Stock: {sku['current_stock']} | Category: {sku['category']}")
            print("-" * 50)
            return
        
        if args.add_sale:
            if not args.sku or args.quantity is None:
                parser.error("--add-sale requires --sku and --quantity")
            if add_sale(args.sku, args.quantity, args.date):
                print(f"✅ Sale recorded: {args.quantity} units of {args.sku}")
            else:
                print(f"❌ Failed to record sale")
                sys.exit(1)
            return
        
        if args.forecast:
            if not args.sku:
                parser.error("--forecast requires --sku")
            forecast = forecast_demand(args.sku, args.days)
            display_forecast(forecast)
            return
        
        if args.report:
            report = generate_forecast_report(args.days)
            display_report(report)
            return
        
        parser.print_help()
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
