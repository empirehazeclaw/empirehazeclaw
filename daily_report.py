#!/usr/bin/env python3
"""
📊 DAILY BUSINESS REPORT
====================
Generates reports based on SOUL.md principles
"""

import json
import fcntl
import sys
from datetime import datetime
from pathlib import Path

LOCK_FILE = "/home/clawbot/.openclaw/workspace/data/.daily_report.lock"

def acquire_lock():
    """Acquire exclusive file lock to prevent race conditions"""
    lock_path = Path(LOCK_FILE)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_fd = open(lock_path, 'w')
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        return lock_fd
    except BlockingIOError:
        print(f"[{datetime.now()}] Another instance is running. Exiting.")
        sys.exit(0)

def release_lock(lock_fd):
    """Release the file lock"""
    fcntl.flock(lock_fd, fcntl.LOCK_UN)
    lock_fd.close()

import os

def generate_report():
    report = []
    report.append("=" * 50)
    report.append(f"📊 BUSINESS REPORT - {datetime.now().strftime('%Y-%m-%d')}")
    report.append("=" * 50)
    
    # 1. Phase
    report.append("\n🎯 PHASE: Validation → First Customers")
    
    # 2. Revenue + Forecast
    try:
        from scripts.finance_tracker import get_summary
        s = get_summary()
        report.append(f"\n💰 FINANCE:")
        report.append(f"   Income: €{s['income']}")
        report.append(f"   Expenses: €{s['expenses']}")
        report.append(f"   Profit: €{s['profit']}")
    except:
        report.append("\n💰 FINANCE: No data")
    
    # 3. Revenue Forecast
    try:
        from scripts.revenue_forecaster import RevenueForecaster
        rf = RevenueForecaster()
        forecast = rf.save_forecast(days=30, forecast_days=30)
        report.append(f"\n🔮 REVENUE FORECAST (30 Days):")
        report.append(f"   Forecasted: €{forecast['forecast']['forecasted_revenue']:.2f}")
        report.append(f"   Confidence: {forecast['forecast']['confidence']}")
        report.append(f"   Est. Leads: {forecast['forecast']['estimated_leads']}")
        report.append(f"   Est. Conversions: {forecast['forecast']['estimated_conversions']}")
    except Exception as e:
        report.append(f"\n🔮 FORECAST: Error - {e}")
    
    # 3. Growth Metrics
    report.append("\n📈 GROWTH:")
    report.append("   Twitter: 88+ followers")
    report.append("   Outreach: 13+ emails sent")
    report.append("   Blog Posts: 57")
    
    # 4. Active Initiatives
    report.append("\n🚀 ACTIVE INITIATIVES:")
    report.append("   - Lead Generator SaaS (MVP)")
    report.append("   - Outreach Campaign")
    report.append("   - Twitter Growth")
    
    # 5. Next 3 Actions
    report.append("\n📋 NEXT 3 ACTIONS:")
    report.append("   1. Follow up on outreach responses")
    report.append("   2. Create more content")
    report.append("   3. Launch first paid product")
    
    # 6. Blockers
    report.append("\n⚠️ BLOCKERS:")
    report.append("   - Need first customers")
    
    report.append("\n" + "=" * 50)
    
    return "\n".join(report)

if __name__ == "__main__":
    lock_fd = acquire_lock()
    try:
        print(generate_report())
    finally:
        release_lock(lock_fd)
