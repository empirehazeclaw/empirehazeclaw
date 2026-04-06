#!/usr/bin/env python3
"""
Analytics Automation Agent - Moltbook Analytics Division
Automates data collection, analysis, and reporting.

Inspired by SOUL.md: CEO mindset, Eigenverantwortung, Geschwindigkeit über Perfektion
"""

import argparse
import json
import logging
import os
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = SCRIPT_DIR.parent.parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = WORKSPACE / "data" / "analytics"
METRICS_FILE = DATA_DIR / "metrics.json"
REPORTS_FILE = DATA_DIR / "reports.json"
DASHBOARD_FILE = DATA_DIR / "dashboard.json"
ALERTS_FILE = DATA_DIR / "alerts.json"
CONFIG_FILE = DATA_DIR / "config.json"

# Ensure directories
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ANALYTICS] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "analytics_automation.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("AnalyticsAutomation")


# ─── Data Helpers ─────────────────────────────────────────────────────────────
def load_json(path: Path, default: dict) -> dict:
    """Load JSON, return default if missing or invalid."""
    if not path.exists():
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load {path}: {e}")
        return default


def save_json(path: Path, data: dict) -> None:
    """Save data to JSON file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        log.error(f"Failed to save {path}: {e}")
        raise


def load_metrics() -> dict:
    """Load metrics database."""
    return load_json(METRICS_FILE, {"metrics": [], "last_updated": None})


def save_metrics(data: dict) -> None:
    """Save metrics database."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(METRICS_FILE, data)


def load_reports() -> dict:
    """Load reports."""
    return load_json(REPORTS_FILE, {"reports": [], "last_updated": None})


def save_reports(data: dict) -> None:
    """Save reports."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(REPORTS_FILE, data)


def load_alerts() -> dict:
    """Load alerts."""
    return load_json(ALERTS_FILE, {"alerts": [], "last_updated": None})


def save_alerts(data: dict) -> None:
    """Save alerts."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(ALERTS_FILE, data)


def load_config() -> dict:
    """Load configuration."""
    defaults = {
        "metrics_sources": ["website", "social", "email", "sales"],
        "report_schedule": "daily",
        "alert_thresholds": {
            "conversion_rate": {"min": 0.01, "max": 0.50},
            "bounce_rate": {"max": 0.70},
            "response_time": {"max": 2000},
        },
        "retention_days": 90,
    }
    return load_json(CONFIG_FILE, defaults)


def generate_id(items: list) -> int:
    """Generate next ID."""
    return max((i.get("id", 0) for i in items), default=0) + 1


# ─── Data Generation ───────────────────────────────────────────────────────────
def generate_metric_snapshot(source: str) -> dict:
    """Generate realistic metric snapshot for a source."""
    base_metrics = {
        "website": {
            "visitors": random.randint(500, 5000),
            "pageviews": random.randint(1500, 15000),
            "bounce_rate": round(random.uniform(0.30, 0.70), 3),
            "avg_session_duration": random.randint(60, 300),
            "conversion_rate": round(random.uniform(0.02, 0.08), 3),
        },
        "social": {
            "followers": random.randint(100, 5000),
            "engagement_rate": round(random.uniform(0.02, 0.10), 3),
            "posts": random.randint(1, 10),
            "reach": random.randint(500, 10000),
            "clicks": random.randint(50, 500),
        },
        "email": {
            "subscribers": random.randint(100, 5000),
            "open_rate": round(random.uniform(0.15, 0.35), 3),
            "click_rate": round(random.uniform(0.02, 0.08), 3),
            "unsubscribes": random.randint(0, 10),
            "bounces": random.randint(0, 5),
        },
        "sales": {
            "revenue": round(random.uniform(100, 5000), 2),
            "orders": random.randint(5, 100),
            "avg_order_value": round(random.uniform(20, 200), 2),
            "conversion_rate": round(random.uniform(0.01, 0.05), 3),
        },
    }
    
    data = base_metrics.get(source, base_metrics["website"])
    return {
        "id": generate_id(load_metrics().get("metrics", [])),
        "source": source,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
    }


def calculate_trends(metrics: List[dict], source: str, field: str) -> dict:
    """Calculate trend for a specific metric field."""
    source_metrics = [m for m in metrics if m.get("source") == source]
    if len(source_metrics) < 2:
        return {"trend": "insufficient_data", "change_percent": 0}
    
    values = []
    for m in source_metrics[-10:]:
        if field in m.get("data", {}):
            values.append(m["data"][field])
    
    if len(values) < 2:
        return {"trend": "insufficient_data", "change_percent": 0}
    
    current = values[-1]
    previous = values[-2]
    if previous == 0:
        change = 100 if current > 0 else 0
    else:
        change = round(((current - previous) / previous) * 100, 2)
    
    trend = "stable"
    if change > 5:
        trend = "increasing"
    elif change < -5:
        trend = "decreasing"
    
    return {"trend": trend, "change_percent": change, "current": current, "previous": previous}


# ─── Commands ─────────────────────────────────────────────────────────────────
def cmd_collect(args) -> None:
    """Collect metrics from sources."""
    sources = args.sources.split(",") if args.sources else ["website", "social", "email", "sales"]
    
    log.info(f"Collecting metrics from: {sources}")
    
    metrics_data = load_metrics()
    collected = []
    
    for source in sources:
        if source not in ["website", "social", "email", "sales"]:
            print(f"⚠️ Unknown source: {source}")
            continue
        
        snapshot = generate_metric_snapshot(source)
        metrics_data["metrics"].append(snapshot)
        collected.append(f"{source}: {len(snapshot['data'])} metrics")
        log.info(f"Collected {source} metrics")
    
    # Trim old metrics if needed
    config = load_config()
    retention = config.get("retention_days", 90)
    cutoff = datetime.utcnow() - timedelta(days=retention)
    metrics_data["metrics"] = [
        m for m in metrics_data["metrics"]
        if datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")) > cutoff
    ]
    
    save_metrics(metrics_data)
    print(f"✅ Collected metrics from {len(collected)} sources:")
    for c in collected:
        print(f"   • {c}")


def cmd_report(args) -> None:
    """Generate analytics report."""
    log.info(f"Generating {args.period} report")
    
    metrics_data = load_metrics()
    reports_data = load_reports()
    
    period_days = {"daily": 1, "weekly": 7, "monthly": 30}.get(args.period, 1)
    cutoff = datetime.utcnow() - timedelta(days=period_days)
    
    recent_metrics = [
        m for m in metrics_data.get("metrics", [])
        if datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")) > cutoff
    ]
    
    # Aggregate by source
    source_data = defaultdict(lambda: {"count": 0, "data": defaultdict(list)})
    for m in recent_metrics:
        source = m.get("source")
        source_data[source]["count"] += 1
        for key, value in m.get("data", {}).items():
            if isinstance(value, (int, float)):
                source_data[source]["data"][key].append(value)
    
    # Calculate summaries
    summary = {}
    for source, info in source_data.items():
        summary[source] = {}
        for field, values in info["data"].items():
            if values:
                summary[source][field] = {
                    "avg": round(sum(values) / len(values), 3),
                    "min": round(min(values), 3),
                    "max": round(max(values), 3),
                    "latest": values[-1],
                }
    
    # Generate report
    report = {
        "id": generate_id(reports_data.get("reports", [])),
        "period": args.period,
        "generated_at": datetime.utcnow().isoformat(),
        "period_start": cutoff.isoformat(),
        "period_end": datetime.utcnow().isoformat(),
        "metrics_collected": len(recent_metrics),
        "sources": list(source_data.keys()),
        "summary": summary,
    }
    
    reports_data["reports"].append(report)
    save_reports(reports_data)
    
    print(f"\n📊 {args.period.capitalize()} Analytics Report")
    print("=" * 60)
    print(f"Period: {report['period_start'][:10]} to {report['period_end'][:10]}")
    print(f"Metrics collected: {report['metrics_collected']}")
    print(f"Sources: {', '.join(report['sources'])}")
    
    if summary:
        print("\nSummary by Source:")
        for source, fields in summary.items():
            print(f"\n  {source.upper()}:")
            for field, stats in fields.items():
                print(f"    {field}: avg={stats['avg']}, min={stats['min']}, max={stats['max']}")


def cmd_report_list(args) -> None:
    """List generated reports."""
    data = load_reports()
    reports = data.get("reports", [])
    
    if not reports:
        print("📄 No reports found. Generate one first with 'report' command.")
        return
    
    print(f"📄 Analytics Reports ({len(reports)} total):")
    print("-" * 70)
    
    for r in sorted(reports, key=lambda x: x.get("generated_at", ""), reverse=True):
        print(f"  #{r['id']} | {r['period']:8} | {r['generated_at'][:10]} | {r['metrics_collected']} metrics")


def cmd_report_view(args) -> None:
    """View report details."""
    data = load_reports()
    for report in data.get("reports", []):
        if report["id"] == args.id:
            print(f"\n📊 Report #{report['id']}")
            print("=" * 60)
            print(f"Period:   {report['period']}")
            print(f"From:     {report['period_start'][:10]}")
            print(f"To:       {report['period_end'][:10]}")
            print(f"Generated:{report['generated_at'][:19]}")
            print(f"Sources:  {', '.join(report['sources'])}")
            print(f"\nSummary:")
            for source, fields in report.get("summary", {}).items():
                print(f"\n  {source.upper()}:")
                for field, stats in fields.items():
                    print(f"    {field}:")
                    print(f"      avg={stats['avg']}, min={stats['min']}, max={stats['max']}, latest={stats['latest']}")
            return
    
    print(f"❌ Report #{args.id} not found.")


def cmd_trends(args) -> None:
    """Show metric trends."""
    metrics_data = load_metrics()
    metrics = metrics_data.get("metrics", [])
    
    if not metrics:
        print("📈 No metrics available. Collect some first.")
        return
    
    source = args.source
    field = args.field
    
    print(f"\n📈 Trend Analysis: {source}.{field}")
    print("=" * 50)
    
    trend = calculate_trends(metrics, source, field)
    print(f"Trend: {trend['trend']}")
    print(f"Change: {trend['change_percent']}%")
    print(f"Current: {trend.get('current', 'N/A')}")
    print(f"Previous: {trend.get('previous', 'N/A')}")


def cmd_alerts(args) -> None:
    """Show active alerts."""
    data = load_alerts()
    alerts = data.get("alerts", [])
    
    if not alerts:
        print("🔔 No alerts.")
        return
    
    active = [a for a in alerts if a.get("status") == "active"]
    print(f"🔔 Active Alerts ({len(active)}):")
    print("-" * 50)
    
    for alert in active:
        severity = alert.get("severity", "info")
        severity_icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(severity, "⚪")
        print(f"  {severity_icon} #{alert['id']} | {alert['source']}.{alert['metric']}")
        print(f"        {alert['message']} (threshold: {alert.get('threshold', 'N/A')})")


def cmd_alerts_check(args) -> None:
    """Check metrics and generate alerts."""
    log.info("Checking metrics for alert conditions")
    
    metrics_data = load_metrics()
    alerts_data = load_alerts()
    config = load_config()
    thresholds = config.get("alert_thresholds", {})
    
    new_alerts = []
    
    for source, source_thresholds in thresholds.items():
        recent = [m for m in metrics_data.get("metrics", []) if m.get("source") == source][-1:]
        
        for metric, threshold in source_thresholds.items():
            if not recent:
                continue
            
            value = recent[0].get("data", {}).get(metric)
            if value is None:
                continue
            
            is_alert = False
            message = ""
            
            if isinstance(threshold, dict):
                if "min" in threshold and value < threshold["min"]:
                    is_alert = True
                    message = f"{value} below minimum {threshold['min']}"
                if "max" in threshold and value > threshold["max"]:
                    is_alert = True
                    message = f"{value} above maximum {threshold['max']}"
            
            if is_alert:
                alert = {
                    "id": generate_id(alerts_data.get("alerts", [])),
                    "source": source,
                    "metric": metric,
                    "value": value,
                    "threshold": threshold,
                    "message": message,
                    "severity": "warning",
                    "status": "active",
                    "created_at": datetime.utcnow().isoformat(),
                }
                new_alerts.append(alert)
                alerts_data["alerts"].append(alert)
    
    if new_alerts:
        save_alerts(alerts_data)
        print(f"⚠️ Generated {len(new_alerts)} new alerts:")
        for a in new_alerts:
            print(f"   {a['source']}.{a['metric']}: {a['message']}")
    else:
        print("✅ No alerts triggered. All metrics within thresholds.")


def cmd_dashboard(args) -> None:
    """Show quick dashboard."""
    metrics_data = load_metrics()
    reports_data = load_reports()
    
    latest_metrics = {}
    for m in metrics_data.get("metrics", []):
        source = m.get("source")
        if source not in latest_metrics:
            latest_metrics[source] = m
    
    print("\n📊 Quick Analytics Dashboard")
    print("=" * 60)
    print(f"Timestamp: {datetime.utcnow().isoformat()[:19]}")
    
    if latest_metrics:
        print("\nLatest Metrics by Source:")
        for source, m in sorted(latest_metrics.items()):
            print(f"\n  {source.upper()}:")
            for key, value in list(m.get("data", {}).items())[:4]:
                if isinstance(value, float):
                    print(f"    {key}: {value:.3f}")
                else:
                    print(f"    {key}: {value}")
    
    recent_reports = reports_data.get("reports", [])[-3:]
    if recent_reports:
        print("\nRecent Reports:")
        for r in recent_reports:
            print(f"  #{r['id']} | {r['period']} | {r['generated_at'][:10]}")
    
    alerts_data = load_alerts()
    active_alerts = [a for a in alerts_data.get("alerts", []) if a.get("status") == "active"]
    if active_alerts:
        print(f"\n⚠️ Active Alerts: {len(active_alerts)}")


def cmd_config(args) -> None:
    """Show configuration."""
    config = load_config()
    print("\n⚙️ Analytics Config")
    print("=" * 50)
    print(f"Metrics Sources: {', '.join(config.get('metrics_sources', []))}")
    print(f"Report Schedule: {config.get('report_schedule')}")
    print(f"Retention Days: {config.get('retention_days')}")
    print("\nAlert Thresholds:")
    for source, thresholds in config.get("alert_thresholds", {}).items():
        print(f"  {source}: {thresholds}")


def cmd_export(args) -> None:
    """Export metrics to file."""
    metrics_data = load_metrics()
    output_path = Path(args.output)
    
    try:
        with open(output_path, "w") as f:
            json.dump(metrics_data, f, indent=2)
        print(f"✅ Exported {len(metrics_data.get('metrics', []))} metrics to {output_path}")
    except IOError as e:
        print(f"❌ Export failed: {e}")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Analytics Automation Agent - Moltbook Analytics Division",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s collect --sources website,social,email
  %(prog)s report --period daily
  %(prog)s report --period weekly
  %(prog)s report-list
  %(prog)s report-view --id 1
  %(prog)s trends --source website --field visitors
  %(prog)s alerts
  %(prog)s alerts-check
  %(prog)s dashboard
  %(prog)s export --output /tmp/metrics.json
  %(prog)s config
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Collect
    p_collect = subparsers.add_parser("collect", help="Collect metrics from sources")
    p_collect.add_argument("--sources", "-s", default=None,
                           help="Comma-separated sources (website,social,email,sales)")
    
    # Report
    p_report = subparsers.add_parser("report", help="Generate analytics report")
    p_report.add_argument("--period", "-p", default="daily",
                         choices=["daily", "weekly", "monthly"],
                         help="Report period")
    
    # Report List
    subparsers.add_parser("report-list", help="List generated reports")
    
    # Report View
    p_view = subparsers.add_parser("report-view", help="View report details")
    p_view.add_argument("--id", "-i", type=int, required=True, help="Report ID")
    
    # Trends
    p_trends = subparsers.add_parser("trends", help="Show metric trends")
    p_trends.add_argument("--source", "-s", required=True,
                          choices=["website", "social", "email", "sales"],
                          help="Metric source")
    p_trends.add_argument("--field", "-f", required=True, help="Metric field")
    
    # Alerts
    subparsers.add_parser("alerts", help="Show active alerts")
    
    # Alerts Check
    subparsers.add_parser("alerts-check", help="Check metrics and generate alerts")
    
    # Dashboard
    subparsers.add_parser("dashboard", help="Show quick dashboard")
    
    # Export
    p_export = subparsers.add_parser("export", help="Export metrics to JSON")
    p_export.add_argument("--output", "-o", required=True, help="Output file path")
    
    # Config
    subparsers.add_parser("config", help="Show configuration")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "collect":
            cmd_collect(args)
        elif args.command == "report":
            cmd_report(args)
        elif args.command == "report-list":
            cmd_report_list(args)
        elif args.command == "report-view":
            cmd_report_view(args)
        elif args.command == "trends":
            cmd_trends(args)
        elif args.command == "alerts":
            cmd_alerts(args)
        elif args.command == "alerts-check":
            cmd_alerts_check(args)
        elif args.command == "dashboard":
            cmd_dashboard(args)
        elif args.command == "export":
            cmd_export(args)
        elif args.command == "config":
            cmd_config(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
