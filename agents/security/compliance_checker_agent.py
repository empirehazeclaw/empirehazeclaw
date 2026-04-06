#!/usr/bin/env python3
"""
✅ Compliance Checker Agent
检查系统配置是否符合安全标准和合规要求 (GDPR, SOC2, ISO27001, NIST, 等)
"""

import argparse
import json
import logging
import os
import sys
import datetime
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "compliance_checker.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ComplianceChecker")

# Data directory
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/security")
DATA_DIR.mkdir(parents=True, exist_ok=True)

COMPLIANCE_REPORTS_FILE = DATA_DIR / "compliance_reports.json"
FRAMEWORKS_FILE = DATA_DIR / "frameworks.json"


class ComplianceChecker:
    """合规性检查工具。"""

    # 合规框架定义
    FRAMEWORKS = {
        "GDPR": {
            "name": "General Data Protection Regulation",
            "description": "EU data privacy regulation",
            "controls": [
                "encryption", "access_control", "data_retention", 
                "consent_management", "breach_notification", "privacy_by_design"
            ]
        },
        "SOC2": {
            "name": "SOC 2 Type II",
            "description": "Service Organization Control 2",
            "controls": [
                "security", "availability", "processing_integrity",
                "confidentiality", "privacy"
            ]
        },
        "ISO27001": {
            "name": "ISO/IEC 27001",
            "description": "Information Security Management",
            "controls": [
                "risk_assessment", "access_control", "cryptography",
                "physical_security", "operations_security", "communications_security"
            ]
        },
        "NIST": {
            "name": "NIST Cybersecurity Framework",
            "description": "US cybersecurity framework",
            "controls": [
                "identify", "protect", "detect", "respond", "recover"
            ]
        },
        "PCI-DSS": {
            "name": "Payment Card Industry Data Security Standard",
            "description": "Payment card security",
            "controls": [
                "firewall", "passwords", "data_protection", 
                "vulnerability_management", "monitoring", "testing"
            ]
        }
    }

    def __init__(self):
        self.compliance_report = {
            "report_id": self._generate_report_id(),
            "timestamp": datetime.datetime.now().isoformat(),
            "framework": None,
            "overall_score": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "warning_checks": 0,
            "checks": [],
            "recommendations": [],
            "executive_summary": ""
        }
        self._load_frameworks()

    def _generate_report_id(self) -> str:
        """Generate unique report ID."""
        return f"compliance_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _load_frameworks(self):
        """Load framework definitions."""
        try:
            if FRAMEWORKS_FILE.exists():
                with open(FRAMEWORKS_FILE, 'r') as f:
                    custom = json.load(f)
                    self.FRAMEWORKS.update(custom.get("custom_frameworks", {}))
        except Exception as e:
            logger.warning(f"Could not load custom frameworks: {e}")

    def _save_report(self):
        """Save compliance report."""
        try:
            data = {"reports": []}
            if COMPLIANCE_REPORTS_FILE.exists():
                with open(COMPLIANCE_REPORTS_FILE, 'r') as f:
                    data = json.load(f)
            
            data["reports"].append(self.compliance_report)
            data["reports"] = data["reports"][-50:]  # Keep last 50
            
            with open(COMPLIANCE_REPORTS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Compliance report saved: {self.compliance_report['report_id']}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

    def _add_check(self, check_id: str, name: str, description: str,
                  status: str, severity: str, remediation: str = "",
                  framework_section: str = ""):
        """Add a compliance check result."""
        check = {
            "id": check_id,
            "name": name,
            "description": description,
            "status": status,  # PASS, FAIL, WARNING, INFO
            "severity": severity,
            "remediation": remediation,
            "framework_section": framework_section
        }
        
        self.compliance_report["checks"].append(check)
        
        if status == "PASS":
            self.compliance_report["passed_checks"] += 1
        elif status == "FAIL":
            self.compliance_report["failed_checks"] += 1
        elif status == "WARNING":
            self.compliance_report["warning_checks"] += 1
        
        return check

    # ============ Security Checks ============

    def check_user_management(self):
        """Check user management compliance."""
        logger.info("Checking user management...")
        
        # Check for root account
        if os.geteuid() == 0:
            self._add_check(
                "UM-001",
                "Root Account Usage",
                "System is running as root user",
                "WARNING",
                "MEDIUM",
                "Use a privileged account with sudo instead of direct root login",
                "Access Control"
            )
        else:
            self._add_check(
                "UM-001",
                "Root Account Usage",
                "System is not running as root",
                "PASS",
                "LOW",
                "",
                "Access Control"
            )
        
        # Check password policy
        try:
            result = subprocess.run(
                ["grep", "^PASS_MAX_DAYS", "/etc/login.defs"],
                capture_output=True, text=True
            )
            if result.returncode == 0 and "90" in result.stdout:
                self._add_check(
                    "UM-002",
                    "Password Expiration",
                    "Password max days set to 90 or less",
                    "PASS",
                    "LOW",
                    "",
                    "Access Control"
                )
            else:
                self._add_check(
                    "UM-002",
                    "Password Expiration",
                    "Password max days not configured for 90 days",
                    "WARNING",
                    "MEDIUM",
                    "Set PASS_MAX_DAYS to 90 in /etc/login.defs",
                    "Access Control"
                )
        except:
            self._add_check(
                "UM-002",
                "Password Expiration",
                "Could not check password policy",
                "INFO",
                "LOW",
                "Verify password expiration settings manually",
                "Access Control"
            )
        
        # Check for empty passwords
        try:
            result = subprocess.run(
                ["awk", "-F:", '($2 == "") {print $1}', "/etc/shadow"],
                capture_output=True, text=True
            )
            if result.stdout.strip():
                self._add_check(
                    "UM-003",
                    "Empty Passwords",
                    f"Users with empty passwords: {result.stdout.strip()}",
                    "FAIL",
                    "CRITICAL",
                    "Set passwords for all accounts or lock them",
                    "Access Control"
                )
            else:
                self._add_check(
                    "UM-003",
                    "Empty Passwords",
                    "No users with empty passwords found",
                    "PASS",
                    "LOW",
                    "",
                    "Access Control"
                )
        except:
            pass

    def check_file_permissions(self):
        """Check file permissions compliance."""
        logger.info("Checking file permissions...")
        
        critical_files = [
            ("/etc/passwd", "644", "Password file world-readable"),
            ("/etc/shadow", "640", "Shadow file should be 640 or stricter"),
            ("/etc/group", "644", "Group file world-readable"),
            ("/etc/gshadow", "640", "Gshadow file should be 640"),
            ("~/.ssh", "700", "SSH directory should be 700"),
            ("~/.bashrc", "644", "Bashrc should not be world-writable"),
        ]
        
        for filepath, expected_perms, desc in critical_files:
            try:
                path = Path(filepath).expanduser()
                if path.exists():
                    mode = oct(os.stat(path).st_mode)[-3:]
                    
                    if mode == expected_perms:
                        self._add_check(
                            f"FP-{len(self.compliance_report['checks'])+1:03d}",
                            filepath,
                            f"Permissions correct: {mode}",
                            "PASS",
                            "LOW",
                            "",
                            "Operations Security"
                        )
                    else:
                        severity = "CRITICAL" if "shadow" in filepath else "HIGH"
                        self._add_check(
                            f"FP-{len(self.compliance_report['checks'])+1:03d}",
                            filepath,
                            f"Expected {expected_perms}, found {mode}: {desc}",
                            "FAIL",
                            severity,
                            f"Run: chmod {expected_perms} {filepath}",
                            "Operations Security"
                        )
                else:
                    self._add_check(
                        f"FP-{len(self.compliance_report['checks'])+1:03d}",
                        filepath,
                        "File does not exist",
                        "INFO",
                        "LOW",
                        "",
                        "Operations Security"
                    )
            except PermissionError:
                self._add_check(
                    f"FP-{len(self.compliance_report['checks'])+1:03d}",
                    filepath,
                    "Cannot access file",
                    "INFO",
                    "LOW",
                    "Check permissions manually",
                    "Operations Security"
                )
            except Exception as e:
                logger.debug(f"Could not check {filepath}: {e}")

    def check_network_security(self):
        """Check network security compliance."""
        logger.info("Checking network security...")
        
        # Check firewall status
        try:
            result = subprocess.run(
                ["iptables", "-L", "-n"],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                self._add_check(
                    "NET-001",
                    "iptables Firewall",
                    "iptables is configured",
                    "PASS",
                    "LOW",
                    "",
                    "Network Security"
                )
            else:
                self._add_check(
                    "NET-001",
                    "iptables Firewall",
                    "No iptables rules found or iptables not active",
                    "WARNING",
                    "MEDIUM",
                    "Configure firewall rules for production systems",
                    "Network Security"
                )
        except FileNotFoundError:
            # Try ufw
            try:
                result = subprocess.run(
                    ["ufw", "status"],
                    capture_output=True, text=True
                )
                if "active" in result.stdout.lower():
                    self._add_check(
                        "NET-001",
                        "UFW Firewall",
                        "UFW firewall is active",
                        "PASS",
                        "LOW",
                        "",
                        "Network Security"
                    )
                else:
                    self._add_check(
                        "NET-001",
                        "Firewall",
                        "No active firewall detected",
                        "WARNING",
                        "MEDIUM",
                        "Enable and configure firewall",
                        "Network Security"
                    )
            except:
                self._add_check(
                    "NET-001",
                    "Firewall",
                    "Could not check firewall status",
                    "INFO",
                    "LOW",
                    "Manually verify firewall is configured",
                    "Network Security"
                )
        
        # Check open ports
        try:
            result = subprocess.run(
                ["ss", "-tunap"],
                capture_output=True, text=True,
                timeout=5
            )
            
            listening_ports = []
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'LISTEN' in line:
                        listening_ports.append(line.strip())
            
            # Check for unnecessary services
            suspicious_ports = {
                "21": "FTP - use SFTP instead",
                "23": "Telnet - unencrypted, use SSH",
                "445": "SMB - potential attack vector"
            }
            
            open_suspicious = []
            for port, warning in suspicious_ports.items():
                for conn in listening_ports:
                    if f":{port}" in conn:
                        open_suspicious.append(f"{port}: {warning}")
            
            if open_suspicious:
                self._add_check(
                    "NET-002",
                    "Suspicious Open Ports",
                    f"Found suspicious listening services: {', '.join(open_suspicious)}",
                    "WARNING",
                    "MEDIUM",
                    "Disable unnecessary services and use secure alternatives",
                    "Network Security"
                )
            else:
                self._add_check(
                    "NET-002",
                    "Open Ports",
                    f"Found {len(listening_ports)} listening ports, no obvious suspicious services",
                    "PASS",
                    "LOW",
                    "",
                    "Network Security"
                )
        except Exception as e:
            logger.debug(f"Network check failed: {e}")
        
        # Check for IP forwarding
        try:
            with open("/proc/sys/net/ipv4/ip_forward", 'r') as f:
                if f.read().strip() == "1":
                    self._add_check(
                        "NET-003",
                        "IP Forwarding",
                        "IP forwarding is enabled",
                        "WARNING",
                        "MEDIUM",
                        "Disable IP forwarding if not required for routing",
                        "Network Security"
                    )
                else:
                    self._add_check(
                        "NET-003",
                        "IP Forwarding",
                        "IP forwarding is disabled",
                        "PASS",
                        "LOW",
                        "",
                        "Network Security"
                    )
        except:
            pass

    def check_encryption(self):
        """Check encryption compliance."""
        logger.info("Checking encryption...")
        
        # Check for SSL/TLS config
        ssl_dirs = ["/etc/ssl", "/etc/pki/tls"]
        found_ssl = False
        
        for ssl_dir in ssl_dirs:
            if Path(ssl_dir).exists():
                found_ssl = True
                
                certs = list(Path(ssl_dir).rglob("*.crt")) + list(Path(ssl_dir).rglob("*.pem"))
                
                self._add_check(
                    "CRYP-001",
                    "SSL/TLS Certificates",
                    f"Found {len(certs)} certificate(s) in {ssl_dir}",
                    "INFO",
                    "LOW",
                    "",
                    "Cryptography"
                )
                break
        
        if not found_ssl:
            self._add_check(
                "CRYP-001",
                "SSL/TLS Certificates",
                "No standard SSL/TLS directories found",
                "INFO",
                "LOW",
                "Verify SSL/TLS configuration for web services",
                "Cryptography"
            )
        
        # Check for encrypted partitions
        try:
            result = subprocess.run(
                ["df", "-T"],
                capture_output=True, text=True
            )
            
            encrypted_found = False
            if result.returncode == 0:
                for line in result.stdout.split('\n')[1:]:
                    if "luks" in line.lower() or "encfs" in line.lower():
                        encrypted_found = True
                        break
            
            if encrypted_found:
                self._add_check(
                    "CRYP-002",
                    "Encrypted Partitions",
                    "Encrypted filesystems detected",
                    "PASS",
                    "LOW",
                    "",
                    "Cryptography"
                )
            else:
                self._add_check(
                    "CRYP-002",
                    "Encrypted Partitions",
                    "No encrypted filesystems detected",
                    "WARNING",
                    "MEDIUM",
                    "Consider encrypting sensitive data partitions",
                    "Cryptography"
                )
        except Exception as e:
            logger.debug(f"Encryption check failed: {e}")

    def check_logging(self):
        """Check logging configuration."""
        logger.info("Checking logging configuration...")
        
        # Check syslog
        log_files = [
            "/var/log/syslog",
            "/var/log/messages",
            "/var/log/auth.log"
        ]
        
        found_logs = 0
        for log in log_files:
            if Path(log).exists():
                found_logs += 1
        
        if found_logs > 0:
            self._add_check(
                "LOG-001",
                "System Logging",
                f"Found {found_logs} system log file(s)",
                "PASS",
                "LOW",
                "",
                "Operations Security"
            )
        else:
            self._add_check(
                "LOG-001",
                "System Logging",
                "No standard system logs found",
                "WARNING",
                "MEDIUM",
                "Ensure syslog is configured and functional",
                "Operations Security"
            )
        
        # Check auditd
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True, text=True
            )
            
            if "auditd" in result.stdout:
                self._add_check(
                    "LOG-002",
                    "Audit Daemon",
                    "auditd is running",
                    "PASS",
                    "LOW",
                    "",
                    "Operations Security"
                )
            else:
                self._add_check(
                    "LOG-002",
                    "Audit Daemon",
                    "auditd is not running",
                    "WARNING",
                    "MEDIUM",
                    "Consider enabling auditd for security event monitoring",
                    "Operations Security"
                )
        except:
            pass

    def check_updates(self):
        """Check system updates."""
        logger.info("Checking system updates...")
        
        # Check package manager updates
        try:
            # Try apt
            result = subprocess.run(
                ["apt-get", "-s", "upgrade"],
                capture_output=True, text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Count updates
                lines = result.stdout.split('\n')
                upgrade_count = 0
                security_count = 0
                
                for line in lines:
                    if "upgraded" in line:
                        parts = line.split()
                        for i, p in enumerate(parts):
                            if "upgraded" in p and i > 0:
                                try:
                                    upgrade_count = int(parts[i-1])
                                except:
                                    pass
                    if "security" in line.lower():
                        security_count += 1
                
                if upgrade_count > 0:
                    self._add_check(
                        "UPD-001",
                        "System Updates",
                        f"{upgrade_count} package update(s) available",
                        "WARNING",
                        "MEDIUM",
                        "Run apt-get upgrade to apply updates",
                        "Vulnerability Management"
                    )
                    
                    if security_count > 0:
                        self._add_check(
                            "UPD-002",
                            "Security Updates",
                            f"Security updates available",
                            "FAIL",
                            "HIGH",
                            "Apply security updates immediately",
                            "Vulnerability Management"
                        )
                else:
                    self._add_check(
                        "UPD-001",
                        "System Updates",
                        "System is up to date",
                        "PASS",
                        "LOW",
                        "",
                        "Vulnerability Management"
                    )
        except Exception as e:
            logger.debug(f"Update check failed: {e}")
            self._add_check(
                "UPD-001",
                "System Updates",
                "Could not check for updates",
                "INFO",
                "LOW",
                "Manually verify system updates",
                "Vulnerability Management"
            )

    def run_full_compliance_check(self, framework: str = "GENERAL"):
        """Run full compliance check."""
        logger.info(f"Starting compliance check for framework: {framework}")
        
        self.compliance_report["framework"] = framework
        
        print(f"\n✅ Starting {framework} Compliance Check...\n")
        
        checks_to_run = [
            ("User Management", self.check_user_management),
            ("File Permissions", self.check_file_permissions),
            ("Network Security", self.check_network_security),
            ("Encryption", self.check_encryption),
            ("Logging", self.check_logging),
            ("Updates", self.check_updates)
        ]
        
        for name, check_func in checks_to_run:
            print(f"  📋 Checking {name}...")
            try:
                check_func()
            except Exception as e:
                logger.error(f"Check {name} failed: {e}")
                self._add_check(
                    f"ERR-{len(self.compliance_report['checks'])+1:03d}",
                    name,
                    f"Check failed with error: {e}",
                    "INFO",
                    "LOW",
                    "Review check manually",
                    "General"
                )
        
        # Calculate overall score
        total_checks = (self.compliance_report["passed_checks"] + 
                       self.compliance_report["failed_checks"] + 
                       self.compliance_report["warning_checks"])
        
        if total_checks > 0:
            # Weight: PASS = 100, WARNING = 50, FAIL = 0
            total_score = (self.compliance_report["passed_checks"] * 100 +
                          self.compliance_report["warning_checks"] * 50)
            self.compliance_report["overall_score"] = total_score // total_checks
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Generate executive summary
        self._generate_executive_summary()
        
        self._save_report()
        
        return self.compliance_report

    def _generate_recommendations(self):
        """Generate recommendations based on failed checks."""
        failed = [c for c in self.compliance_report["checks"] if c["status"] == "FAIL"]
        warnings = [c for c in self.compliance_report["checks"] if c["status"] == "WARNING"]
        
        if failed:
            self.compliance_report["recommendations"].append({
                "priority": "HIGH",
                "text": f"Address {len(failed)} critical failures immediately"
            })
        
        if len(warnings) > 5:
            self.compliance_report["recommendations"].append({
                "priority": "MEDIUM",
                "text": f"Review {len(warnings)} warnings and remediate as needed"
            })

    def _generate_executive_summary(self):
        """Generate executive summary."""
        score = self.compliance_report["overall_score"]
        
        if score >= 90:
            status = "EXCELLENT"
        elif score >= 75:
            status = "GOOD"
        elif score >= 50:
            status = "NEEDS IMPROVEMENT"
        else:
            status = "CRITICAL"
        
        self.compliance_report["executive_summary"] = (
            f"Compliance Score: {score} ({status}). "
            f"Passed: {self.compliance_report['passed_checks']}, "
            f"Failed: {self.compliance_report['failed_checks']}, "
            f"Warnings: {self.compliance_report['warning_checks']}."
        )

    def generate_report(self) -> str:
        """Generate compliance report."""
        report = []
        report.append("=" * 70)
        report.append("✅ COMPLIANCE ASSESSMENT REPORT")
        report.append("=" * 70)
        report.append(f"Report ID: {self.compliance_report['report_id']}")
        report.append(f"Framework: {self.compliance_report.get('framework', 'GENERAL')}")
        report.append(f"Timestamp: {self.compliance_report['timestamp']}")
        report.append("")
        
        # Score
        score = self.compliance_report["overall_score"]
        if score >= 90:
            grade = "🟢 EXCELLENT"
        elif score >= 75:
            grade = "🟡 GOOD"
        elif score >= 50:
            grade = "🟠 NEEDS IMPROVEMENT"
        else:
            grade = "🔴 CRITICAL"
        
        report.append(f"SECURITY SCORE: {score}/100 - {grade}")
        report.append("")
        report.append(f"Passed Checks:   {self.compliance_report['passed_checks']}")
        report.append(f"Failed Checks:   {self.compliance_report['failed_checks']}")
        report.append(f"Warnings:        {self.compliance_report['warning_checks']}")
        report.append("")
        
        # Executive Summary
        if self.compliance_report.get("executive_summary"):
            report.append("📊 EXECUTIVE SUMMARY:")
            report.append(f"  {self.compliance_report['executive_summary']}")
            report.append("")
        
        # Failed Checks
        failed = [c for c in self.compliance_report["checks"] if c["status"] == "FAIL"]
        if failed:
            report.append("🔴 FAILED CHECKS:")
            for check in failed:
                report.append(f"  • [{check['id']}] {check['name']}")
                report.append(f"    {check['description']}")
                if check.get('remediation'):
                    report.append(f"    → {check['remediation']}")
            report.append("")
        
        # Warnings
        warnings = [c for c in self.compliance_report["checks"] if c["status"] == "WARNING"]
        if warnings:
            report.append("🟡 WARNINGS:")
            for check in warnings[:10]:  # Limit to 10
                report.append(f"  • [{check['id']}] {check['name']}")
                report.append(f"    {check['description']}")
            if len(warnings) > 10:
                report.append(f"  ... and {len(warnings) - 10} more warnings")
            report.append("")
        
        # Passed Checks
        passed = [c for c in self.compliance_report["checks"] if c["status"] == "PASS"]
        if passed:
            report.append(f"🟢 PASSED CHECKS ({len(passed)}):")
            for check in passed[:5]:
                report.append(f"  ✓ [{check['id']}] {check['name']}")
            if len(passed) > 5:
                report.append(f"  ... and {len(passed) - 5} more")
            report.append("")
        
        # Recommendations
        if self.compliance_report.get("recommendations"):
            report.append("💡 RECOMMENDATIONS:")
            for rec in self.compliance_report["recommendations"]:
                report.append(f"  [{rec['priority']}] {rec['text']}")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)

    def list_frameworks(self) -> List[Dict]:
        """List available compliance frameworks."""
        return [
            {"id": fid, "name": f["name"], "description": f["description"]}
            for fid, f in self.FRAMEWORKS.items()
        ]


def main():
    parser = argparse.ArgumentParser(
        description="✅ Compliance Checker Agent - Security compliance auditing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --check --framework GDPR
  %(prog)s --check --framework SOC2
  %(prog)s --check --framework ISO27001
  %(prog)s --check --framework NIST
  %(prog)s --check --framework PCI-DSS
  %(prog)s --list-frameworks
  %(prog)s --list-reports
  %(prog)s --report compliance_20240315_120000
  
Supports: GDPR, SOC2, ISO27001, NIST, PCI-DSS
        """
    )
    
    parser.add_argument("--check", "-c", action="store_true", help="Run compliance check")
    parser.add_argument("--framework", "-f", 
                       choices=["GDPR", "SOC2", "ISO27001", "NIST", "PCI-DSS", "GENERAL"],
                       default="GENERAL", help="Compliance framework")
    parser.add_argument("--list-frameworks", "-l", action="store_true", 
                       help="List available frameworks")
    parser.add_argument("--list-reports", action="store_true", help="List previous reports")
    parser.add_argument("--report", "-r", help="Show specific compliance report")
    parser.add_argument("--output", "-o", help="Output file for report (JSON)")
    
    args = parser.parse_args()

    checker = ComplianceChecker()

    if args.list_frameworks:
        print("\n📋 AVAILABLE COMPLIANCE FRAMEWORKS:\n")
        for fw in checker.list_frameworks():
            print(f"  [{fw['id']}] {fw['name']}")
            print(f"       {fw['description']}")
            print()
        sys.exit(0)

    if args.list_reports:
        try:
            with open(COMPLIANCE_REPORTS_FILE, 'r') as f:
                data = json.load(f)
            print(f"\n📋 Found {len(data['reports'])} compliance reports:\n")
            for report in data["reports"][-10:]:
                print(f"  • {report['report_id']}")
                print(f"    Framework: {report.get('framework', 'N/A')}")
                print(f"    Score: {report['overall_score']}/100")
                print(f"    Time: {report['timestamp']}")
                print()
        except FileNotFoundError:
            print("No compliance reports found.")
        sys.exit(0)

    if args.report:
        try:
            with open(COMPLIANCE_REPORTS_FILE, 'r') as f:
                data = json.load(f)
            for report in data["reports"]:
                if report["report_id"] == args.report:
                    checker.compliance_report = report
                    print(checker.generate_report())
                    break
            else:
                print(f"Report {args.report} not found.")
        except FileNotFoundError:
            print("No compliance reports found.")
        sys.exit(0)

    if args.check:
        try:
            results = checker.run_full_compliance_check(args.framework)
            print(checker.generate_report())
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\n📄 Report saved to {args.output}")
        except KeyboardInterrupt:
            print("\n⚠️  Check interrupted")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
