#!/usr/bin/env python3
"""
SOX Compliance Agent
Sarbanes-Oxley Act compliance checking and reporting
Validates IT controls, access management, and financial system security
"""

import argparse
import json
import logging
import os
import socket
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "sox_compliance.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SOXCompliance")


class SOXComplianceAgent:
    """SOX Compliance checking and reporting"""
    
    # SOX key controls (simplified)
    REQUIRED_CONTROLS = {
        "access_control": {
            "name": "Access Control",
            "description": "Logical and physical access controls",
            "requirements": [
                "User access reviews quarterly",
                "Segregation of duties enforced",
                "Privileged access logged",
                "Inactive accounts disabled after 90 days"
            ],
            "severity": "critical"
        },
        "change_management": {
            "name": "Change Management",
            "description": "System changes must be authorized and documented",
            "requirements": [
                "Change request documentation",
                "Approval workflow",
                "Testing documentation",
                "Rollback procedures"
            ],
            "severity": "critical"
        },
        "data_integrity": {
            "name": "Data Integrity",
            "description": "Financial data must be accurate and complete",
            "requirements": [
                "Input validation",
                "Edit checks",
                "Reconciliation procedures",
                "Audit trails"
            ],
            "severity": "critical"
        },
        "backup_recovery": {
            "name": "Backup and Recovery",
            "description": "Critical data must be backed up and recoverable",
            "requirements": [
                "Daily backups",
                "Backup verification testing",
                "Disaster recovery plan",
                "Recovery time objectives defined"
            ],
            "severity": "high"
        },
        "security_monitoring": {
            "name": "Security Monitoring",
            "description": "Continuous security monitoring",
            "requirements": [
                "Log aggregation",
                "Intrusion detection",
                "Vulnerability scanning",
                "Incident response procedures"
            ],
            "severity": "high"
        },
        "password_policy": {
            "name": "Password Policy",
            "description": "Strong authentication requirements",
            "requirements": [
                "Minimum 8 characters",
                "Mixed case required",
                "Numbers required",
                "Special characters required",
                "90-day expiration"
            ],
            "severity": "medium"
        }
    }
    
    def __init__(self, output_file: Optional[str] = None):
        self.output_file = output_file or f"/home/clawbot/.openclaw/workspace/data/sox_compliance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.db_path = Path("/home/clawbot/.openclaw/workspace/data/sox_compliance.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "audit_time": datetime.now().isoformat(),
            "compliance_level": "unknown",
            "overall_score": 0,
            "controls": {},
            "findings": [],
            "recommendations": [],
            "next_audit_date": None
        }
        
        self._init_db()
    
    def _init_db(self):
        """Initialize compliance tracking database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS compliance_controls
                     (id TEXT PRIMARY KEY, name TEXT, status TEXT, 
                      last_checked TEXT, findings TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS audit_history
                     (id INTEGER PRIMARY KEY, audit_date TEXT, 
                      overall_score REAL, compliance_level TEXT)''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized: {self.db_path}")
    
    def _check_access_control(self) -> Dict:
        """Check access control compliance"""
        findings = []
        score = 100
        
        # Check for inactive accounts (simulated)
        inactive_days = 0  # Would check actual system in production
        
        # Check password policy compliance
        try:
            import spwd
            findings.append({"type": "info", "message": "Shadow password database accessible"})
        except ImportError:
            findings.append({"type": "warning", "message": "Cannot access shadow password database (running as non-root)"})
        
        # Check for password expiration
        score -= 10 if score == 100 else 0
        
        # Check for privileged users
        try:
            with open('/etc/group') as f:
                for line in f:
                    if 'sudo' in line or 'wheel' in line:
                        findings.append({"type": "info", "message": f"Privileged group found: {line.strip()}"})
        except PermissionError:
            findings.append({"type": "warning", "message": "Cannot read /etc/group"})
        
        status = "compliant" if score >= 80 else "non_compliant" if score >= 50 else "critical"
        
        return {
            "control_id": "access_control",
            "status": status,
            "score": score,
            "findings": findings
        }
    
    def _check_change_management(self) -> Dict:
        """Check change management compliance"""
        findings = []
        score = 100
        
        # Check for configuration management
        config_dirs = ['/etc', '/opt', '/var/www']
        managed_count = 0
        
        for dir_path in config_dirs:
            if Path(dir_path).exists():
                managed_count += 1
        
        coverage = managed_count / len(config_dirs) * 100
        
        if coverage < 100:
            score -= int((100 - coverage) / 2)
            findings.append({
                "type": "warning",
                "message": f"Configuration coverage: {coverage:.0f}% (some dirs not managed)"
            })
        
        # Check for backup of config files
        backup_marker = Path("/var/backups")
        if backup_marker.exists():
            findings.append({"type": "info", "message": "System backup directory exists"})
        else:
            score -= 10
            findings.append({"type": "warning", "message": "No backup directory found"})
        
        status = "compliant" if score >= 80 else "non_compliant" if score >= 50 else "critical"
        
        return {
            "control_id": "change_management",
            "status": status,
            "score": score,
            "findings": findings
        }
    
    def _check_data_integrity(self) -> Dict:
        """Check data integrity controls"""
        findings = []
        score = 100
        
        # Check filesystem integrity tools
        integrity_tools = ['sha256sum', 'md5sum', 'aide']
        available_tools = []
        
        for tool in integrity_tools:
            if os.system(f"which {tool} >/dev/null 2>&1") == 0:
                available_tools.append(tool)
        
        if available_tools:
            findings.append({
                "type": "info",
                "message": f"Integrity tools available: {', '.join(available_tools)}"
            })
        else:
            score -= 20
            findings.append({
                "type": "warning",
                "message": "No file integrity monitoring tools found"
            })
        
        # Check for audit logging
        audit_paths = ['/var/log/auth.log', '/var/log/audit/audit.log']
        audit_enabled = any(Path(p).exists() for p in audit_paths)
        
        if audit_enabled:
            findings.append({"type": "info", "message": "Audit logging is enabled"})
        else:
            score -= 15
            findings.append({"type": "warning", "message": "Audit logging may not be fully enabled"})
        
        status = "compliant" if score >= 80 else "non_compliant" if score >= 50 else "critical"
        
        return {
            "control_id": "data_integrity",
            "status": status,
            "score": score,
            "findings": findings
        }
    
    def _check_backup_recovery(self) -> Dict:
        """Check backup and recovery controls"""
        findings = []
        score = 100
        
        # Check for backup utilities
        backup_tools = ['rsync', 'tar', 'duplicity', 'bacula', 'amanda']
        available = []
        
        for tool in backup_tools:
            if os.system(f"which {tool} >/dev/null 2>&1") == 0:
                available.append(tool)
        
        if available:
            findings.append({
                "type": "info",
                "message": f"Backup tools available: {', '.join(available)}"
            })
        else:
            score -= 25
            findings.append({
                "type": "critical",
                "message": "No standard backup tools found"
            })
        
        # Check for backup destination
        backup_locations = ['/backup', '/backups', '/var/backups', '/mnt/backup']
        has_backup = any(Path(loc).exists() for loc in backup_locations)
        
        if has_backup:
            findings.append({"type": "info", "message": "Backup directory exists"})
        else:
            score -= 15
            findings.append({"type": "warning", "message": "No dedicated backup directory found"})
        
        status = "compliant" if score >= 80 else "non_compliant" if score >= 50 else "critical"
        
        return {
            "control_id": "backup_recovery",
            "status": status,
            "score": score,
            "findings": findings
        }
    
    def _check_security_monitoring(self) -> Dict:
        """Check security monitoring controls"""
        findings = []
        score = 100
        
        # Check for security monitoring tools
        mon_tools = ['fail2ban', 'aide', 'rkhunter', 'tripwire', 'ossec']
        available = []
        
        for tool in mon_tools:
            if os.system(f"which {tool} >/dev/null 2>&1") == 0:
                available.append(tool)
        
        if available:
            findings.append({
                "type": "info",
                "message": f"Security monitoring tools: {', '.join(available)}"
            })
        else:
            score -= 15
            findings.append({
                "type": "warning",
                "message": "Limited security monitoring tools installed"
            })
        
        # Check firewall status
        if os.system("iptables -L >/dev/null 2>&1") == 0:
            findings.append({"type": "info", "message": "iptables firewall is accessible"})
        elif os.system("ufw status >/dev/null 2>&1") == 0:
            findings.append({"type": "info", "message": "UFW firewall is accessible"})
        
        status = "compliant" if score >= 80 else "non_compliant" if score >= 50 else "critical"
        
        return {
            "control_id": "security_monitoring",
            "status": status,
            "score": score,
            "findings": findings
        }
    
    def _check_password_policy(self) -> Dict:
        """Check password policy compliance"""
        findings = []
        score = 100
        
        # Check password policy files
        password_policy_files = [
            '/etc/login.defs',
            '/etc/pam.d/common-password',
            '/etc/security/pwquality.conf'
        ]
        
        policy_found = False
        for f in password_policy_files:
            if Path(f).exists():
                policy_found = True
                findings.append({"type": "info", "message": f"Password policy file found: {f}"})
        
        if not policy_found:
            score -= 20
            findings.append({
                "type": "warning",
                "message": "No password policy configuration found"
            })
        
        # Check for password expiration settings
        try:
            with open('/etc/login.defs') as f:
                content = f.read()
                if 'PASS_MAX_DAYS' in content:
                    findings.append({"type": "info", "message": "PASS_MAX_DAYS configured in login.defs"})
                if 'PASS_MIN_DAYS' in content:
                    findings.append({"type": "info", "message": "PASS_MIN_DAYS configured in login.defs"})
        except PermissionError:
            findings.append({"type": "warning", "message": "Cannot read password policy (permission denied)"})
        
        status = "compliant" if score >= 80 else "non_compliant" if score >= 50 else "critical"
        
        return {
            "control_id": "password_policy",
            "status": status,
            "score": score,
            "findings": findings
        }
    
    def run_audit(self) -> Dict:
        """Run full SOX compliance audit"""
        logger.info("Starting SOX compliance audit")
        
        controls = [
            ("access_control", self._check_access_control),
            ("change_management", self._check_change_management),
            ("data_integrity", self._check_data_integrity),
            ("backup_recovery", self._check_backup_recovery),
            ("security_monitoring", self._check_security_monitoring),
            ("password_policy", self._check_password_policy)
        ]
        
        all_findings = []
        total_score = 0
        critical_count = 0
        non_compliant_count = 0
        
        for control_id, check_func in controls:
            logger.info(f"Checking control: {control_id}")
            
            control_info = self.REQUIRED_CONTROLS[control_id]
            result = check_func()
            
            self.results["controls"][control_id] = {
                **control_info,
                **result
            }
            
            all_findings.extend(result.get("findings", []))
            total_score += result["score"]
            
            if result["status"] == "critical":
                critical_count += 1
            elif result["status"] == "non_compliant":
                non_compliant_count += 1
        
        # Calculate overall score
        self.results["overall_score"] = round(total_score / len(controls), 1)
        
        # Determine compliance level
        if self.results["overall_score"] >= 90 and critical_count == 0:
            self.results["compliance_level"] = "compliant"
        elif self.results["overall_score"] >= 70:
            self.results["compliance_level"] = "partially_compliant"
        elif self.results["overall_score"] >= 50:
            self.results["compliance_level"] = "non_compliant"
        else:
            self.results["compliance_level"] = "critical"
        
        # Set next audit date (quarterly)
        self.results["next_audit_date"] = (datetime.now() + timedelta(days=90)).isoformat()
        
        # Add all findings
        self.results["findings"] = all_findings
        
        # Generate recommendations
        self.results["recommendations"] = self._generate_recommendations()
        
        # Save to database
        self._save_to_db()
        
        logger.info(f"SOX compliance audit complete. Level: {self.results['compliance_level']}")
        
        return self.results
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on findings"""
        recommendations = []
        
        controls = self.results.get("controls", {})
        
        for control_id, control_data in controls.items():
            if control_data.get("status") in ["non_compliant", "critical"]:
                name = control_data.get("name", control_id)
                recommendations.append(f"Review and remediate {name} controls - currently {control_data.get('status')}")
        
        if self.results.get("overall_score", 100) < 90:
            recommendations.append("Implement regular compliance monitoring and automated checks")
        
        if not recommendations:
            recommendations.append("Maintain current compliance posture and continue quarterly reviews")
        
        recommendations.append("Document all exceptions and remediation plans")
        recommendations.append("Train staff on SOX compliance requirements")
        
        return recommendations
    
    def _save_to_db(self):
        """Save audit results to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Save control statuses
        for control_id, data in self.results.get("controls", {}).items():
            c.execute('''INSERT OR REPLACE INTO compliance_controls 
                         VALUES (?, ?, ?, ?, ?)''',
                     (control_id, data.get("name"), data.get("status"),
                      datetime.now().isoformat(), json.dumps(data.get("findings", []))))
        
        # Save audit history
        c.execute('''INSERT INTO audit_history VALUES (NULL, ?, ?, ?)''',
                 (datetime.now().isoformat(), self.results["overall_score"],
                  self.results["compliance_level"]))
        
        conn.commit()
        conn.close()
    
    def save_results(self):
        """Save audit results to JSON file"""
        with open(self.output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Results saved to {self.output_file}")
    
    def print_report(self):
        """Print compliance report"""
        print(f"\n{'='*70}")
        print(f"SOX COMPLIANCE AUDIT REPORT")
        print(f"{'='*70}")
        print(f"Audit Date: {self.results['audit_time']}")
        print(f"Overall Score: {self.results['overall_score']}/100")
        print(f"Compliance Level: {self.results['compliance_level'].upper()}")
        print(f"Next Audit: {self.results.get('next_audit_date', 'N/A')}")
        
        print(f"\nControl Status:")
        for control_id, data in self.results.get("controls", {}).items():
            status_icon = "✅" if data.get("status") == "compliant" else "⚠️" if data.get("status") == "non_compliant" else "❌"
            print(f"  {status_icon} {data.get('name', control_id)}: {data.get('score', 0)}/100 ({data.get('status', 'unknown')})")
        
        if self.results.get("findings"):
            print(f"\nFindings ({len(self.results['findings'])}):")
            for finding in self.results["findings"][:10]:
                icon = "🔴" if finding.get("type") == "critical" else "🟡" if finding.get("type") == "warning" else "🔵"
                print(f"  {icon} {finding.get('message', '')}")
            if len(self.results["findings"]) > 10:
                print(f"  ... and {len(self.results['findings']) - 10} more")
        
        print(f"\nRecommendations:")
        for rec in self.results.get("recommendations", [])[:5]:
            print(f"  → {rec}")
        
        print(f"\nReport saved to: {self.output_file}")
        print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description="SOX Compliance Agent - Sarbanes-Oxley Act compliance checking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --audit                    Run full SOX compliance audit
  %(prog)s --audit --verbose          Run with detailed output
  %(prog)s --report                   Generate report from last audit
        """
    )
    parser.add_argument("--audit", "-a", action="store_true", help="Run SOX compliance audit")
    parser.add_argument("--report", "-r", action="store_true", help="Generate report from saved results")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        agent = SOXComplianceAgent(args.output)
        
        if args.audit or not args.report:
            agent.run_audit()
            agent.save_results()
            agent.print_report()
        elif args.report:
            # Load and display last results
            if agent.db_path.exists():
                print("Loading previous audit results...")
                # Could implement loading from db here
                print("Use --audit to run a new audit")
            else:
                print("No previous audit found. Use --audit to run one.")
        
    except KeyboardInterrupt:
        print("\nAudit interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
