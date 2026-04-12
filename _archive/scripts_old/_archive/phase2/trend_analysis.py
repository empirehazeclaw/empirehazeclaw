#!/usr/bin/env python3
"""
Sir HazeClaw Performance Trend Analysis
Analysiert Token-Trends und erstellt Reports.

Usage:
    python3 trend_analysis.py              # Show today's trends
    python3 trend_analysis.py --week       # Show weekly trends
    python3 trend_analysis.py --alert      # Check for anomalies
    python3 trend_analysis.py --report     # Generate report for Master
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
TOKEN_LOG = WORKSPACE / "data/token_log.json"
COORDINATOR_LOG = WORKSPACE / "data/learning_coordinator.json"
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"

ALERT_THRESHOLD = 0.20  # 20% increase triggers alert

def load_token_log():
    """Load token log."""
    if TOKEN_LOG.exists():
        with open(TOKEN_LOG) as f:
            return json.load(f)
    return {"entries": [], "total_tokens": 0}

def load_coordinator_log():
    """Load coordinator log with token usage."""
    if COORDINATOR_LOG.exists():
        with open(COORDINATOR_LOG) as f:
            return json.load(f)
    return {"token_usage": [], "runs": []}

def calculate_daily_tokens():
    """Calculate tokens per day."""
    log = load_coordinator_log()
    usage = log.get("token_usage", [])
    
    daily = {}
    for entry in usage:
        day = entry.get("timestamp", "")[:10]
        if day:
            daily[day] = daily.get(day, 0) + entry.get("total", 0)
    
    return daily

def calculate_trend(daily_data):
    """Calculate trend direction."""
    if len(daily_data) < 2:
        return "unknown", 0
    
    days = sorted(daily_data.keys())
    recent = daily_data[days[-1]] if days else 0
    previous = daily_data[days[-2]] if len(days) > 1 else recent
    
    if previous == 0:
        return "unknown", 0
    
    change_pct = (recent - previous) / previous * 100
    
    if change_pct > 10:
        return "increasing", change_pct
    elif change_pct < -10:
        return "decreasing", change_pct
    else:
        return "stable", change_pct

def show_today_trends():
    """Show today's token trends."""
    daily = calculate_daily_tokens()
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📊 **Token Trends — Today**")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    
    today_tokens = daily.get(today, 0)
    print(f"   **Today:** {today_tokens:,} tokens")
    
    # Calculate average
    if daily:
        avg = sum(daily.values()) / len(daily)
        print(f"   **Daily Avg:** {avg:,.0f} tokens")
    
    # Trend
    trend, change = calculate_trend(daily)
    direction = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
    print(f"   **Trend:** {direction} {abs(change):.1f}% vs yesterday")
    
    # Recent days
    print()
    print("   **Last 7 days:**")
    for day in sorted(daily.keys())[-7:]:
        tokens = daily[day]
        bar_len = min(tokens // 500, 40)
        print(f"     {day}: {'█' * bar_len} {tokens:,}")

def show_weekly_trends():
    """Show weekly token trends."""
    daily = calculate_daily_tokens()
    
    print("📊 **Token Trends — Last 7 Days**")
    print()
    
    week_ago = datetime.now() - timedelta(days=7)
    week_entries = [
        (day, tokens) for day, tokens in daily.items()
        if datetime.fromisoformat(day) > week_ago
    ]
    
    if not week_entries:
        print("   No data this week")
        return
    
    total = sum(t for _, t in week_entries)
    avg = total / len(week_entries) if week_entries else 0
    
    print(f"   **Week Total:** {total:,} tokens")
    print(f"   **Daily Avg:** {avg:,.0f} tokens")
    
    # Day by day
    print()
    print("   **Daily Breakdown:**")
    for day, tokens in sorted(week_entries):
        bar_len = min(tokens // 500, 40)
        print(f"     {day}: {'█' * bar_len} {tokens:,}")
    
    # Trend
    trend, change = calculate_trend(daily)
    direction = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
    print()
    print(f"   **Overall Trend:** {direction} {abs(change):.1f}%")

def check_anomalies():
    """Check for token usage anomalies."""
    daily = calculate_daily_tokens()
    trend, change = calculate_trend(daily)
    
    alerts = []
    
    # Check for significant increase
    if trend == "increasing" and change > ALERT_THRESHOLD * 100:
        alerts.append(f"Token usage UP {change:.1f}% vs yesterday")
    
    # Check for consecutive increases
    if len(daily) >= 3:
        days = sorted(daily.keys())
        if all(daily[days[i]] <= daily[days[i+1]] for i in range(len(days)-1)):
            alerts.append("Token usage increasing for 3+ consecutive days")
    
    return alerts

def generate_report():
    """Generate full report for Master."""
    daily = calculate_daily_tokens()
    trend, change = calculate_trend(daily)
    alerts = check_anomalies()
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_tokens = daily.get(today, 0)
    
    report = f"""
📊 **Performance Trend Report**
{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

**Today's Usage:**
- Tokens used: {today_tokens:,}
- Trend: {'📈 UP' if trend == 'increasing' else '📉 DOWN' if trend == 'decreasing' else '➡️ STABLE'} {abs(change):.1f}%

**Weekly Summary:**
"""
    # Add weekly total
    week_ago = datetime.now() - timedelta(days=7)
    week_total = sum(t for d, t in daily.items() if datetime.fromisoformat(d) > week_ago)
    report += f"- Week total: {week_total:,} tokens\n"
    
    if daily:
        avg = sum(daily.values()) / len(daily)
        report += f"- Daily average: {avg:,.0f} tokens\n"
    
    if alerts:
        report += f"\n**⚠️ Alerts:**\n"
        for alert in alerts:
            report += f"- {alert}\n"
    else:
        report += f"\n**✅ No anomalies detected**\n"
    
    return report

def main():
    if len(sys.argv) < 2:
        show_today_trends()
    elif sys.argv[1] == "--week":
        show_weekly_trends()
    elif sys.argv[1] == "--alert":
        alerts = check_anomalies()
        if alerts:
            print("⚠️ **Anomalies detected:**")
            for alert in alerts:
                print(f"  - {alert}")
        else:
            print("✅ No anomalies")
    elif sys.argv[1] == "--report":
        print(generate_report())
    elif sys.argv[1] == "--help":
        print(__doc__)
    else:
        print(__doc__)

if __name__ == "__main__":
    sys.exit(main())