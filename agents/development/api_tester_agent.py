#!/usr/bin/env python3
"""
API Tester Agent - OpenClaw Development Suite
Tests REST APIs, stores test results, monitors uptime.
Reads/Writes: /home/clawbot/.openclaw/workspace/data/api_tests/api_tests.json
             /home/clawbot/.openclaw/workspace/data/api_tests/results.json
"""

import argparse
import json
import logging
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "api_tests"
DATA_FILE = DATA_DIR / "api_tests.json"
RESULTS_FILE = DATA_DIR / "results.json"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "api_tester.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("APITester")


def load_apis() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        initial = {"apis": [], "last_updated": datetime.utcnow().isoformat()}
        save_apis(initial)
        return initial
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load apis: {e}")
        return {"apis": [], "last_updated": datetime.utcnow().isoformat()}


def save_apis(data: dict) -> None:
    data["last_updated"] = datetime.utcnow().isoformat()
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        log.error(f"Failed to save apis: {e}")
        raise


def load_results() -> dict:
    if not RESULTS_FILE.exists():
        return {"results": [], "last_updated": datetime.utcnow().isoformat()}
    try:
        with open(RESULTS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"results": [], "last_updated": datetime.utcnow().isoformat()}


def save_results(data: dict) -> None:
    data["last_updated"] = datetime.utcnow().isoformat()
    try:
        with open(RESULTS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        log.error(f"Failed to save results: {e}")


def generate_id(apis: list) -> int:
    return max((a.get("id", 0) for a in apis), default=0) + 1


def do_request(method: str, url: str, headers: dict = None, body: str = None, timeout: int = 10) -> tuple:
    """Perform HTTP request and return (success, status_code, response_body, elapsed_ms, error)."""
    start = time.time()
    headers = headers or {}
    req = urllib.request.Request(url, method=method, headers=headers)
    if body:
        req.data = body.encode("utf-8")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed_ms = int((time.time() - start) * 1000)
            status = resp.getcode()
            try:
                body_out = resp.read().decode("utf-8")
            except Exception:
                body_out = ""
            return (200 <= status < 300, status, body_out[:5000], elapsed_ms, None)
    except urllib.error.HTTPError as e:
        elapsed_ms = int((time.time() - start) * 1000)
        try:
            err_body = e.read().decode("utf-8")[:2000]
        except Exception:
            err_body = str(e)
        return (False, e.code, err_body, elapsed_ms, str(e))
    except urllib.error.URLError as e:
        elapsed_ms = int((time.time() - start) * 1000)
        return (False, 0, "", elapsed_ms, str(e.reason))
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        return (False, 0, "", elapsed_ms, str(e))


def parse_headers(header_str: str) -> dict:
    headers = {}
    for line in header_str.strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip()] = v.strip()
    return headers


def cmd_add(args) -> None:
    """Add a new API endpoint."""
    apis_data = load_apis()
    headers = parse_headers(args.headers) if args.headers else {}
    api = {
        "id": generate_id(apis_data["apis"]),
        "name": args.name,
        "url": args.url,
        "method": args.method.upper(),
        "headers": headers,
        "body": args.body or "",
        "expected_status": args.expected_status,
        "description": args.description or "",
        "project": args.project or "general",
        "created_at": datetime.utcnow().isoformat(),
        "last_tested": None,
        "enabled": True,
    }
    apis_data["apis"].append(api)
    save_apis(apis_data)
    log.info(f"API added: #{api['id']} - {api['name']}")
    print(f"🔌 API #{api['id']} added: {api['name']} ({api['method']} {api['url']})")


def cmd_list(args) -> None:
    """List all API endpoints."""
    apis_data = load_apis()
    apis = apis_data["apis"]
    if args.project:
        apis = [a for a in apis if a.get("project") == args.project]
    if not apis:
        print("🔌 No APIs found.")
        return
    print(f"\n🔌 API Endpoints ({len(apis)} found)\n{'─'*70}")
    for a in apis:
        status_icon = "🟢 enabled" if a.get("enabled") else "🔴 disabled"
        last = a.get("last_tested", "Never")
        print(f"  #{a['id']:3d} {status_icon} | {a['method']:6s} | {a['name']}")
        print(f"       URL: {a['url'][:60]}")
        print(f"       Project: {a.get('project')} | Last tested: {last}")
    print()


def cmd_test(args) -> None:
    """Test a single API or all APIs."""
    apis_data = load_apis()
    results_data = load_results()

    targets = []
    if args.all:
        targets = [(a, None) for a in apis_data["apis"] if a.get("enabled")]
    else:
        for a in apis_data["apis"]:
            if a["id"] == args.api_id:
                targets = [(a, None)]
                break
        if not targets:
            print(f"❌ API #{args.api_id} not found.")
            return

    passed = 0
    failed = 0
    for api, _ in targets:
        method = api.get("method", "GET")
        url = api.get("url")
        headers = api.get("headers", {})
        body = api.get("body", "") or None
        expected = api.get("expected_status", 200)

        success, status, response, elapsed, error = do_request(method, url, headers, body, args.timeout)

        # Check status match
        status_ok = status == expected
        overall = success and status_ok

        result = {
            "id": len(results_data["results"]) + 1,
            "api_id": api["id"],
            "api_name": api["name"],
            "url": url,
            "method": method,
            "status_code": status,
            "expected_status": expected,
            "success": overall,
            "response_time_ms": elapsed,
            "response_preview": response[:500],
            "error": error,
            "tested_at": datetime.utcnow().isoformat(),
        }
        results_data["results"].append(result)

        # Update last_tested
        for a in apis_data["apis"]:
            if a["id"] == api["id"]:
                a["last_tested"] = datetime.utcnow().isoformat()
                break

        if overall:
            passed += 1
            icon = "✅"
        else:
            failed += 1
            icon = "❌"

        print(f"  {icon} #{api['id']} {method} {url[:55]} | {status} | {elapsed}ms")

        save_apis(apis_data)
        save_results(results_data)

    log.info(f"Test completed: {passed} passed, {failed} failed")
    print(f"\n📊 Results: {passed} ✅ | {failed} ❌")


def cmd_results(args) -> None:
    """Show recent test results."""
    results_data = load_results()
    results = results_data.get("results", [])
    if not results:
        print("📋 No test results yet.")
        return
    # Show last N results
    recent = results[-min(args.last, len(results)):]
    recent.reverse()
    print(f"\n📋 Recent Test Results ({len(recent)} of {len(results)})\n{'─'*70}")
    for r in recent:
        icon = "✅" if r.get("success") else "❌"
        elapsed = r.get("response_time_ms", 0)
        status = r.get("status_code", 0)
        print(f"  {icon} #{r['id']:4d} [{r['method']:6s}] {r.get('api_name','?')[:30]}")
        print(f"       URL: {r.get('url','')[:60]} | Status: {status} | Time: {elapsed}ms")
        print(f"       At: {r.get('tested_at','')[:19]}")
        if r.get("error"):
            print(f"       Error: {r['error'][:80]}")
    print()


def cmd_delete(args) -> None:
    """Delete an API endpoint."""
    apis_data = load_apis()
    original = len(apis_data["apis"])
    apis_data["apis"] = [a for a in apis_data["apis"] if a["id"] != args.api_id]
    if len(apis_data["apis"]) < original:
        save_apis(apis_data)
        log.info(f"API #{args.api_id} deleted")
        print(f"🗑️  API #{args.api_id} deleted.")
    else:
        print(f"❌ API #{args.api_id} not found.")


def cmd_health(args) -> None:
    """Show API health summary."""
    apis_data = load_apis()
    results_data = load_results()
    results = results_data.get("results", [])
    if not results:
        print("📋 No test results yet. Run 'api-tester test --all' first.")
        return

    print(f"\n💚 API Health Summary\n{'─'*50}")
    for api in apis_data:
        if not api.get("enabled"):
            continue
        api_results = [r for r in results if r.get("api_id") == api["id"]]
        if not api_results:
            print(f"  #{api['id']:3d} {api['name'][:30]:<30} ⚪ No tests yet")
            continue
        recent = api_results[-args.last:]
        success_rate = sum(1 for r in recent if r.get("success")) / len(recent) * 100
        avg_time = sum(r.get("response_time_ms", 0) for r in recent) / len(recent)
        status_icon = "🟢" if success_rate >= 80 else "🟡" if success_rate >= 50 else "🔴"
        print(f"  {status_icon} #{api['id']:3d} {api['name'][:30]:<30} {success_rate:5.1f}% | avg {avg_time:.0f}ms | {api['method']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="api-tester",
        description="🔌 API Tester Agent — test REST endpoints, monitor uptime",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  api-tester add "Health Check" --url https://api.example.com/health --method GET --expected-status 200
  api-tester add "Create User" --url https://api.example.com/users --method POST --body '{"name":"test"}'
  api-tester list --project myapp
  api-tester test 3 --timeout 15
  api-tester test --all
  api-tester results --last 20
  api-tester health
  api-tester delete 2
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add an API endpoint")
    p_add.add_argument("name", help="API name")
    p_add.add_argument("--url", required=True, help="Full URL")
    p_add.add_argument("--method", default="GET", choices=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
    p_add.add_argument("--headers", default="", help="Headers as 'Key: Value' lines")
    p_add.add_argument("--body", default="", help="Request body")
    p_add.add_argument("--expected-status", type=int, default=200, help="Expected HTTP status code")
    p_add.add_argument("-d", "--description", default="", help="Description")
    p_add.add_argument("-p", "--project", default="general", help="Project name")

    p_list = sub.add_parser("list", help="List API endpoints")
    p_list.add_argument("--project", help="Filter by project")

    p_test = sub.add_parser("test", help="Test an API")
    p_test.add_argument("api_id", nargs="?", type=int, help="API ID to test")
    p_test.add_argument("--all", action="store_true", help="Test all enabled APIs")
    p_test.add_argument("--timeout", type=int, default=10, help="Timeout in seconds")

    p_results = sub.add_parser("results", help="Show test results")
    p_results.add_argument("--last", type=int, default=20, help="Number of recent results to show")

    p_del = sub.add_parser("delete", help="Delete an API endpoint")
    p_del.add_argument("api_id", type=int, help="API ID to delete")

    p_health = sub.add_parser("health", help="Show API health summary")
    p_health.add_argument("--last", type=int, default=10, help="Number of recent tests per API")

    args = parser.parse_args()
    try:
        if args.command == "add":
            cmd_add(args)
        elif args.command == "list":
            cmd_list(args)
        elif args.command == "test":
            cmd_test(args)
        elif args.command == "results":
            cmd_results(args)
        elif args.command == "delete":
            cmd_delete(args)
        elif args.command == "health":
            cmd_health(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
