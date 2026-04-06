#!/usr/bin/env python3
"""
CTO Tech Agent
==============
Manages technical infrastructure, monitors services, handles deployments,
and tracks technical debt and system health.
"""

import argparse
import json
import sys
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import uuid

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CTO - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "cto_tech.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Data paths
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/business")
DATA_DIR.mkdir(parents=True, exist_ok=True)
SERVICES_FILE = DATA_DIR / "services.json"
DEPLOYMENTS_FILE = DATA_DIR / "deployments.json"
SYSTEMS_FILE = DATA_DIR / "systems.json"
TECH_DEBT_FILE = DATA_DIR / "tech_debt.json"


def load_json(filepath: Path, default: dict = None) -> dict:
    """Load JSON file or return default."""
    if default is None:
        default = {}
    try:
        if filepath.exists():
            return json.loads(filepath.read_text())
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
    return default


def save_json(filepath: Path, data: dict) -> bool:
    """Save data to JSON file."""
    try:
        filepath.write_text(json.dumps(data, indent=2, default=str))
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def init_data_files():
    """Initialize data files if they don't exist."""
    if not SERVICES_FILE.exists():
        save_json(SERVICES_FILE, {"services": []})
    
    if not DEPLOYMENTS_FILE.exists():
        save_json(DEPLOYMENTS_FILE, {"deployments": []})
    
    if not SYSTEMS_FILE.exists():
        save_json(SYSTEMS_FILE, {"systems": []})
    
    if not TECH_DEBT_FILE.exists():
        save_json(TECH_DEBT_FILE, {"items": []})


def check_service_health(service_url: str) -> dict:
    """Check if a service is responding."""
    try:
        import urllib.request
        import urllib.error
        req = urllib.request.Request(service_url, method='HEAD')
        req.add_header('User-Agent', 'CTO-Agent/1.0')
        with urllib.request.urlopen(req, timeout=5) as response:
            return {"status": "healthy", "code": response.status}
    except urllib.error.HTTPError as e:
        return {"status": "error", "code": e.code}
    except Exception as e:
        return {"status": "down", "error": str(e)}


def cmd_status(args) -> int:
    """Show technical infrastructure status."""
    logger.info("Showing tech infrastructure status...")
    
    services = load_json(SERVICES_FILE)
    deployments = load_json(DEPLOYMENTS_FILE)
    systems = load_json(SYSTEMS_FILE)
    tech_debt = load_json(TECH_DEBT_FILE)
    
    print("\n" + "="*60)
    print("💻 CTO TECH DASHBOARD")
    print("="*60)
    print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-"*60)
    
    print("\n🛠️  SERVICES")
    print(f"   Total Registered: {len(services.get('services', []))}")
    
    healthy = len([s for s in services.get('services', []) if s.get('health') == 'healthy'])
    degraded = len([s for s in services.get('services', []) if s.get('health') == 'degraded'])
    down = len([s for s in services.get('services', []) if s.get('health') == 'down'])
    
    print(f"   Healthy: {healthy} | Degraded: {degraded} | Down: {down}")
    
    if services.get('services'):
        print("\n   Service Health:")
        for svc in services.get('services', [])[:5]:
            health_icon = {"healthy": "🟢", "degraded": "🟡", "down": "🔴"}.get(svc.get('health', 'unknown'), "⚪")
            print(f"      {health_icon} {svc.get('name', 'Unknown')} ({svc.get('url', '')})")
    
    print("\n🚀 DEPLOYMENTS")
    print(f"   Total: {len(deployments.get('deployments', []))}")
    recent = [d for d in deployments.get('deployments', []) 
               if d.get('deployed_at', '').startswith(datetime.now().strftime('%Y-%m-%d'))]
    print(f"   Today: {len(recent)}")
    
    print("\n💻 SYSTEMS")
    print(f"   Total: {len(systems.get('systems', []))}")
    
    print("\n📊 TECHNICAL DEBT")
    print(f"   Total Items: {len(tech_debt.get('items', []))}")
    high_priority = len([t for t in tech_debt.get('items', []) if t.get('priority') == 'high'])
    print(f"   High Priority: {high_priority}")
    
    print("\n" + "="*60)
    return 0


def cmd_health_check(args) -> int:
    """Perform health check on all services."""
    logger.info("Running health checks...")
    
    services = load_json(SERVICES_FILE)
    all_services = services.get('services', [])
    
    if not all_services:
        print("No services registered. Add services first.")
        return 0
    
    print("\n🔍 Running Health Checks...")
    print("-"*60)
    
    results = []
    for svc in all_services:
        url = svc.get('url', '')
        if not url:
            continue
        
        print(f"   Checking {svc.get('name')}... ", end="", flush=True)
        health = check_service_health(url)
        
        svc['health'] = health['status']
        svc['last_check'] = datetime.now().isoformat()
        results.append({"name": svc.get('name'), "health": health})
        
        if health['status'] == 'healthy':
            print(f"🟢 OK ({health['code']})")
        elif health['status'] == 'error':
            print(f"🟡 Error ({health['code']})")
        else:
            print(f"🔴 Down ({health.get('error', 'Unknown')})")
    
    save_json(SERVICES_FILE, services)
    
    # Summary
    healthy = len([r for r in results if r['health']['status'] == 'healthy'])
    print(f"\n📊 Summary: {healthy}/{len(results)} services healthy")
    
    return 0


def cmd_add_service(args) -> int:
    """Register a new service."""
    logger.info(f"Adding service: {args.name}")
    
    services = load_json(SERVICES_FILE)
    
    service = {
        "id": str(uuid.uuid4())[:8],
        "name": args.name,
        "url": args.url,
        "type": args.type or "web",
        "health": "unknown",
        "last_check": None,
        "created_at": datetime.now().isoformat(),
        "notes": args.notes or ""
    }
    
    services['services'].append(service)
    save_json(SERVICES_FILE, services)
    
    print(f"✅ Service added: {args.name}")
    return 0


def cmd_list_services(args) -> int:
    """List all registered services."""
    logger.info("Listing services...")
    
    services = load_json(SERVICES_FILE)
    all_services = services.get('services', [])
    
    if not all_services:
        print("No services registered.")
        return 0
    
    print(f"\n🛠️  Services ({len(all_services)}):")
    print("-"*70)
    for svc in all_services:
        health_icon = {"healthy": "🟢", "degraded": "🟡", "down": "🔴", "unknown": "⚪"}.get(
            svc.get('health', 'unknown'), "⚪")
        print(f"   {health_icon} {svc.get('name'):<25} | {svc.get('url', ''):<30} | {svc.get('type', 'web')}")
    
    return 0


def cmd_log_deployment(args) -> int:
    """Log a new deployment."""
    logger.info(f"Logging deployment: {args.version}")
    
    deployments = load_json(DEPLOYMENTS_FILE)
    
    deployment = {
        "id": str(uuid.uuid4())[:8],
        "version": args.version,
        "environment": args.environment or "production",
        "status": args.status or "deployed",
        "deployed_by": args.deployed_by or "unknown",
        "deployed_at": datetime.now().isoformat(),
        "notes": args.notes or "",
        "rollback_available": args.rollback.lower() == 'yes' if args.rollback else True
    }
    
    deployments['deployments'].append(deployment)
    save_json(DEPLOYMENTS_FILE, deployments)
    
    print(f"✅ Deployment logged: v{args.version} to {args.environment}")
    return 0


def cmd_list_deployments(args) -> int:
    """List deployment history."""
    logger.info("Listing deployments...")
    
    deployments = load_json(DEPLOYMENTS_FILE)
    all_deps = deployments.get('deployments', [])
    
    if args.environment:
        all_deps = [d for d in all_deps if d.get('environment') == args.environment]
    
    if not all_deps:
        print("No deployments found.")
        return 0
    
    print(f"\n🚀 Deployments ({len(all_deps)}):")
    print("-"*70)
    for dep in sorted(all_deps, key=lambda x: x.get('deployed_at', ''), reverse=True)[:10]:
        status_icon = {"deployed": "🟢", "failed": "🔴", "rolling_back": "🟡"}.get(
            dep.get('status', 'deployed'), "⚪")
        date = dep.get('deployed_at', '')[:10]
        print(f"   {status_icon} v{dep.get('version', '?')} | {dep.get('environment', '?'):<12} | {date} | {dep.get('deployed_by', '?')}")
    
    return 0


def cmd_add_system(args) -> int:
    """Add a system component."""
    logger.info(f"Adding system: {args.name}")
    
    systems = load_json(SYSTEMS_FILE)
    
    system = {
        "id": str(uuid.uuid4())[:8],
        "name": args.name,
        "type": args.type or "component",
        "status": args.system_status or "operational",
        "provider": args.provider or "",
        "cost_monthly": float(args.monthly_cost) if args.monthly_cost else 0,
        "created_at": datetime.now().isoformat()
    }
    
    systems['systems'].append(system)
    save_json(SYSTEMS_FILE, systems)
    
    print(f"✅ System added: {args.name}")
    return 0


def cmd_infrastructure_cost(args) -> int:
    """Calculate total infrastructure costs."""
    logger.info("Calculating infrastructure costs...")
    
    systems = load_json(SYSTEMS_FILE)
    all_systems = systems.get('systems', [])
    
    if not all_systems:
        print("No systems registered.")
        return 0
    
    total_monthly = sum(s.get('cost_monthly', 0) for s in all_systems)
    total_annual = total_monthly * 12
    
    # Group by type
    by_type = {}
    for s in all_systems:
        t = s.get('type', 'other')
        by_type[t] = by_type.get(t, 0) + s.get('cost_monthly', 0)
    
    print("\n" + "="*60)
    print("💰 INFRASTRUCTURE COSTS")
    print("="*60)
    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-"*60)
    
    print(f"\n📊 TOTAL COSTS")
    print(f"   Monthly: ${total_monthly:,.2f}")
    print(f"   Annual:  ${total_annual:,.2f}")
    
    print(f"\n📊 BY TYPE")
    for t, cost in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        print(f"   {t:<20} ${cost:>10,.2f}/mo")
    
    print("\n" + "="*60)
    return 0


def cmd_add_tech_debt(args) -> int:
    """Add a technical debt item."""
    logger.info(f"Adding tech debt: {args.title}")
    
    tech_debt = load_json(TECH_DEBT_FILE)
    
    item = {
        "id": str(uuid.uuid4())[:8],
        "title": args.title,
        "description": args.description or "",
        "area": args.area or "general",
        "priority": args.priority or "medium",
        "effort_hours": float(args.effort) if args.effort else 0,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "ticket_ref": args.ticket or ""
    }
    
    tech_debt['items'].append(item)
    save_json(TECH_DEBT_FILE, tech_debt)
    
    print(f"✅ Tech debt item added: {args.title}")
    return 0


def cmd_list_tech_debt(args) -> int:
    """List technical debt items."""
    logger.info("Listing tech debt...")
    
    tech_debt = load_json(TECH_DEBT_FILE)
    items = tech_debt.get('items', [])
    
    if args.area:
        items = [i for i in items if i.get('area') == args.area]
    if args.priority:
        items = [i for i in items if i.get('priority') == args.priority]
    
    if not items:
        print("No tech debt items found.")
        return 0
    
    total_effort = sum(i.get('effort_hours', 0) for i in items)
    
    print(f"\n📊 Technical Debt ({len(items)} items, ~{total_effort:.0f}h effort):")
    print("-"*70)
    for item in items:
        prio_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(item.get('priority', 'medium'), "⚪")
        print(f"   {prio_icon} [{item.get('priority', '?')}] {item.get('title', 'Untitled')}")
        print(f"       Area: {item.get('area', '?')} | Effort: {item.get('effort_hours', 0)}h")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="💻 CTO Tech Agent - Infrastructure & Technical Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                    Show tech infrastructure status
  %(prog)s health-check              Run health checks on all services
  %(prog)s add-service --name API --url https://api.example.com
  %(prog)s list-services
  %(prog)s log-deployment --version 2.1.0 --environment production
  %(prog)s list-deployments --environment production
  %(prog)s add-system --name "Main DB" --type database --monthly-cost 50
  %(prog)s infrastructure-cost        Show infrastructure costs
  %(prog)s add-tech-debt --title "Legacy auth" --priority high --effort 16
  %(prog)s list-tech-debt --priority high
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show tech infrastructure status')
    
    # Health check
    subparsers.add_parser('health-check', help='Run health checks on all services')
    
    # Service commands
    svc_parser = subparsers.add_parser('add-service', help='Register a new service')
    svc_parser.add_argument('--name', required=True, help='Service name')
    svc_parser.add_argument('--url', required=True, help='Service URL')
    svc_parser.add_argument('--type', help='Service type (web, api, db, etc.)')
    svc_parser.add_argument('--notes', help='Notes')
    
    subparsers.add_parser('list-services', help='List all services')
    
    # Deployment commands
    dep_parser = subparsers.add_parser('log-deployment', help='Log a deployment')
    dep_parser.add_argument('--version', required=True, help='Version number')
    dep_parser.add_argument('--environment', default='production', help='Environment')
    dep_parser.add_argument('--status', default='deployed', help='Deployment status')
    dep_parser.add_argument('--deployed-by', help='Who deployed')
    dep_parser.add_argument('--notes', help='Notes')
    dep_parser.add_argument('--rollback', choices=['yes', 'no'], help='Rollback available')
    
    list_dep_parser = subparsers.add_parser('list-deployments', help='List deployments')
    list_dep_parser.add_argument('--environment', help='Filter by environment')
    
    # System commands
    sys_parser = subparsers.add_parser('add-system', help='Add a system component')
    sys_parser.add_argument('--name', required=True, help='System name')
    sys_parser.add_argument('--type', help='System type (server, db, storage, etc.)')
    sys_parser.add_argument('--status', dest='system_status', default='operational', help='System status')
    sys_parser.add_argument('--provider', help='Provider name')
    sys_parser.add_argument('--monthly-cost', help='Monthly cost in USD')
    
    subparsers.add_parser('infrastructure-cost', help='Calculate infrastructure costs')
    
    # Tech debt commands
    debt_parser = subparsers.add_parser('add-tech-debt', help='Add technical debt item')
    debt_parser.add_argument('--title', required=True, help='Title')
    debt_parser.add_argument('--description', help='Description')
    debt_parser.add_argument('--area', help='Area (frontend, backend, db, etc.)')
    debt_parser.add_argument('--priority', default='medium', choices=['low', 'medium', 'high'])
    debt_parser.add_argument('--effort', help='Estimated effort in hours')
    debt_parser.add_argument('--ticket', help='Ticket reference')
    
    list_debt_parser = subparsers.add_parser('list-tech-debt', help='List tech debt items')
    list_debt_parser.add_argument('--area', help='Filter by area')
    list_debt_parser.add_argument('--priority', choices=['low', 'medium', 'high'])
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize data files
    init_data_files()
    
    # Route to command handler
    commands = {
        'status': cmd_status,
        'health-check': cmd_health_check,
        'add-service': cmd_add_service,
        'list-services': cmd_list_services,
        'log-deployment': cmd_log_deployment,
        'list-deployments': cmd_list_deployments,
        'add-system': cmd_add_system,
        'infrastructure-cost': cmd_infrastructure_cost,
        'add-tech-debt': cmd_add_tech_debt,
        'list-tech-debt': cmd_list_tech_debt
    }
    
    try:
        return commands[args.command](args)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
