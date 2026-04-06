#!/usr/bin/env python3
"""
API Integrations Agent - Productivity Suite
Manage API integrations, credentials, and external service connections.

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
from urllib.parse import urlparse

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = SCRIPT_DIR.parent.parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = WORKSPACE / "data" / "api_integrations"
INTEGRATIONS_FILE = DATA_DIR / "integrations.json"
CREDENTIALS_FILE = DATA_DIR / "credentials.json"
REQUESTS_FILE = DATA_DIR / "requests.json"
CONFIG_FILE = DATA_DIR / "config.json"

# Ensure directories
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [API-INTEGRATIONS] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "api_integrations.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("APIIntegrations")


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


def load_integrations() -> dict:
    """Load integrations database."""
    defaults = {
        "integrations": [
            {
                "id": 1,
                "name": "Stripe Payments",
                "service": "stripe",
                "type": "payment",
                "status": "active",
                "base_url": "https://api.stripe.com/v1",
                "endpoints": ["/customers", "/charges", "/subscriptions"],
                "rate_limit": 100,
                "last_call": None,
                "created_at": "2026-03-01T00:00:00Z",
            },
            {
                "id": 2,
                "name": "SendGrid Email",
                "service": "sendgrid",
                "type": "email",
                "status": "active",
                "base_url": "https://api.sendgrid.com/v3",
                "endpoints": ["/mail/send", "/contacts", "/templates"],
                "rate_limit": 1000,
                "last_call": None,
                "created_at": "2026-03-01T00:00:00Z",
            },
            {
                "id": 3,
                "name": "Shopify Store",
                "service": "shopify",
                "type": "ecommerce",
                "status": "active",
                "base_url": "https://{shop}.myshopify.com/admin/api/2024-01",
                "endpoints": ["/products.json", "/orders.json", "/customers.json"],
                "rate_limit": 40,
                "last_call": None,
                "created_at": "2026-03-05T00:00:00Z",
            },
        ],
        "last_updated": None,
    }
    return load_json(INTEGRATIONS_FILE, defaults)


def save_integrations(data: dict) -> None:
    """Save integrations database."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(INTEGRATIONS_FILE, data)


def load_credentials() -> dict:
    """Load credentials (encrypted in production)."""
    defaults = {
        "credentials": [
            {"id": 1, "integration_id": 1, "name": "Stripe Key", "type": "api_key", "last_used": None},
            {"id": 2, "integration_id": 2, "name": "SendGrid Key", "type": "api_key", "last_used": None},
            {"id": 3, "integration_id": 3, "name": "Shopify Token", "type": "access_token", "last_used": None},
        ],
        "last_updated": None,
    }
    return load_json(CREDENTIALS_FILE, defaults)


def save_credentials(data: dict) -> None:
    """Save credentials."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(CREDENTIALS_FILE, data)


def load_requests() -> dict:
    """Load API request history."""
    return load_json(REQUESTS_FILE, {"requests": [], "last_updated": None})


def save_requests(data: dict) -> None:
    """Save API request history."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(REQUESTS_FILE, data)


def load_config() -> dict:
    """Load configuration."""
    defaults = {
        "timeout_seconds": 30,
        "max_retries": 3,
        "retry_delay_seconds": 1,
        "rate_limit_strategy": "exponential_backoff",
        "log_requests": True,
        "log_responses": False,
        "credential_storage": "encrypted",
    }
    return load_json(CONFIG_FILE, defaults)


def generate_id(items: list) -> int:
    """Generate next ID."""
    return max((i.get("id", 0) for i in items), default=0) + 1


# ─── API Simulation ───────────────────────────────────────────────────────────
def call_api(integration: dict, endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Simulate an API call (in production, would use requests library)."""
    import random
    
    integration_name = integration.get("name", "Unknown")
    base_url = integration.get("base_url", "")
    
    log.info(f"API Call: {method} {base_url}{endpoint}")
    
    # Simulate API response
    start_time = datetime.utcnow()
    success = random.random() > 0.1  # 90% success rate
    
    response_time_ms = random.randint(50, 500)
    
    if success:
        response = {
            "status_code": 200 if method == "GET" else 201,
            "headers": {"Content-Type": "application/json"},
            "body": {
                "success": True,
                "data": {"result": "sample_data", "endpoint": endpoint},
                "timestamp": datetime.utcnow().isoformat(),
            },
            "response_time_ms": response_time_ms,
        }
    else:
        errors = ["Rate limit exceeded", "Unauthorized", "Server error", "Timeout"]
        response = {
            "status_code": random.choice([429, 401, 500, 504]),
            "headers": {"Content-Type": "application/json"},
            "body": {
                "error": random.choice(errors),
                "timestamp": datetime.utcnow().isoformat(),
            },
            "response_time_ms": response_time_ms,
        }
    
    return {
        "success": success,
        "integration_id": integration.get("id"),
        "integration_name": integration_name,
        "endpoint": endpoint,
        "method": method,
        "status_code": response["status_code"],
        "response_time_ms": response_time_ms,
        "response": response,
        "called_at": start_time.isoformat(),
    }


# ─── Commands ─────────────────────────────────────────────────────────────────
def cmd_list(args) -> None:
    """List all integrations."""
    data = load_integrations()
    integrations = data.get("integrations", [])
    
    if not integrations:
        print("🔗 No integrations configured.")
        return
    
    type_filter = args.type
    status_filter = args.status
    
    filtered = integrations
    if type_filter:
        filtered = [i for i in filtered if i.get("type") == type_filter]
    if status_filter:
        filtered = [i for i in filtered if i.get("status") == status_filter]
    
    print(f"🔗 API Integrations ({len(filtered)} of {len(integrations)}):")
    print("-" * 70)
    
    for i in sorted(filtered, key=lambda x: x.get("name", "")):
        status_icon = {"active": "🟢", "inactive": "🔴", "error": "⚠️"}.get(i.get("status", "unknown"), "⚪")
        last_call = i.get("last_call", "Never")
        if last_call:
            last_call = last_call[:10]
        print(f"  #{i['id']} | {status_icon} {i['name']:20} | {i['type']:10} | {i['service']:10} | Last: {last_call}")


def cmd_add(args) -> None:
    """Add a new API integration."""
    data = load_integrations()
    
    integration = {
        "id": generate_id(data.get("integrations", [])),
        "name": args.name,
        "service": args.service,
        "type": args.type,
        "status": "active",
        "base_url": args.base_url,
        "endpoints": [],
        "rate_limit": args.rate_limit or 100,
        "last_call": None,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    data["integrations"].append(integration)
    save_integrations(data)
    
    print(f"✅ Added integration #{integration['id']}: {integration['name']}")
    print(f"   Service: {integration['service']}")
    print(f"   Type: {integration['type']}")
    print(f"   Base URL: {integration['base_url']}")


def cmd_view(args) -> None:
    """View integration details."""
    data = load_integrations()
    for i in data.get("integrations", []):
        if i["id"] == args.id:
            print(f"\n🔗 Integration #{i['id']}: {i['name']}")
            print("=" * 60)
            print(f"Service:     {i.get('service', 'N/A')}")
            print(f"Type:        {i.get('type', 'N/A')}")
            print(f"Status:      {i.get('status', 'N/A')}")
            print(f"Base URL:    {i.get('base_url', 'N/A')}")
            print(f"Rate Limit:  {i.get('rate_limit', 'N/A')} req/min")
            print(f"Created:    {i.get('created_at', 'N/A')}")
            print(f"Last Call:  {i.get('last_call', 'N/A')}")
            
            if i.get("endpoints"):
                print(f"\nEndpoints:")
                for ep in i["endpoints"]:
                    print(f"  • {ep}")
            
            # Show credentials
            creds_data = load_credentials()
            creds = [c for c in creds_data.get("credentials", []) if c.get("integration_id") == i["id"]]
            if creds:
                print(f"\nCredentials ({len(creds)}):")
                for c in creds:
                    print(f"  • {c.get('name')} ({c.get('type')})")
            return
    
    print(f"❌ Integration #{args.id} not found.")


def cmd_update(args) -> None:
    """Update integration properties."""
    data = load_integrations()
    
    for i in data.get("integrations", []):
        if i["id"] == args.id:
            if args.name:
                i["name"] = args.name
            if args.base_url:
                i["base_url"] = args.base_url
            if args.rate_limit:
                i["rate_limit"] = args.rate_limit
            if args.status:
                i["status"] = args.status
            
            save_integrations(data)
            print(f"✅ Updated integration #{args.id}")
            return
    
    print(f"❌ Integration #{args.id} not found.")


def cmd_delete(args) -> None:
    """Delete an integration."""
    data = load_integrations()
    original_len = len(data.get("integrations", []))
    data["integrations"] = [i for i in data["integrations"] if i["id"] != args.id]
    
    if len(data["integrations"]) < original_len:
        save_integrations(data)
        # Also delete related credentials
        creds_data = load_credentials()
        creds_data["credentials"] = [c for c in creds_data["credentials"] if c.get("integration_id") != args.id]
        save_credentials(creds_data)
        print(f"✅ Deleted integration #{args.id}")
    else:
        print(f"❌ Integration #{args.id} not found.")


def cmd_call(args) -> None:
    """Make an API call to an integration."""
    integrations_data = load_integrations()
    integration = None
    
    for i in integrations_data.get("integrations", []):
        if i["id"] == args.integration_id:
            integration = i
            break
    
    if not integration:
        print(f"❌ Integration #{args.integration_id} not found.")
        return
    
    if integration.get("status") != "active":
        print(f"⚠️ Integration is not active.")
        return
    
    log.info(f"Calling API: {integration['name']} {args.endpoint}")
    print(f"🔄 {args.method} {integration['base_url']}{args.endpoint}")
    
    result = call_api(integration, args.endpoint, args.method)
    
    # Save request
    requests_data = load_requests()
    requests_data["requests"].append(result)
    save_requests(requests_data)
    
    # Update integration last_call
    for i in integrations_data.get("integrations", []):
        if i["id"] == integration["id"]:
            i["last_call"] = datetime.utcnow().isoformat()
            break
    save_integrations(integrations_data)
    
    # Print result
    if result["success"]:
        print(f"✅ Success ({result['status_code']}) - {result['response_time_ms']}ms")
        if args.verbose and result.get("response", {}).get("body"):
            print(f"\nResponse:\n{json.dumps(result['response']['body'], indent=2)[:500]}")
    else:
        print(f"❌ Failed ({result['status_code']}) - {result['response_time_ms']}ms")
        if result.get("response", {}).get("body", {}).get("error"):
            print(f"   Error: {result['response']['body']['error']}")


def cmd_credentials(args) -> None:
    """List credentials for an integration."""
    creds_data = load_credentials()
    integrations_data = load_integrations()
    
    if args.integration_id:
        creds = [c for c in creds_data.get("credentials", []) if c.get("integration_id") == args.integration_id]
        if not creds:
            print(f"No credentials found for integration #{args.integration_id}")
    else:
        creds = creds_data.get("credentials", [])
    
    if not creds:
        print("🔐 No credentials stored.")
        return
    
    print(f"🔐 Credentials ({len(creds)}):")
    print("-" * 70)
    
    for c in creds:
        integration_name = "unknown"
        for i in integrations_data.get("integrations", []):
            if i["id"] == c.get("integration_id"):
                integration_name = i.get("name", "unknown")
                break
        
        last_used = c.get("last_used", "Never")
        if last_used:
            last_used = last_used[:10]
        
        # Mask actual credential value
        print(f"  #{c['id']} | {c['name']:20} | {integration_name:20} | {c.get('type')}: **** | Used: {last_used}")


def cmd_credential_add(args) -> None:
    """Add a credential to an integration."""
    integrations_data = load_integrations()
    
    # Verify integration exists
    integration_exists = any(i["id"] == args.integration_id for i in integrations_data.get("integrations", []))
    if not integration_exists:
        print(f"❌ Integration #{args.integration_id} not found.")
        return
    
    creds_data = load_credentials()
    
    credential = {
        "id": generate_id(creds_data.get("credentials", [])),
        "integration_id": args.integration_id,
        "name": args.name,
        "type": args.type,
        "last_used": None,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    creds_data["credentials"].append(credential)
    save_credentials(creds_data)
    
    print(f"✅ Added credential #{credential['id']}: {credential['name']}")
    print(f"   Type: {credential['type']}")
    print(f"   Integration ID: {credential['integration_id']}")


def cmd_credential_delete(args) -> None:
    """Delete a credential."""
    creds_data = load_credentials()
    original_len = len(creds_data.get("credentials", []))
    creds_data["credentials"] = [c for c in creds_data["credentials"] if c["id"] != args.id]
    
    if len(creds_data["credentials"]) < original_len:
        save_credentials(creds_data)
        print(f"✅ Deleted credential #{args.id}")
    else:
        print(f"❌ Credential #{args.id} not found.")


def cmd_endpoints(args) -> None:
    """List known endpoints for an integration."""
    data = load_integrations()
    
    for i in data.get("integrations", []):
        if i["id"] == args.id:
            endpoints = i.get("endpoints", [])
            if not endpoints:
                print(f"No known endpoints for {i['name']}")
            else:
                print(f"📡 Endpoints for {i['name']} ({len(endpoints)}):")
                for ep in endpoints:
                    print(f"  • {ep}")
            return
    
    print(f"❌ Integration #{args.id} not found.")


def cmd_endpoint_add(args) -> None:
    """Add an endpoint to an integration."""
    data = load_integrations()
    
    for i in data.get("integrations", []):
        if i["id"] == args.id:
            if "endpoints" not in i:
                i["endpoints"] = []
            
            if args.endpoint not in i["endpoints"]:
                i["endpoints"].append(args.endpoint)
                save_integrations(data)
                print(f"✅ Added endpoint to integration #{args.id}: {args.endpoint}")
            else:
                print(f"⚠️ Endpoint already exists: {args.endpoint}")
            return
    
    print(f"❌ Integration #{args.id} not found.")


def cmd_history(args) -> None:
    """Show API request history."""
    data = load_requests()
    requests = data.get("requests", [])
    
    if not requests:
        print("📜 No API requests recorded.")
        return
    
    integration_filter = args.integration_id
    if integration_filter:
        requests = [r for r in requests if r.get("integration_id") == integration_filter]
    
    limit = args.limit
    filtered = requests[-limit:] if limit else requests
    
    print(f"📜 API Request History ({len(filtered)} recent):")
    print("-" * 70)
    
    for r in sorted(filtered, key=lambda x: x.get("called_at", ""), reverse=True):
        status = "✅" if r.get("success") else "❌"
        print(f"  #{r.get('id', '?')} | {status} | {r.get('method'):6} | {r.get('integration_name', 'unknown')[:15]:15} | {r.get('endpoint', '')[:25]}")
        print(f"        {r.get('status_code')} | {r.get('response_time_ms', 0)}ms | {r.get('called_at', '')[:19]}")


def cmd_stats(args) -> None:
    """Show API integration statistics."""
    integrations_data = load_integrations()
    requests_data = load_requests()
    
    integrations = integrations_data.get("integrations", [])
    requests = requests_data.get("requests", [])
    
    active = sum(1 for i in integrations if i.get("status") == "active")
    total_calls = len(requests)
    successful_calls = sum(1 for r in requests if r.get("success"))
    
    # Count by integration
    by_integration = {}
    for r in requests:
        name = r.get("integration_name", "unknown")
        by_integration[name] = by_integration.get(name, 0) + 1
    
    print("\n📊 API Integration Statistics")
    print("=" * 50)
    print(f"Total Integrations: {len(integrations)}")
    print(f"Active Integrations: {active}")
    print(f"\nTotal API Calls: {total_calls}")
    print(f"Successful Calls: {successful_calls}")
    print(f"Failed Calls: {total_calls - successful_calls}")
    print(f"Success Rate: {(successful_calls/total_calls*100) if total_calls > 0 else 0:.1f}%")
    
    if by_integration:
        print("\nCalls by Integration:")
        for name, count in sorted(by_integration.items(), key=lambda x: x[1], reverse=True):
            print(f"  {name}: {count}")


def cmd_test(args) -> None:
    """Test an integration by making a test API call."""
    integrations_data = load_integrations()
    integration = None
    
    for i in integrations_data.get("integrations", []):
        if i["id"] == args.id:
            integration = i
            break
    
    if not integration:
        print(f"❌ Integration #{args.id} not found.")
        return
    
    print(f"🧪 Testing integration: {integration['name']}")
    print(f"   Base URL: {integration['base_url']}")
    print(f"   Status: {integration['status']}")
    
    # Make test call
    test_endpoint = args.endpoint or "/health"
    result = call_api(integration, test_endpoint, "GET")
    
    requests_data = load_requests()
    requests_data["requests"].append(result)
    save_requests(requests_data)
    
    if result["success"]:
        print(f"\n✅ Test successful!")
        print(f"   Status: {result['status_code']}")
        print(f"   Response time: {result['response_time_ms']}ms")
    else:
        print(f"\n❌ Test failed!")
        print(f"   Status: {result['status_code']}")
        print(f"   Error: {result.get('response', {}).get('body', {}).get('error', 'Unknown')}")


def cmd_config(args) -> None:
    """Show configuration."""
    config = load_config()
    print("\n⚙️ API Integrations Config")
    print("=" * 50)
    for key, value in config.items():
        print(f"  {key}: {value}")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="API Integrations Agent - Productivity Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list
  %(prog)s list --type payment
  %(prog)s add --name "My API" --service myapi --type custom --base-url "https://api.example.com"
  %(prog)s view --id 1
  %(prog)s update --id 1 --name "New Name" --rate-limit 200
  %(prog)s delete --id 1
  %(prog)s call --integration-id 1 --endpoint "/users" --method GET
  %(prog)s call --integration-id 1 --endpoint "/orders" --method POST --verbose
  %(prog)s credentials
  %(prog)s credentials --integration-id 1
  %(prog)s credential-add --integration-id 1 --name "API Key" --type api_key
  %(prog)s credential-delete --id 1
  %(prog)s endpoints --id 1
  %(prog)s endpoint-add --id 1 --endpoint "/products"
  %(prog)s history
  %(prog)s history --integration-id 1 --limit 20
  %(prog)s stats
  %(prog)s test --id 1
  %(prog)s test --id 1 --endpoint "/status"
  %(prog)s config
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List
    p_list = subparsers.add_parser("list", help="List integrations")
    p_list.add_argument("--type", "-t", default=None, help="Filter by type")
    p_list.add_argument("--status", "-s", default=None, help="Filter by status")
    
    # Add
    p_add = subparsers.add_parser("add", help="Add a new integration")
    p_add.add_argument("--name", "-n", required=True, help="Integration name")
    p_add.add_argument("--service", "-s", required=True, help="Service identifier")
    p_add.add_argument("--type", "-t", required=True, help="Integration type")
    p_add.add_argument("--base-url", "-u", required=True, help="Base API URL")
    p_add.add_argument("--rate-limit", "-r", type=int, default=None, help="Rate limit (req/min)")
    
    # View
    p_view = subparsers.add_parser("view", help="View integration details")
    p_view.add_argument("--id", "-i", type=int, required=True, help="Integration ID")
    
    # Update
    p_update = subparsers.add_parser("update", help="Update integration")
    p_update.add_argument("--id", "-i", type=int, required=True, help="Integration ID")
    p_update.add_argument("--name", "-n", default=None, help="New name")
    p_update.add_argument("--base-url", "-u", default=None, help="New base URL")
    p_update.add_argument("--rate-limit", "-r", type=int, default=None, help="New rate limit")
    p_update.add_argument("--status", "-s", default=None, help="New status")
    
    # Delete
    p_delete = subparsers.add_parser("delete", help="Delete an integration")
    p_delete.add_argument("--id", "-i", type=int, required=True, help="Integration ID")
    
    # Call
    p_call = subparsers.add_parser("call", help="Make an API call")
    p_call.add_argument("--integration-id", "-i", type=int, required=True, help="Integration ID")
    p_call.add_argument("--endpoint", "-e", required=True, help="API endpoint")
    p_call.add_argument("--method", "-m", default="GET", choices=["GET", "POST", "PUT", "DELETE", "PATCH"],
                        help="HTTP method")
    p_call.add_argument("--verbose", "-v", action="store_true", help="Show full response")
    
    # Credentials
    p_creds = subparsers.add_parser("credentials", help="List credentials")
    p_creds.add_argument("--integration-id", "-i", type=int, default=None, help="Filter by integration")
    
    # Credential Add
    p_cred_add = subparsers.add_parser("credential-add", help="Add a credential")
    p_cred_add.add_argument("--integration-id", "-i", type=int, required=True, help="Integration ID")
    p_cred_add.add_argument("--name", "-n", required=True, help="Credential name")
    p_cred_add.add_argument("--type", "-t", required=True, help="Credential type")
    
    # Credential Delete
    p_cred_del = subparsers.add_parser("credential-delete", help="Delete a credential")
    p_cred_del.add_argument("--id", "-i", type=int, required=True, help="Credential ID")
    
    # Endpoints
    p_endpoints = subparsers.add_parser("endpoints", help="List integration endpoints")
    p_endpoints.add_argument("--id", "-i", type=int, required=True, help="Integration ID")
    
    # Endpoint Add
    p_ep_add = subparsers.add_parser("endpoint-add", help="Add an endpoint")
    p_ep_add.add_argument("--id", "-i", type=int, required=True, help="Integration ID")
    p_ep_add.add_argument("--endpoint", "-e", required=True, help="Endpoint path")
    
    # History
    p_history = subparsers.add_parser("history", help="Show API request history")
    p_history.add_argument("--integration-id", "-i", type=int, default=None, help="Filter by integration")
    p_history.add_argument("--limit", "-l", type=int, default=None, help="Limit results")
    
    # Stats
    subparsers.add_parser("stats", help="Show statistics")
    
    # Test
    p_test = subparsers.add_parser("test", help="Test an integration")
    p_test.add_argument("--id", "-i", type=int, required=True, help="Integration ID")
    p_test.add_argument("--endpoint", "-e", default=None, help="Test endpoint")
    
    # Config
    subparsers.add_parser("config", help="Show configuration")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "list":
            cmd_list(args)
        elif args.command == "add":
            cmd_add(args)
        elif args.command == "view":
            cmd_view(args)
        elif args.command == "update":
            cmd_update(args)
        elif args.command == "delete":
            cmd_delete(args)
        elif args.command == "call":
            cmd_call(args)
        elif args.command == "credentials":
            cmd_credentials(args)
        elif args.command == "credential-add":
            cmd_credential_add(args)
        elif args.command == "credential-delete":
            cmd_credential_delete(args)
        elif args.command == "endpoints":
            cmd_endpoints(args)
        elif args.command == "endpoint-add":
            cmd_endpoint_add(args)
        elif args.command == "history":
            cmd_history(args)
        elif args.command == "stats":
            cmd_stats(args)
        elif args.command == "test":
            cmd_test(args)
        elif args.command == "config":
            cmd_config(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
