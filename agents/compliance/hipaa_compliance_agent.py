#!/usr/bin/env python3
"""
HIPAA Compliance Agent
Health Insurance Portability and Accountability Act compliance checking
Validates PHI protection, access controls, and healthcare data security
"""

import argparse
import json
import logging
import os
import pwd
import socket
import sqlite3
import stat
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "hipaa_compliance.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("HIPACompliance")


class HIPAComplianceAgent:
    """HIPAA Compliance checking and reporting"""
    
    # HIPAA Safe Harbor and required safeguards
    REQUIRED_SAFEGUARDS = {
        "administrative_safeguards": {
            "name": "Administrative Safeguards",
            "description": "Policies and procedures for HIPAA compliance",
            "requirements": [
                "Security Officer designated",
                "Risk assessment conducted annually",
                " workforce training documented",
                " contingency plan in place",
                "Business Associate agreements signed"
            ],
            "standards": [
                "164.308(a)(1)",  # Security Management Process
                "164.308(a)(3)",  # Workforce Security
                "164.308(a)(5)",  # Security Awareness Training
                "164.308(a)(6)",  # Incident Procedures
                "164.308(a)(7)"   # Contingency Plan
            ],
            "severity": "critical"
        },
        "physical_safeguards": {
            "name": "Physical Safeguards",
            "description": "Physical access to PHI and facilities",
            "requirements": [
                "Facility access controls",
                "Workstation use policies",
                "Workstation security",
                "Device and media controls"
            ],
            "standards": [
                "164.310(a)(1)",  # Facility Access Controls
                "164.310(b)",     # Workstation Use
                "164.310(c)",     # Workstation Security
                "164.310(d)(1)",  # Device and Media Controls
                "164.310(d)(2)",  # Device and Media Controls
                "164.310(d)(3)"   # Device and Media Controls
            ],
            "severity": "critical"
        },
        "technical_safeguards": {
            "name": "Technical Safeguards",
            "description": "Technical protections for PHI",
            "requirements": [
                "Access control implemented",
                "Audit controls enabled",
                "Integrity controls in place",
                "Transmission security (TLS/SSL)",
                "Emergency access procedures"
            ],
            "standards": [
                "164.312(a)(1)",  # Access Control
                "164.312(a)(2)",  # Access Control
                "164.312(b)",     # Audit Controls
                "164.312(c)(1)",  # Integrity
                "164.312(e)(1)",  # Transmission Security
                "164.312(e)(2)",  # Transmission Security
                "164.312(a)(2)(ii)"  # Emergency Access
            ],
            "severity": "critical"
        },
        "phi_protection": {
            "name": "PHI Protection",
            "description": "Protected Health Information safeguards",
            "requirements": [
                "PHI encrypted at rest",
                "PHI encrypted in transit",
                "PHI access logging",
                "PHI disclosure tracking",
                "Minimum necessary standard"
            ],
            "severity": "critical"
        },
        "breach_notification": {
            "name": "Breach Notification",
            "description": "Breach detection and reporting",
            "requirements": [
                "Breach detection system",
                "60-day notification policy",
                "Risk assessment for breaches",
                "Breach log maintained"
            ],
            "standards": [
                "164.400",  # Notification
                "164.402",  # Definitions
                "164.404",  # Notification Timeliness
                "164.406",  # Notification to Media
                "164.408"   # Notification to HHS
            ],
            "severity": "high"
        }
    }
    
    def __init__(self, output_file: Optional[str] = None):
        self.output_file = output_file or f"/home/clawbot/.openclaw/workspace/data/hipaa_compliance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.db_path = Path("/home/clawbot/.openclaw/workspace/data/hipaa_compliance.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "audit_time": datetime.now().isoformat(),
            "compliance_level": "unknown",
            "overall_score": 0,
            "safeguards": {},
            "findings": [],
            "phi_locations": [],
            "recommendations": [],
            "next_audit_date": None
        }
        
        self._init_db()
    
    def _init_db(self):
        """Initialize HIPAA compliance tracking database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS hipaa_safeguards
                     (id TEXT PRIMARY KEY, name TEXT, status TEXT, 
                      last_checked TEXT, findings TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS phi_access_log
                     (id INTEGER PRIMARY KEY, user TEXT, action TEXT,
                      resource TEXT, timestamp TEXT, compliant INTEGER)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS audit_history
                     (id INTEGER PRIMARY KEY, audit_date TEXT, 
                      overall_score REAL, compliance_level TEXT)''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized: {self.db_path}")
    
    def _check_administrative_safeguards(self) -> Dict:
        """Check administrative safeguards"""
        findings = []
        score = 100
        
        # Check for Security Officer (would be in a real system)
        security_officer_defined = os.path.exists('/etc/security/officer') or os.path.exists('/opt/hipaa')
        
        if security_officer_defined:
            findings.append({"type": "info", "message": "HIPAA configuration directory exists"})
        else:
            findings.append({"type": "info", "message": "Security Officer designation should be documented"})
        
        # Check for security policies
        policy_files = ['/etc/security/policy', '/opt/hipaa/policies', '/root/hipaa']
        has_policies = any(Path(f).exists() for f in policy_files)
        
        if has_policies:
            findings.append({"type": "info", "message": "Security policy files found"})
        else:
            score -= 15
            findings.append({"type": "warning", "message": "Security policies should be documented"})
        
        # Check for risk assessment
        risk_files = ['/var/hipaa/risk_assessment', '/opt/hipaa/risk']
        has_risk = any(Path(f).exists() for f in risk_files)
        
        if has_risk:
            findings.append({"type": "info", "message": "Risk assessment documentation found"})
        else:
            score -= 20
            findings.append({"type": "warning", "message": "Annual risk assessment should be documented"})
        
        # Check for contingency plan
        contingency_files = ['/var/hipaa/contingency', '/opt/hipaa/disaster_recovery']
        has_contingency = any(Path(f).exists() for f in contingency_files)
        
        if has_contingency:
            findings.append({"type": "info", "message": "Contingency plan documentation found"})
        else:
            score -= 15
            findings.append({"type": "warning", "message": "Contingency plan should be documented"})
        
        # Check for BA agreements (would be in documents in production)
        ba_agreements = Path('/var/hipaa/ba_agreements')
        if ba_agreements.exists():
            findings.append({"type": "info", "message": "Business Associate agreement directory exists"})
        else:
            findings.append({"type": "info", "message": "Business Associate agreements should be on file"})
        
        status = "compliant" if score >= 80 else "non_compliant" if score >= 50 else "critical"
        
        return {
            "safeguard_id": "administrative_safeguards",
            "status": status,
            "score": score,
            "findings": findings
        }
    
    def _check_physical_safeguards(self) -> Dict:
        """Check physical safeguards"""
        findings = []
        score = 100
        
        # Check for console lock
        if os.system("ps aux | grep -v grep | grep -E 'screen|tmux|screenlock' >/dev/null") == 0:
            findings.append({"type": "info", "message": "Session management tools available"})
        
        # Check for screen lock tools
        screenlock_tools = ['xlock', 'xscrnsaver', 'gnome-screensaver']
        has_lock = False
        for tool in screenlock_tools:
            if os.system(f"which {tool} >/dev/null 2>&1") == 0:
                has_lock = True
                findings.append({"type": "info", "message": f"Screen lock tool available: {tool}"})
                break
        
        # Check device permissions
        sensitive_devices = ['/dev/sda', '/dev/sdb']  # Disks
        for dev in sensitive_devices:
            if Path(dev).exists():
                mode = os.stat(dev).st_mode
                if mode & stat.S_IROTH or mode & stat.S_IWOTH:
                    score -= 10
                    findings.append({"type": "warning", "message": f"Device {dev} has world permissions"})
        
        # Check for automatic logout
        auto_logout_files = ['/etc/profile.d/autologout.sh', '/etc/tmux.conf']
        has_autologout = any(Path(f).exists() for f in auto_logout_files)
        
        if has_autologout:
            findings.append({"type": "info", "message": "Auto-logout configuration found"})
        
        status = "compliant" if score >= 80 else "non_compliant" if score >= 50 else "critical"
        
        return {
            "safeguard_id": "physical_safeguards",
            "status": status,
            "score": score,
            "findings": findings
        }
    
    def _check_technical_safeguards(self) -> Dict:
        """Check technical safeguards"""
        findings = []
        score = 100
        
        # Check access controls
        access_control_score = 100
        
        # Check for PAM (Pluggable Authentication Modules)
        pam_dir = Path('/etc/pam.d')
        if pam_dir.exists():
            findings.append({"type": "info", "message": "PAM authentication is configured"})
        else:
            access_control_score -= 20
        
        # Check for sudo configuration
        sudoers_file = Path('/etc/sudoers')
        sudoers_d = Path('/etc/sudoers.d')
        
        if sudoers_file.exists() or sudoers_d.exists():
            findings.append({"type": "info", "message": "Sudo access is configured"})
        
        # Check audit logging
        audit_score = 100
        log_dirs = ['/var/log/auth.log', '/var/log/audit', '/var/log/syslog']
        log_count = sum(1 for d in log_dirs if Path(d).exists())
        
        if log_count >= 2:
            findings.append({"type": "info", "message": "Comprehensive audit logging enabled"})
        else:
            audit_score -= 30
        
        # Check encryption tools
        encryption_tools = ['gpg', 'openssl', 'cryptsetup', 'luks']
        available_encryption = []
        for tool in encryption_tools:
            if os.system(f"which {tool} >/dev/null 2>&1") == 0:
                available_encryption.append(tool)
        
        if available_encryption:
            findings.append({
                "type": "info",
                "message": f"Encryption tools available: {', '.join(available_encryption)}"
            })
        else:
            score -= 15
            findings.append({"type": "warning", "message": "Limited encryption tools available"})
        
        # Check for TLS/SSL
        if os.system("which openssl >/dev/null 2>&1") == 0:
            findings.append({"type": "info", "message": "OpenSSL available for TLS/SSL"})
        
        # Check for SSH hardening
        ssh_config = Path('/etc/ssh/sshd_config')
        if ssh_config.exists():
            try:
                with open(ssh_config) as f:
                    content = f.read()
                    if 'PermitRootLogin no' in content or 'PermitRootLogin prohibit-password' in content:
                        findings.append({"type": "info", "message": "SSH root login is restricted"})
                    if 'PasswordAuthentication no' in content:
                        findings.append({"type": "info", "message": "SSH password authentication is disabled"})
            except PermissionError:
                pass
        
        score = min(score, (access_control_score + audit_score + 100) // 3)
        
        status = "compliant" if score >= 80 else "non_compliant" if score >= 50 else "critical"
        
        return {
            "safeguard_id": "technical_safeguards",
            "status": status,
            "score": score,
            "findings": findings
        }
    
    def _check_phi_protection(self) -> Dict:
        """Check PHI protection measures"""
        findings = []
        score = 100
        
        # Common PHI locations in healthcare systems
        phi_paths = [
            '/var/lib/mysql/healthcare',
            '/var/lib/postgresql/healthcare',
            '/opt/ehr',
            '/opt/emr',
            '/opt/hipaa/phi',
            '/var/hipaa',
            '/opt/healthcare',
            '/var/www/html/patient-portal'
        ]
        
        found_phi_locations = []
        
        for path in phi_paths:
            if Path(path).exists():
                found_phi_locations.append(path)
                findings.append({"type": "info", "message": f"Potential PHI location found: {path}"})
        
        # Check for PHI encryption
        encrypted_phi = False
        for path in phi_paths:
            luks_path = Path(f"{path}.luks")
            encrypted_file = Path(f"{path}.encrypted")
            
            if luks_path.exists() or encrypted_file.exists():
                encrypted_phi = True
                findings.append({"type": "info", "message": f"Encrypted PHI storage found at {path}"})
                break
        
        if not encrypted_phi and found_phi_locations:
            score -= 25
            findings.append({
                "type": "critical",
                "message": "PHI may not be encrypted at rest"
            })
        
        # Check for PHI access logging
        phi_log_dir = Path('/var/hipaa/logs')
        if phi_log_dir.exists():
            findings.append({"type": "info", "message": "PHI access logging directory exists"})
        else:
            score -= 15
            findings.append({"type": "warning", "message": "PHI access logging should be implemented"})
        
        # Check database encryption
        db_encryption_tools = ['mysql', 'postgres']
        for db in db_encryption_tools:
            if os.system(f"which {db} >/dev/null 2>&1") == 0:
                findings.append({"type": "info", "message": f"{db} installed - ensure tables are encrypted"})
        
        self.results["phi_locations"] = found_phi_locations
        
        status = "compliant" if score >= 80 else "non_compliant" if score >= 50 else "critical"
        
        return {
            "safeguard_id": "phi_protection",
            "status": status,
            "score": score,
            "findings": findings
        }
    
    def _check_breach_notification(self) -> Dict:
        """Check breach notification procedures"""
        findings = []
        score = 100
        
        # Check for breach detection tools
        ids_tools = ['snort', 'suricata', 'aide', 'tripwire', 'ossec-hids']
        available_ids = []
        
        for tool in ids_tools:
            if os.system(f"which {tool} >/dev/null 2>&1") == 0:
                available_ids.append(tool)
        
        if available_ids:
            findings.append({
                "type": "info",
                "message": f"Intrusion detection available: {', '.join(available_ids)}"
            })
        else:
            score -= 15
            findings.append({"type": "warning", "message": "Intrusion detection system recommended"})
        
        # Check for breach notification policy
        breach_policy_files = ['/var/hipaa/breach_policy', '/opt/hipaa/breach_notification']
        has_breach_policy = any(Path(f).exists() for f in breach_policy_files)
        
        if has_breach_policy:
            findings.append({"type": "info", "message": "Breach notification policy exists"})
        else:
            score -= 20
            findings.append({
                "type": "warning",
                "message": "Breach notification policy should be documented"
            })
        
        # Check for incident response procedures
        incident_files = ['/var/hipaa/incident_response', '/opt/hipaa/ir_plan']
        has_incident_response = any(Path(f).exists() for f in incident_files)
        
        if has_incident_response:
            findings.append({"type": "info", "message": "Incident response procedures found"})
        else:
            score -= 15
            findings.append({"type": "warning", "message": "Incident response procedures should be documented"})
        
        # Check logging for breach detection
        log_aggregation = ['/var/log', '/var/log/audit']
        log_count = sum(1 for d in log_aggregation if Path(d).exists())
        
        if log_count >= 1:
            findings.append({"type": "info", "message": "System logging is configured"})
        
        status = "compliant" if score >= 80 else "non_compliant" if score >= 50 else "critical"
        
        return {
            "safeguard_id": "breach_notification",
            "status": status,
            "score": score,
            "findings": findings
        }
    
    def run_audit(self) -> Dict:
        """Run full HIPAA compliance audit"""
        logger.info("Starting HIPAA compliance audit")
        
        safeguards = [
            ("administrative_safeguards", self._check_administrative_safeguards),
            ("physical_safeguards", self._check_physical_safeguards),
            ("technical_safeguards", self._check_technical_safeguards),
            ("phi_protection", self._check_phi_protection),
            ("breach_notification", self._check_breach_notification)
        ]
        
        all_findings = []
        total_score = 0
        critical_count = 0
        non_compliant_count = 0
        
        for safeguard_id, check_func in safeguards:
            logger.info(f"Checking safeguard: {safeguard_id}")
            
            safeguard_info = self.REQUIRED_SAFEGUARDS[safeguard_id]
            result = check_func()
            
            self.results["safeguards"][safeguard_id] = {
                **safeguard_info,
                "name": safeguard_info.get("name"),
                "description": safeguard_info.get("description"),
                "standards": safeguard_info.get("standards", [])
            }
            
            all_findings.extend(result.get("findings", []))
            total_score += result["score"]
            
            if result["status"] == "critical":
                critical_count += 1
            elif result["status"] == "non_compliant":
                non_compliant_count += 1
        
        # Calculate overall score
        self.results["overall_score"] = round(total_score / len(safeguards), 1)
        
        # Determine compliance level
        if self.results["overall_score"] >= 90 and critical_count == 0:
            self.results["compliance_level"] = "compliant"
        elif self.results["overall_score"] >= 70:
            self.results["compliance_level"] = "partially_compliant"
        elif self.results["overall_score"] >= 50:
            self.results["compliance_level"] = "non_compliant"
        else:
            self.results["compliance_level"] = "critical"
        
        # Set next audit date (annually for HIPAA)
        self.results["next_audit_date"] = (datetime.now() + timedelta(days=365)).isoformat()
        
        # Add all findings
        self.results["findings"] = all_findings
        
        # Generate recommendations
        self.results["recommendations"] = self._generate_recommendations()
        
        # Save to database
        self._save_to_db()
        
        logger.info(f"HIPAA compliance audit complete. Level: {self.results['compliance_level']}")
        
        return self.results
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on findings"""
        recommendations = []
        
        safeguards = self.results.get("safeguards", {})
        
        # Check each safeguard category
        if safeguards.get("administrative_safeguards", {}).get("status") in ["non_compliant", "critical"]:
            recommendations.append("Designate a Security Officer and document risk assessment procedures")
        
        if safeguards.get("physical_safeguards", {}).get("status") in ["non_compliant", "critical"]:
            recommendations.append("Implement automatic screen lock and workstation security policies")
        
        if safeguards.get("technical_safeguards", {}).get("status") in ["non_compliant", "critical"]:
            recommendations.append("Enable audit logging and implement strong access controls")
        
        if safeguards.get("phi_protection", {}).get("status") in ["non_compliant", "critical"]:
            recommendations.append("Implement encryption for all PHI data at rest and in transit")
        
        if safeguards.get("breach_notification", {}).get("status") in ["non_compliant", "critical"]:
            recommendations.append("Develop and document breach notification procedures")
        
        # General recommendations
        recommendations.append("Conduct annual HIPAA compliance training for all workforce members")
        recommendations.append("Review and update Business Associate Agreements")
        recommendations.append("Perform regular technical safeguard assessments")
        
        if not recommendations:
            recommendations.append("Maintain current compliance posture and continue regular audits")
        
        return recommendations
    
    def _save_to_db(self):
        """Save audit results to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Save safeguard statuses
        for safeguard_id, data in self.results.get("safeguards", {}).items():
            c.execute('''INSERT OR REPLACE INTO hipaa_safeguards 
                         VALUES (?, ?, ?, ?, ?)''',
                     (safeguard_id, data.get("name"), data.get("status"),
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
        print(f"HIPAA COMPLIANCE AUDIT REPORT")
        print(f"{'='*70}")
        print(f"Audit Date: {self.results['audit_time']}")
        print(f"Overall Score: {self.results['overall_score']}/100")
        print(f"Compliance Level: {self.results['compliance_level'].upper().replace('_', ' ')}")
        print(f"Next Audit: {self.results.get('next_audit_date', 'N/A')}")
        
        print(f"\nSafeguard Status:")
        for safeguard_id, data in self.results.get("safeguards", {}).items():
            status_icon = "✅" if data.get("status") == "compliant" else "⚠️" if data.get("status") == "non_compliant" else "❌"
            print(f"  {status_icon} {data.get('name', safeguard_id)}: {data.get('score', 0)}/100 ({data.get('status', 'unknown').replace('_', ' ')})")
        
        if self.results.get("phi_locations"):
            print(f"\nPHI Locations Found ({len(self.results['phi_locations'])}):")
            for loc in self.results["phi_locations"][:5]:
                print(f"  📁 {loc}")
        
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
        description="HIPAA Compliance Agent - Health data protection compliance checking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --audit                    Run full HIPAA compliance audit
  %(prog)s --audit --verbose          Run with detailed output
  %(prog)s --report                   Generate report from last audit
        """
    )
    parser.add_argument("--audit", "-a", action="store_true", help="Run HIPAA compliance audit")
    parser.add_argument("--report", "-r", action="store_true", help="Generate report from saved results")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        agent = HIPAComplianceAgent(args.output)
        
        if args.audit or not args.report:
            agent.run_audit()
            agent.save_results()
            agent.print_report()
        elif args.report:
            if agent.db_path.exists():
                print("Loading previous audit results...")
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
