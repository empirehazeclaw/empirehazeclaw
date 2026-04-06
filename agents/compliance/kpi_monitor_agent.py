#!/usr/bin/env python3
"""
KPI Monitor Agent
Tracks and monitors key performance indicators for business operations
Generates dashboards and alerts based on KPI thresholds
"""

import argparse
import json
import logging
import os
import sqlite3
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "kpi_monitor.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("KPIMonitor")


@dataclass
class KPI:
    """Represents a single KPI metric"""
    id: str
    name: str
    value: float
    unit: str
    target: float
    threshold_low: float
    threshold_high: float
    category: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def status(self) -> str:
        """Determine KPI status based on thresholds"""
        if self.value < self.threshold_low:
            return "critical_low"
        elif self.value > self.threshold_high:
            return "critical_high"
        elif self.value < self.target * 0.9 or self.value > self.target * 1.1:
            return "warning"
        return "on_target"


@dataclass
class Alert:
    """Represents a KPI alert"""
    kpi_id: str
    kpi_name: str
    severity: str
    message: str
    current_value: float
    threshold: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class KPIMonitor:
    """KPI Monitoring and Alerting System"""
    
    # Default KPI templates
    DEFAULT_KPIS = {
        "system_uptime": {
            "name": "System Uptime",
            "target": 99.9,
            "threshold_low": 95.0,
            "threshold_high": 100.0,
            "unit": "%",
            "category": "infrastructure"
        },
        "response_time_avg": {
            "name": "Average Response Time",
            "target": 200,
            "threshold_low": 0,
            "threshold_high": 500,
            "unit": "ms",
            "category": "performance"
        },
        "error_rate": {
            "name": "Error Rate",
            "target": 0.1,
            "threshold_low": 0,
            "threshold_high": 1.0,
            "unit": "%",
            "category": "quality"
        },
        "cpu_usage": {
            "name": "CPU Usage",
            "target": 50,
            "threshold_low": 0,
            "threshold_high": 80,
            "unit": "%",
            "category": "infrastructure"
        },
        "memory_usage": {
            "name": "Memory Usage",
            "target": 60,
            "threshold_low": 0,
            "threshold_high": 85,
            "unit": "%",
            "category": "infrastructure"
        },
        "disk_usage": {
            "name": "Disk Usage",
            "target": 70,
            "threshold_low": 0,
            "threshold_high": 90,
            "unit": "%",
            "category": "infrastructure"
        },
        "active_users": {
            "name": "Active Users",
            "target": 100,
            "threshold_low": 10,
            "threshold_high": 500,
            "unit": "users",
            "category": "business"
        },
        "revenue_daily": {
            "name": "Daily Revenue",
            "target": 1000,
            "threshold_low": 100,
            "threshold_high": 10000,
            "unit": "USD",
            "category": "business"
        },
        "conversion_rate": {
            "name": "Conversion Rate",
            "target": 3.5,
            "threshold_low": 1.0,
            "threshold_high": 10.0,
            "unit": "%",
            "category": "business"
        },
        "support_tickets_open": {
            "name": "Open Support Tickets",
            "target": 10,
            "threshold_low": 0,
            "threshold_high": 50,
            "unit": "tickets",
            "category": "operations"
        }
    }
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir or "/home/clawbot/.openclaw/workspace/data")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.kpi_file = self.output_dir / f"kpi_status_{datetime.now().strftime('%Y%m%d')}.json"
        self.alerts_file = self.output_dir / f"kpi_alerts_{datetime.now().strftime('%Y%m%d')}.json"
        self.history_file = self.output_dir / "kpi_history.db"
        self.dashboard_file = self.output_dir / "kpi_dashboard.json"
        
        self.kpis: Dict[str, KPI] = {}
        self.alerts: List[Alert] = []
        
        self._init_db()
    
    def _init_db(self):
        """Initialize KPI history database"""
        conn = sqlite3.connect(self.history_file)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS kpi_history
                     (id TEXT, name TEXT, value REAL, unit TEXT,
                      target REAL, category TEXT, timestamp TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS alerts
                     (id INTEGER PRIMARY KEY, kpi_id TEXT, severity TEXT,
                      message TEXT, current_value REAL, threshold REAL,
                      timestamp TEXT, acknowledged INTEGER DEFAULT 0)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS daily_stats
                     (date TEXT PRIMARY KEY, avg_value REAL, max_value REAL,
                      min_value REAL, count INTEGER)''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized: {self.history_file}")
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Gather system metrics"""
        metrics = {}
        
        # CPU usage
        try:
            with open('/proc/loadavg') as f:
                load = float(f.read().split()[0])
                # Convert load to percentage (simplified)
                metrics['cpu_usage'] = min(load * 25, 100)  # Rough approximation
        except (FileNotFoundError, PermissionError):
            metrics['cpu_usage'] = 0
        
        # Memory usage
        try:
            with open('/proc/meminfo') as f:
                meminfo = f.read()
                total = used = 0
                for line in meminfo.split('\n'):
                    if line.startswith('MemTotal:'):
                        total = int(line.split()[1])
                    elif line.startswith('MemAvailable:'):
                        used = int(line.split()[1])
                if total > 0:
                    metrics['memory_usage'] = ((total - used) / total) * 100
                else:
                    metrics['memory_usage'] = 0
        except (FileNotFoundError, PermissionError):
            metrics['memory_usage'] = 0
        
        # Disk usage
        try:
            import shutil
            usage = shutil.disk_usage('/')
            metrics['disk_usage'] = (usage.used / usage.total) * 100
        except Exception:
            metrics['disk_usage'] = 0
        
        return metrics
    
    def _get_demo_kpi_value(self, kpi_id: str) -> float:
        """Get a demo value for a KPI (simulates data collection)"""
        import random
        
        # Simulated values for demo
        demo_values = {
            "system_uptime": 99.7 + random.random() * 0.3,
            "response_time_avg": 150 + random.random() * 100,
            "error_rate": random.random() * 0.5,
            "cpu_usage": 20 + random.random() * 40,
            "memory_usage": 40 + random.random() * 30,
            "disk_usage": 50 + random.random() * 20,
            "active_users": int(80 + random.random() * 40),
            "revenue_daily": 800 + random.random() * 400,
            "conversion_rate": 2.5 + random.random() * 2,
            "support_tickets_open": int(random.random() * 15)
        }
        
        return demo_values.get(kpi_id, 0)
    
    def add_kpi(self, kpi: KPI):
        """Add a KPI to monitoring"""
        self.kpis[kpi.id] = kpi
        logger.info(f"Added KPI: {kpi.name} = {kpi.value} {kpi.unit}")
    
    def add_kpi_from_template(self, kpi_id: str, value: Optional[float] = None) -> KPI:
        """Add a KPI from a predefined template"""
        if kpi_id not in self.DEFAULT_KPIS:
            raise ValueError(f"Unknown KPI template: {kpi_id}")
        
        template = self.DEFAULT_KPIS[kpi_id]
        
        # Get actual value
        if value is None:
            value = self._get_demo_kpi_value(kpi_id)
        
        kpi = KPI(
            id=kpi_id,
            name=template["name"],
            value=value,
            unit=template["unit"],
            target=template["target"],
            threshold_low=template["threshold_low"],
            threshold_high=template["threshold_high"],
            category=template["category"]
        )
        
        self.add_kpi(kpi)
        return kpi
    
    def update_kpi(self, kpi_id: str, value: float):
        """Update an existing KPI value"""
        if kpi_id not in self.kpis:
            # Add from template if it exists
            if kpi_id in self.DEFAULT_KPIS:
                self.add_kpi_from_template(kpi_id, value)
            else:
                raise ValueError(f"KPI not found: {kpi_id}")
        else:
            self.kpis[kpi_id].value = value
            self.kpis[kpi_id].timestamp = datetime.now().isoformat()
        
        # Check thresholds and generate alerts
        self._check_thresholds(self.kpis[kpi_id])
    
    def _check_thresholds(self, kpi: KPI):
        """Check KPI against thresholds and generate alerts"""
        status = kpi.status()
        
        if status == "critical_low":
            alert = Alert(
                kpi_id=kpi.id,
                kpi_name=kpi.name,
                severity="critical",
                message=f"{kpi.name} is critically low: {kpi.value:.2f}{kpi.unit}",
                current_value=kpi.value,
                threshold=kpi.threshold_low
            )
            self.alerts.append(alert)
            logger.warning(f"CRITICAL: {alert.message}")
        
        elif status == "critical_high":
            alert = Alert(
                kpi_id=kpi.id,
                kpi_name=kpi.name,
                severity="critical",
                message=f"{kpi.name} is critically high: {kpi.value:.2f}{kpi.unit}",
                current_value=kpi.value,
                threshold=kpi.threshold_high
            )
            self.alerts.append(alert)
            logger.warning(f"CRITICAL: {alert.message}")
        
        elif status == "warning":
            direction = "below target" if kpi.value < kpi.target else "above target"
            alert = Alert(
                kpi_id=kpi.id,
                kpi_name=kpi.name,
                severity="warning",
                message=f"{kpi.name} is {direction}: {kpi.value:.2f}{kpi.unit} (target: {kpi.target:.2f})",
                current_value=kpi.value,
                threshold=kpi.target
            )
            self.alerts.append(alert)
            logger.info(f"WARNING: {alert.message}")
    
    def _save_to_db(self, kpi: KPI):
        """Save KPI value to history database"""
        conn = sqlite3.connect(self.history_file)
        c = conn.cursor()
        
        c.execute('''INSERT INTO kpi_history VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (kpi.id, kpi.name, kpi.value, kpi.unit, kpi.target, kpi.category, kpi.timestamp))
        
        conn.commit()
        conn.close()
    
    def collect_all_metrics(self):
        """Collect all system metrics"""
        system_metrics = self._get_system_metrics()
        
        # Map system metrics to KPIs
        for metric_name, value in system_metrics.items():
            if metric_name in self.DEFAULT_KPIS:
                self.update_kpi(metric_name, value)
            elif metric_name == "disk_usage":
                self.update_kpi("disk_usage", value)
    
    def get_kpi_history(self, kpi_id: str, days: int = 7) -> List[Dict]:
        """Get KPI history for specified number of days"""
        conn = sqlite3.connect(self.history_file)
        c = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        c.execute('''SELECT timestamp, value FROM kpi_history
                     WHERE id = ? AND timestamp > ?
                     ORDER BY timestamp ASC''',
                  (kpi_id, cutoff))
        
        results = [{"timestamp": row[0], "value": row[1]} for row in c.fetchall()]
        
        conn.close()
        return results
    
    def get_daily_summary(self, days: int = 30) -> List[Dict]:
        """Get daily summary statistics"""
        conn = sqlite3.connect(self.history_file)
        c = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        c.execute('''SELECT date, avg_value, max_value, min_value, count
                     FROM daily_stats WHERE date > ? ORDER BY date DESC''',
                  (cutoff,))
        
        results = [
            {"date": row[0], "avg": row[1], "max": row[2], "min": row[3], "count": row[4]}
            for row in c.fetchall()
        ]
        
        conn.close()
        return results
    
    def acknowledge_alert(self, alert_index: int):
        """Acknowledge an alert"""
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index].acknowledged = True
            logger.info(f"Alert acknowledged: {self.alerts[alert_index].message}")
    
    def generate_dashboard(self) -> Dict:
        """Generate dashboard data"""
        dashboard = {
            "generated_at": datetime.now().isoformat(),
            "kpis": [],
            "alerts": [],
            "summary": {
                "total_kpis": len(self.kpis),
                "on_target": 0,
                "warning": 0,
                "critical": 0
            },
            "categories": {}
        }
        
        # Categorize KPIs
        for kpi in self.kpis.values():
            kpi_data = {
                "id": kpi.id,
                "name": kpi.name,
                "value": round(kpi.value, 2),
                "unit": kpi.unit,
                "target": kpi.target,
                "status": kpi.status(),
                "variance": round(((kpi.value - kpi.target) / kpi.target) * 100, 1) if kpi.target != 0 else 0
            }
            dashboard["kpis"].append(kpi_data)
            
            status = kpi.status()
            if status == "on_target":
                dashboard["summary"]["on_target"] += 1
            elif "warning" in status:
                dashboard["summary"]["warning"] += 1
            else:
                dashboard["summary"]["critical"] += 1
            
            if kpi.category not in dashboard["categories"]:
                dashboard["categories"][kpi.category] = []
            dashboard["categories"][kpi.category].append(kpi_data)
        
        # Add active alerts
        for alert in self.alerts:
            if not getattr(alert, 'acknowledged', False):
                dashboard["alerts"].append({
                    "kpi_id": alert.kpi_id,
                    "kpi_name": alert.kpi_name,
                    "severity": alert.severity,
                    "message": alert.message,
                    "timestamp": alert.timestamp
                })
        
        return dashboard
    
    def save_results(self):
        """Save current KPI status and alerts"""
        # Save KPI status
        kpi_data = {kpi_id: asdict(kpi) for kpi_id, kpi in self.kpis.items()}
        
        with open(self.kpi_file, 'w') as f:
            json.dump(kpi_data, f, indent=2)
        
        # Save alerts
        alerts_data = [asdict(alert) for alert in self.alerts]
        
        with open(self.alerts_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)
        
        # Save dashboard
        dashboard = self.generate_dashboard()
        
        with open(self.dashboard_file, 'w') as f:
            json.dump(dashboard, f, indent=2)
        
        # Save to history
        for kpi in self.kpis.values():
            self._save_to_db(kpi)
        
        logger.info(f"KPI data saved to {self.output_dir}")
    
    def run_monitoring(self, collect_system: bool = True):
        """Run KPI monitoring cycle"""
        logger.info("Starting KPI monitoring cycle")
        
        # Collect system metrics
        if collect_system:
            self.collect_all_metrics()
        
        # If no KPIs configured, add defaults
        if not self.kpis:
            for kpi_id in self.DEFAULT_KPIS:
                self.add_kpi_from_template(kpi_id)
        
        # Generate dashboard
        dashboard = self.generate_dashboard()
        
        # Save results
        self.save_results()
        
        return dashboard
    
    def print_dashboard(self, dashboard: Optional[Dict] = None):
        """Print KPI dashboard to console"""
        if dashboard is None:
            dashboard = self.generate_dashboard()
        
        print(f"\n{'='*70}")
        print(f"KPI MONITORING DASHBOARD")
        print(f"{'='*70}")
        print(f"Generated: {dashboard['generated_at']}")
        
        summary = dashboard.get("summary", {})
        print(f"\nSummary:")
        print(f"  Total KPIs: {summary.get('total_kpis', 0)}")
        print(f"  ✅ On Target: {summary.get('on_target', 0)}")
        print(f"  ⚠️  Warning: {summary.get('warning', 0)}")
        print(f"  ❌ Critical: {summary.get('critical', 0)}")
        
        if dashboard.get("alerts"):
            print(f"\nActive Alerts ({len(dashboard['alerts'])}):")
            for alert in dashboard["alerts"][:5]:
                icon = "🔴" if alert["severity"] == "critical" else "🟡"
                print(f"  {icon} [{alert['severity'].upper()}] {alert['message']}")
        
        print(f"\nKPI Details:")
        for kpi in dashboard.get("kpis", []):
            status_icon = "✅" if kpi["status"] == "on_target" else "⚠️" if "warning" in kpi["status"] else "❌"
            variance_str = f"{kpi['variance']:+.1f}%" if kpi["variance"] != 0 else ""
            
            print(f"  {status_icon} {kpi['name']}: {kpi['value']}{kpi['unit']} (target: {kpi['target']}{kpi['unit']}) {variance_str}")
        
        print(f"\nDashboard saved to: {self.dashboard_file}")
        print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description="KPI Monitor - Track and monitor key performance indicators",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --monitor                   Run KPI monitoring with defaults
  %(prog)s --monitor --kpi cpu_usage    Monitor specific KPI
  %(prog)s --history error_rate        Get history for a KPI
  %(prog)s --dashboard                 Print current dashboard
  %(prog)s --set response_time_avg=150  Set KPI value manually
        """
    )
    parser.add_argument("--monitor", "-m", action="store_true", help="Run KPI monitoring cycle")
    parser.add_argument("--dashboard", "-d", action="store_true", help="Show current dashboard")
    parser.add_argument("--kpi", "-k", help="Monitor specific KPI ID")
    parser.add_argument("--history", help="Get KPI history (specify KPI ID)")
    parser.add_argument("--days", type=int, default=7, help="Number of days for history")
    parser.add_argument("--set", "-s", help="Set KPI value (format: kpi_id=value)")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    monitor = KPIMonitor(args.output)
    
    try:
        if args.set:
            # Set a specific KPI value
            kpi_id, value = args.set.split('=')
            monitor.update_kpi(kpi_id.strip(), float(value.strip()))
            monitor.save_results()
            print(f"Updated {kpi_id} = {value}")
        
        elif args.history:
            # Get KPI history
            history = monitor.get_kpi_history(args.history, args.days)
            print(f"\nKPI History: {args.history} (last {args.days} days)")
            print(f"{'='*50}")
            for entry in history:
                print(f"  {entry['timestamp']}: {entry['value']}")
        
        elif args.dashboard:
            # Show dashboard
            with open(monitor.dashboard_file) as f:
                dashboard = json.load(f)
            monitor.print_dashboard(dashboard)
        
        elif args.monitor:
            # Run monitoring
            if args.kpi:
                monitor.add_kpi_from_template(args.kpi)
            else:
                monitor.run_monitoring()
            
            dashboard = monitor.generate_dashboard()
            monitor.print_dashboard(dashboard)
        
        else:
            # Default: show dashboard
            if monitor.dashboard_file.exists():
                with open(monitor.dashboard_file) as f:
                    dashboard = json.load(f)
                monitor.print_dashboard(dashboard)
            else:
                print("No dashboard found. Run --monitor to collect KPIs.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nMonitoring interrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
