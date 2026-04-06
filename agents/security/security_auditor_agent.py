#!/usr/bin/env python3
"""
🔍 Security Auditor Agent
Comprehensive security audits for systems, configurations, and infrastructure.
"""

import argparse
import json
import logging
import os
import sys
import datetime
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "security_auditor.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SecurityAuditor")

# Data directory
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/security")
DATA_DIR.mkdir(parents=True, exist_ok=True)

AUDIT_REPORTS_FILE = DATA_DIR / "audit_reports.json"
SYSTEM_INFO_FILE = DATA_DIR / "system_info.json"


class SecurityAuditor:
    """Comprehensive security auditing capabilities."""

    def __init__(self):
        self.audit_results = {
            "audit_id": self._generate_audit_id(),
            "timestamp": datetime.datetime.now().isoformat(),
            "system_checks": {},
            "file_checks": [],
            "config_checks": [],
            "overall_score": 0,
            "recommendations": []
        }
        self.score_breakdown = defaultdict(int)

    def _generate_audit_id(self) -> str:
        """Generate unique audit ID."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"audit_{timestamp}"

    def _save_audit(self):
        """Save audit report."""
        try:
            data = {"audits": []}
            if AUDIT_REPORTS_FILE.exists():
                with open(AUDIT_REPORTS_FILE, 'r') as f:
                    data = json.load(f)
            
            data["audits"].append(self.audit_results)
            data["audits"] = data["audits"][-50:]  # Keep last 50
            
            with open(AUDIT_REPORTS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Audit saved: {self.audit_results['audit_id']}")
        except Exception as e:
            logger.error(f"Failed to save audit: {e}")

    def audit_system_info(self) -> Dict:
        """Gather and audit basic system information."""
        logger.info("Auditing system information...")
        
        info = {
            "os": os.name,
            "platform": sys.platform,
            "hostname": socket.gethostname() if hasattr(socket, 'gethostname') else "unknown",
            "user": os.getenv("USER") or os.getenv("USERNAME") or "unknown",
            "home": os.path.expanduser("~"),
            "python_version": sys.version
        }
        
        self.audit_results["system_checks"]["system_info"] = info
        
        # Check for security-relevant info
        checks = []
        
        # Check if running as root
        if os.geteuid() == 0:
            checks.append({
                "check": "root_user",
                "status": "WARNING",
                "message": "Running as root user - increased risk if compromised"
            })
            self.score_breakdown["root"] = -10
        else:
            checks.append({
                "check": "root_user",
                "status": "OK",
                "message": "Not running as root"
            })
        
        # Check home directory permissions
        home = info["home"]
        try:
            stat_info = os.stat(home)
            mode = oct(stat_info.st_mode)[-3:]
            if mode != "700":
                checks.append({
                    "check": "home_permissions",
                    "status": "WARNING",
                    "message": f"Home directory has permissions {mode}, should be 700"
                })
                self.score_breakdown["permissions"] -= 5
            else:
                checks.append({
                    "check": "home_permissions",
                    "status": "OK",
                    "message": "Home directory permissions are secure"
                })
        except Exception as e:
            logger.warning(f"Could not check home permissions: {e}")
        
        self.audit_results["system_checks"]["security_checks"] = checks
        return info

    def audit_sensitive_files(self, path: str = None) -> List[Dict]:
        """Audit sensitive files for permissions and exposure."""
        logger.info("Auditing sensitive files...")
        
        sensitive_patterns = [
            ".env", ".pem", ".key", ".p12", ".jks",
            "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
            ".aws/credentials", ".docker/config.json"
        ]
        
        results = []
        
        def check_file(filepath):
            try:
                if not os.path.exists(filepath):
                    return None
                
                stat_info = os.stat(filepath)
                mode = stat_info.st_mode
                perms = oct(mode)[-3:]
                
                is_sensitive = any(pattern in str(filepath) for pattern in sensitive_patterns)
                
                result = {
                    "path": filepath,
                    "permissions": perms,
                    "size": stat_info.st_size,
                    "modified": datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    "is_sensitive": is_sensitive,
                    "issues": []
                }
                
                # Check world-readable
                if mode & 0o004:
                    result["issues"].append("World-readable")
                    if is_sensitive:
                        result["severity"] = "CRITICAL"
                        self.score_breakdown["sensitive_exposure"] -= 20
                    else:
                        result["severity"] = "WARNING"
                        self.score_breakdown["permissions"] -= 5
                
                # Check group-readable
                if mode & 0o040:
                    result["issues"].append("Group-readable")
                    if is_sensitive:
                        result["issues"].append("SENSITIVE - Group accessible")
                        result["severity"] = "HIGH"
                        self.score_breakdown["sensitive_exposure"] -= 15
                
                # Sensitive files should have strict permissions
                if is_sensitive and perms not in ["600", "400"]:
                    result["issues"].append(f"Sensitive file should be 600 or 400, is {perms}")
                    result["severity"] = "HIGH"
                    self.score_breakdown["sensitive_perms"] -= 10
                
                return result
            except Exception as e:
                logger.warning(f"Could not check {filepath}: {e}")
                return None
        
        # Check common sensitive locations
        paths_to_check = [
            os.path.expanduser("~/.ssh"),
            os.path.expanduser("~/.gnupg"),
            os.path.expanduser("~/.aws"),
            os.path.expanduser("~/.config"),
            path or os.path.expanduser("~")
        ]
        
        for base_path in paths_to_check:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    for f in files:
                        filepath = os.path.join(root, f)
                        result = check_file(filepath)
                        if result and (result["is_sensitive"] or result["issues"]):
                            results.append(result)
        
        self.audit_results["file_checks"] = results
        return results

    def audit_running_processes(self) -> List[Dict]:
        """Audit running processes for security concerns."""
        logger.info("Auditing running processes...")
        
        processes = []
        
        try:
            # Get process info
            for proc_dir in Path("/proc").iterdir():
                if not proc_dir.name.isdigit():
                    continue
                
                try:
                    pid = int(proc_dir.name)
                    cmdline_file = proc_dir / "cmdline"
                    
                    if cmdline_file.exists():
                        with open(cmdline_file, 'r') as f:
                            cmdline = f.read().replace('\x00', ' ').strip()
                        
                        if cmdline:
                            processes.append({
                                "pid": pid,
                                "command": cmdline[:100],
                                "issues": []
                            })
                except (PermissionError, FileNotFoundError, ProcessLookupError):
                    pass
        except Exception as e:
            logger.warning(f"Could not enumerate processes: {e}")
        
        # Check for suspicious processes
        suspicious_patterns = [
            ("nc ", "Netcat listener"),
            ("ncat", "Netcat variant"),
            ("/dev/tcp", "Raw socket"),
            ("msfvenom", "Metasploit payload"),
            ("john", "John the Ripper"),
            ("hashcat", "Hashcat"),
            ("hydra", "Hydra brute force")
        ]
        
        flagged = []
        for proc in processes:
            for pattern, desc in suspicious_patterns:
                if pattern in proc["command"]:
                    proc["issues"].append(f"Suspicious: {desc}")
                    flagged.append(proc)
        
        self.audit_results["system_checks"]["processes"] = {
            "total": len(processes),
            "suspicious": len(flagged),
            "flagged": flagged[:20]  # Limit to 20
        }
        
        return processes

    def audit_network_connections(self) -> Dict:
        """Audit network connections."""
        logger.info("Auditing network connections...")
        
        connections = {"listening": [], "established": [], "issues": []}
        
        try:
            result = subprocess.run(
                ["ss", "-tunap"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n')[1:]:
                    if 'LISTEN' in line:
                        connections["listening"].append(line.strip())
                    elif 'ESTAB' in line:
                        connections["established"].append(line.strip())
                        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Could not run ss command, trying netstat")
            try:
                result = subprocess.run(
                    ["netstat", "-tunap"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n')[2:]:
                        if 'LISTEN' in line:
                            connections["listening"].append(line.strip())
                        elif 'ESTAB' in line:
                            connections["established"].append(line.strip())
            except Exception as e:
                logger.warning(f"netstat also failed: {e}")
        
        # Check for suspicious listening ports
        suspicious_ports = {
            "4444": "Metasploit default",
            "5555": "Android ADB",
            "31337": "Back Orifice"
        }
        
        for conn in connections["listening"]:
            for port, desc in suspicious_ports.items():
                if f":{port}" in conn:
                    connections["issues"].append(f"Suspicious port {port}: {desc}")
        
        self.audit_results["system_checks"]["network"] = connections
        return connections

    def audit_cron_jobs(self) -> List[Dict]:
        """Audit cron jobs for security issues."""
        logger.info("Auditing cron jobs...")
        
        cron_jobs = []
        
        cron_locations = [
            "/etc/crontab",
            "/var/spool/cron",
            "/etc/cron.d",
            "/etc/cron.daily",
            "/etc/cron.hourly",
            "/etc/cron.weekly",
            "/etc/cron.monthly",
            os.path.expanduser("~/crontab")
        ]
        
        for location in cron_locations:
            try:
                path = Path(location)
                if path.is_file():
                    with open(path, 'r') as f:
                        for i, line in enumerate(f, 1):
                            line = line.strip()
                            if line and not line.startswith("#"):
                                cron_jobs.append({
                                    "source": f"{location}:{i}",
                                    "job": line[:150],
                                    "issues": []
                                })
                                
                                # Check for issues
                                if "wget" in line or "curl" in line:
                                    cron_jobs[-1]["issues"].append("Downloads from network")
                                if "python" in line and "-m" not in line:
                                    cron_jobs[-1]["issues"].append("Python script execution")
                                if ">>" not in line and "2>" not in line:
                                    cron_jobs[-1]["issues"].append("No output logging")
                                
                elif path.is_dir():
                    for cron_file in path.iterdir():
                        if cron_file.is_file():
                            try:
                                with open(cron_file, 'r') as f:
                                    for i, line in enumerate(f, 1):
                                        line = line.strip()
                                        if line and not line.startswith("#"):
                                            cron_jobs.append({
                                                "source": f"{cron_file}:{i}",
                                                "job": line[:150],
                                                "issues": []
                                            })
                            except:
                                pass
            except PermissionError:
                logger.debug(f"No permission to read {location}")
            except Exception as e:
                logger.debug(f"Could not read {location}: {e}")
        
        self.audit_results["system_checks"]["cron_jobs"] = cron_jobs
        return cron_jobs

    def calculate_overall_score(self):
        """Calculate overall security score."""
        # Base score
        base_score = 100
        
        # Apply deductions
        deductions = {
            "root": -15 if os.geteuid() == 0 else 0,
            "sensitive_exposure": -25,
            "sensitive_perms": -15,
            "permissions": -10,
            "network": -10,
            "processes": -5
        }
        
        total_deduction = sum(self.score_breakdown.values())
        self.audit_results["overall_score"] = max(0, min(100, base_score + total_deduction))
        
        # Generate recommendations
        recommendations = []
        
        if self.audit_results["overall_score"] < 50:
            recommendations.append("🚨 CRITICAL: Security score is low. Immediate action required.")
        elif self.audit_results["overall_score"] < 75:
            recommendations.append("⚠️ WARNING: Security score needs improvement.")
        
        if os.geteuid() == 0:
            recommendations.append("• Avoid running services as root user")
        
        # Check file issues
        critical_files = [f for f in self.audit_results["file_checks"] 
                         if f.get("severity") == "CRITICAL"]
        if critical_files:
            recommendations.append(f"• {len(critical_files)} critical file(s) have insecure permissions")
        
        # Check network issues
        if self.audit_results["system_checks"].get("network", {}).get("issues"):
            recommendations.append("• Review suspicious network listeners")
        
        self.audit_results["recommendations"] = recommendations
        return self.audit_results["overall_score"]

    def generate_report(self) -> str:
        """Generate audit report."""
        self.calculate_overall_score()
        
        report = []
        report.append("=" * 60)
        report.append("🔍 SECURITY AUDIT REPORT")
        report.append("=" * 60)
        report.append(f"Audit ID: {self.audit_results['audit_id']}")
        report.append(f"Timestamp: {self.audit_results['timestamp']}")
        report.append(f"Overall Score: {self.audit_results['overall_score']}/100")
        report.append("")
        
        # System Info
        report.append("📋 SYSTEM INFORMATION:")
        sys_info = self.audit_results["system_checks"].get("system_info", {})
        for key, value in sys_info.items():
            if key not in ["security_checks"]:
                report.append(f"  {key}: {value}")
        report.append("")
        
        # Security Checks
        report.append("🔒 SECURITY CHECKS:")
        for check in self.audit_results["system_checks"].get("system_info", {}).get("security_checks", []):
            status_icon = "✅" if check["status"] == "OK" else "⚠️"
            report.append(f"  {status_icon} [{check['status']}] {check['check']}: {check['message']}")
        report.append("")
        
        # File Checks
        file_issues = [f for f in self.audit_results["file_checks"] if f.get("issues")]
        if file_issues:
            report.append(f"📁 SENSITIVE FILES ({len(file_issues)} issues):")
            for f in file_issues[:10]:
                sev = f.get("severity", "INFO")
                report.append(f"  [{sev}] {f['path']}")
                report.append(f"       Permissions: {f['permissions']}")
                for issue in f["issues"]:
                    report.append(f"       • {issue}")
            report.append("")
        
        # Network
        network = self.audit_results["system_checks"].get("network", {})
        if network.get("listening"):
            report.append(f"🌐 NETWORK LISTENING ({len(network['listening'])} ports):")
            for conn in network["listening"][:5]:
                report.append(f"  • {conn}")
            if len(network["listening"]) > 5:
                report.append(f"  ... and {len(network['listening']) - 5} more")
            report.append("")
        
        if network.get("issues"):
            report.append("⚠️ NETWORK ISSUES:")
            for issue in network["issues"]:
                report.append(f"  • {issue}")
            report.append("")
        
        # Recommendations
        if self.audit_results["recommendations"]:
            report.append("💡 RECOMMENDATIONS:")
            for rec in self.audit_results["recommendations"]:
                report.append(f"  {rec}")
            report.append("")
        
        report.append("=" * 60)
        return "\n".join(report)

    def run_full_audit(self) -> Dict:
        """Run comprehensive security audit."""
        logger.info("Starting comprehensive security audit...")
        
        print("🔍 Running Security Audit...\n")
        
        print("  📋 Gathering system information...")
        self.audit_system_info()
        
        print("  📁 Checking file permissions...")
        self.audit_sensitive_files()
        
        print("  🔄 Checking processes...")
        self.audit_running_processes()
        
        print("  🌐 Analyzing network connections...")
        self.audit_network_connections()
        
        print("  ⏰ Checking cron jobs...")
        self.audit_cron_jobs()
        
        self._save_audit()
        
        print("\n" + self.generate_report())
        
        return self.audit_results


def main():
    import socket  # For gethostname
    
    parser = argparse.ArgumentParser(
        description="🔍 Security Auditor Agent - Comprehensive security auditing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --audit
  %(prog)s --list-reports
  %(prog)s --report audit_20240315_120000
  %(prog)s --check-files /path/to/check
  
This tool performs security audits for authorized systems only.
        """
    )
    
    parser.add_argument("--audit", "-a", action="store_true", help="Run full security audit")
    parser.add_argument("--list-reports", "-l", action="store_true", help="List previous audit reports")
    parser.add_argument("--report", "-r", help="Show specific audit report")
    parser.add_argument("--check-files", help="Check specific path for sensitive files")
    parser.add_argument("--output", "-o", help="Output file for report (JSON)")
    
    args = parser.parse_args()

    auditor = SecurityAuditor()
    
    if args.check_files:
        print(f"🔍 Checking files in: {args.check_files}")
        results = auditor.audit_sensitive_files(args.check_files)
        print(f"\nFound {len(results)} files with issues")
        for r in results[:10]:
            print(f"  [{r.get('severity', 'INFO')}] {r['path']} - {r['permissions']}")
        sys.exit(0)
    
    if args.list_reports:
        try:
            with open(AUDIT_REPORTS_FILE, 'r') as f:
                data = json.load(f)
            print(f"\n📋 Found {len(data['audits'])} audit reports:\n")
            for audit in data["audits"][-10:]:
                print(f"  • {audit['audit_id']}")
                print(f"    Score: {audit['overall_score']}/100")
                print(f"    Time: {audit['timestamp']}")
                print()
        except FileNotFoundError:
            print("No audit reports found.")
        sys.exit(0)
    
    if args.report:
        try:
            with open(AUDIT_REPORTS_FILE, 'r') as f:
                data = json.load(f)
            for audit in data["audits"]:
                if audit["audit_id"] == args.report:
                    auditor.audit_results = audit
                    print(auditor.generate_report())
                    break
            else:
                print(f"Audit {args.report} not found.")
        except FileNotFoundError:
            print("No audit reports found.")
        sys.exit(0)
    
    if args.audit or not any(vars(args).values()):
        try:
            results = auditor.run_full_audit()
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\n📄 Report saved to {args.output}")
        except KeyboardInterrupt:
            print("\n⚠️  Audit interrupted")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Audit failed: {e}")
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
