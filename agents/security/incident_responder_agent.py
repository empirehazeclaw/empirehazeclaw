#!/usr/bin/env python3
"""
🚨 Incident Responder Agent
Automated incident response with triage, containment, and recovery procedures.
"""

import argparse
import json
import logging
import os
import sys
import datetime
import subprocess
import socket
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "incident_responder.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("IncidentResponder")

# Data directory
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/security")
DATA_DIR.mkdir(parents=True, exist_ok=True)

INCIDENTS_FILE = DATA_DIR / "incidents.json"
TEMPLATES_FILE = DATA_DIR / "response_templates.json"


class Severity(Enum):
    """Incident severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Status(Enum):
    """Incident status."""
    NEW = "NEW"
    TRIAGED = "TRIAGED"
    CONTAINED = "CONTAINED"
    ERADICATED = "ERADICATED"
    RECOVERED = "RECOVERED"
    CLOSED = "CLOSED"


class IncidentResponder:
    """Automated incident response capabilities."""

    def __init__(self):
        self.incident = {
            "id": self._generate_incident_id(),
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "severity": None,
            "status": Status.NEW.value,
            "title": None,
            "description": None,
            "affected_assets": [],
            "indicators": [],
            "actions_taken": [],
            "timeline": [],
            "containment_actions": [],
            "eradication_actions": [],
            "recovery_actions": [],
            "lessons_learned": []
        }
        self.timeline = self.incident["timeline"]

    def _generate_incident_id(self) -> str:
        """Generate unique incident ID."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"INC_{timestamp}"

    def _log_action(self, action: str, details: str = ""):
        """Log action to timeline."""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        self.timeline.append(entry)
        logger.info(f"[{entry['timestamp']}] {action}: {details}")

    def _save_incident(self):
        """Save incident to JSON."""
        self.incident["updated_at"] = datetime.datetime.now().isoformat()
        
        try:
            data = {"incidents": []}
            if INCIDENTS_FILE.exists():
                with open(INCIDENTS_FILE, 'r') as f:
                    data = json.load(f)
            
            # Update or add incident
            found = False
            for i, inc in enumerate(data["incidents"]):
                if inc["id"] == self.incident["id"]:
                    data["incidents"][i] = self.incident
                    found = True
                    break
            
            if not found:
                data["incidents"].append(self.incident)
            
            # Keep last 100 incidents
            data["incidents"] = data["incidents"][-100:]
            
            with open(INCIDENTS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Incident saved: {self.incident['id']}")
        except Exception as e:
            logger.error(f"Failed to save incident: {e}")

    def create_incident(
        self,
        title: str,
        description: str,
        severity: str = "MEDIUM",
        affected_assets: List[str] = None
    ) -> Dict:
        """Create new incident."""
        self.incident["title"] = title
        self.incident["description"] = description
        self.incident["severity"] = severity
        self.incident["affected_assets"] = affected_assets or []
        
        self._log_action("INCIDENT_CREATED", f"Title: {title}, Severity: {severity}")
        
        # Auto-triage based on severity
        if severity in ["CRITICAL", "HIGH"]:
            self._log_action("ALERT_TRIGGERED", "High severity incident - immediate response required")
        
        self._save_incident()
        return self.incident

    def triage(self, force: bool = False) -> Dict:
        """Perform incident triage."""
        logger.info("Performing incident triage...")
        
        self.incident["status"] = Status.TRIAGED.value
        
        triage_results = {
            "id": self.incident["id"],
            "checks_performed": [],
            "initial_assessment": None,
            "recommended_actions": []
        }
        
        # Severity-based triage
        severity = self.incident.get("severity", "MEDIUM")
        
        triage_results["checks_performed"].append({
            "check": "severity_assessment",
            "result": severity,
            "recommendation": self._get_severity_recommendation(severity)
        })
        
        # Check affected assets
        assets = self.incident.get("affected_assets", [])
        if assets:
            triage_results["checks_performed"].append({
                "check": "affected_assets",
                "result": f"{len(assets)} asset(s)",
                "assets": assets
            })
        
        # Network assessment
        triage_results["checks_performed"].append({
            "check": "network_connections",
            "result": "Scanning for suspicious connections..."
        })
        
        try:
            result = subprocess.run(
                ["ss", "-tunap"],
                capture_output=True,
                text=True,
                timeout=5
            )
            suspicious = []
            for line in result.stdout.split('\n'):
                for port in ["4444", "5555", "31337", "6666", "6667"]:
                    if f":{port}" in line:
                        suspicious.append(line.strip())
            
            if suspicious:
                triage_results["checks_performed"].append({
                    "check": "suspicious_ports",
                    "result": f"Found {len(suspicious)} suspicious connection(s)",
                    "details": suspicious
                })
                self.incident["indicators"].append({
                    "type": "suspicious_network",
                    "description": "Suspicious network activity detected",
                    "data": suspicious
                })
        except Exception as e:
            logger.debug(f"Network scan failed: {e}")
        
        # Process check
        triage_results["checks_performed"].append({
            "check": "running_processes",
            "result": "Checking for suspicious processes..."
        })
        
        try:
            suspicious_procs = []
            suspicious_patterns = ["nc ", "ncat", "msfvenom", "/dev/tcp"]
            
            for proc_dir in Path("/proc").iterdir():
                if not proc_dir.name.isdigit():
                    continue
                try:
                    with open(proc_dir / "cmdline", 'r') as f:
                        cmdline = f.read().replace('\x00', ' ')
                        for pattern in suspicious_patterns:
                            if pattern in cmdline:
                                suspicious_procs.append({
                                    "pid": proc_dir.name,
                                    "cmd": cmdline[:80]
                                })
                except:
                    pass
            
            if suspicious_procs:
                triage_results["checks_performed"].append({
                    "check": "suspicious_processes",
                    "result": f"Found {len(suspicious_procs)} suspicious process(es)",
                    "details": suspicious_procs
                })
        except Exception as e:
            logger.debug(f"Process scan failed: {e}")
        
        # Generate assessment
        triage_results["initial_assessment"] = self._generate_assessment()
        triage_results["recommended_actions"] = self._get_recommended_actions(severity)
        
        self._log_action("TRIAGE_COMPLETED", f"Initial assessment: {triage_results['initial_assessment']}")
        self._save_incident()
        
        return triage_results

    def _get_severity_recommendation(self, severity: str) -> str:
        """Get recommendation based on severity."""
        recommendations = {
            "CRITICAL": "Immediate response required - activate incident response team",
            "HIGH": "Urgent response needed - begin containment within 1 hour",
            "MEDIUM": "Response within 4 hours - begin investigation",
            "LOW": "Response within 24 hours - monitor and document",
            "INFO": "Log for review - no immediate action required"
        }
        return recommendations.get(severity, "Unknown severity")

    def _generate_assessment(self) -> str:
        """Generate initial assessment."""
        severity = self.incident.get("severity", "MEDIUM")
        indicators = len(self.incident.get("indicators", []))
        assets = len(self.incident.get("affected_assets", []))
        
        if severity == "CRITICAL":
            return f"Active incident requiring immediate containment. {indicators} indicator(s), {assets} asset(s) affected."
        elif severity == "HIGH":
            return f"Significant incident with potential for spread. {indicators} indicator(s), {assets} asset(s) affected."
        else:
            return f"Incident under investigation. {indicators} indicator(s) found."

    def _get_recommended_actions(self, severity: str) -> List[str]:
        """Get recommended actions based on severity."""
        base_actions = [
            "Document all findings in incident record",
            "Notify incident response team",
            "Preserve evidence for analysis"
        ]
        
        if severity in ["CRITICAL", "HIGH"]:
            base_actions.extend([
                "ISOLATE affected systems from network",
                "Begin active containment procedures",
                "Activate backup/recovery procedures",
                "Notify management and stakeholders"
            ])
        
        return base_actions

    def contain(self, action: str = "auto") -> Dict:
        """Perform containment actions."""
        logger.info("Performing containment...")
        
        containment_results = {
            "actions_taken": [],
            "status": "success"
        }
        
        if action == "auto":
            severity = self.incident.get("severity", "MEDIUM")
            
            if severity in ["CRITICAL", "HIGH"]:
                # Aggressive containment
                containment_results["actions_taken"].append({
                    "action": "network_isolation_recommended",
                    "target": "affected_systems",
                    "method": "firewall_rules_or_disconnect",
                    "status": "recommended"
                })
                
                # Kill suspicious processes
                try:
                    for proc_dir in Path("/proc").iterdir():
                        if not proc_dir.name.isdigit():
                            continue
                        try:
                            with open(proc_dir / "cmdline", 'r') as f:
                                cmdline = f.read()
                                if b"msfvenom" in cmdline or b"/dev/tcp" in cmdline:
                                    pid = int(proc_dir.name)
                                    try:
                                        os.kill(pid, 9)
                                        containment_results["actions_taken"].append({
                                            "action": "process_killed",
                                            "pid": pid,
                                            "status": "success"
                                        })
                                        self._log_action("PROCESS_KILLED", f"PID {pid}")
                                    except:
                                        pass
                        except:
                            pass
                except Exception as e:
                    logger.warning(f"Process cleanup failed: {e}")
            else:
                containment_results["actions_taken"].append({
                    "action": "monitoring_enhanced",
                    "description": "Increase monitoring on affected systems",
                    "status": "completed"
                })
        
        self.incident["status"] = Status.CONTAINED.value
        self.incident["containment_actions"].extend(containment_results["actions_taken"])
        self._log_action("CONTAINMENT_COMPLETED", f"{len(containment_results['actions_taken'])} action(s) taken")
        self._save_incident()
        
        return containment_results

    def eradicate(self) -> Dict:
        """Perform eradication."""
        logger.info("Performing eradication...")
        
        eradication_results = {
            "actions_taken": [],
            "malware_removed": [],
            "vulnerabilities_patched": []
        }
        
        # Malware removal steps
        eradication_results["actions_taken"].append({
            "action": "malware_scan",
            "command": "ClamAV or similar AV scan",
            "status": "recommended"
        })
        
        # Patch vulnerabilities
        eradication_results["actions_taken"].append({
            "action": "patch_management",
            "description": "Apply security patches to affected systems",
            "status": "recommended"
        })
        
        # Reset credentials
        eradication_results["actions_taken"].append({
            "action": "credential_reset",
            "description": "Reset passwords for affected accounts",
            "status": "recommended"
        })
        
        # Review and close backdoors
        eradication_results["actions_taken"].append({
            "action": "backdoor_review",
            "description": "Check for and remove any persistence mechanisms",
            "status": "recommended"
        })
        
        self.incident["status"] = Status.ERADICATED.value
        self.incident["eradication_actions"].extend(eradication_results["actions_taken"])
        self._log_action("ERADICATION_COMPLETED")
        self._save_incident()
        
        return eradication_results

    def recover(self) -> Dict:
        """Perform recovery."""
        logger.info("Performing recovery...")
        
        recovery_results = {
            "actions_taken": [],
            "systems_restored": []
        }
        
        recovery_results["actions_taken"].append({
            "action": "system_restoration",
            "description": "Restore systems from clean backups",
            "status": "recommended"
        })
        
        recovery_results["actions_taken"].append({
            "action": "data_verification",
            "description": "Verify integrity of restored data",
            "status": "recommended"
        })
        
        recovery_results["actions_taken"].append({
            "action": "service_resumption",
            "description": "Gradually resume normal operations",
            "status": "recommended"
        })
        
        recovery_results["actions_taken"].append({
            "action": "monitoring_validation",
            "description": "Validate security controls are functioning",
            "status": "recommended"
        })
        
        self.incident["status"] = Status.RECOVERED.value
        self.incident["recovery_actions"].extend(recovery_results["actions_taken"])
        self._log_action("RECOVERY_COMPLETED")
        self._save_incident()
        
        return recovery_results

    def add_lesson(self, lesson: str):
        """Add lessons learned."""
        self.incident["lessons_learned"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "lesson": lesson
        })
        self._log_action("LESSON_ADDED", lesson)
        self._save_incident()

    def close(self, summary: str = "") -> Dict:
        """Close the incident."""
        self.incident["status"] = Status.CLOSED.value
        self.incident["closed_at"] = datetime.datetime.now().isoformat()
        self.incident["summary"] = summary
        
        self._log_action("INCIDENT_CLOSED", summary or "No summary provided")
        self._save_incident()
        
        return self.incident

    def generate_report(self) -> str:
        """Generate incident report."""
        report = []
        report.append("=" * 60)
        report.append("🚨 INCIDENT RESPONSE REPORT")
        report.append("=" * 60)
        report.append(f"Incident ID: {self.incident['id']}")
        report.append(f"Title: {self.incident.get('title', 'N/A')}")
        report.append(f"Severity: {self.incident.get('severity', 'N/A')}")
        report.append(f"Status: {self.incident['status']}")
        report.append(f"Created: {self.incident['created_at']}")
        report.append(f"Updated: {self.incident.get('updated_at', 'N/A')}")
        report.append("")
        
        if self.incident.get("description"):
            report.append("📝 DESCRIPTION:")
            report.append(f"  {self.incident['description']}")
            report.append("")
        
        if self.incident.get("affected_assets"):
            report.append("💻 AFFECTED ASSETS:")
            for asset in self.incident["affected_assets"]:
                report.append(f"  • {asset}")
            report.append("")
        
        if self.incident.get("indicators"):
            report.append("🔍 INDICATORS OF COMPROMISE:")
            for ind in self.incident["indicators"]:
                report.append(f"  • [{ind.get('type', 'unknown')}] {ind.get('description', '')}")
            report.append("")
        
        if self.incident.get("timeline"):
            report.append("📅 TIMELINE:")
            for entry in self.incident["timeline"][-10:]:
                report.append(f"  • {entry['timestamp']}: {entry['action']}")
                if entry.get('details'):
                    report.append(f"    {entry['details']}")
            report.append("")
        
        if self.incident.get("lessons_learned"):
            report.append("📚 LESSONS LEARNED:")
            for lesson in self.incident["lessons_learned"]:
                report.append(f"  • {lesson['lesson']}")
            report.append("")
        
        report.append("=" * 60)
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="🚨 Incident Responder Agent - Automated incident response",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --create "Suspicious Login" "Multiple failed logins detected" --severity HIGH
  %(prog)s --triage --incident INC_20240315_120000
  %(prog)s --contain
  %(prog)s --list-incidents
  %(prog)s --close --summary "Incident resolved"
  
This tool is for AUTHORIZED incident response only.
        """
    )
    
    parser.add_argument("--create", nargs=2, metavar=("TITLE", "DESCRIPTION"),
                       help="Create new incident")
    parser.add_argument("--severity", choices=["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
                       default="MEDIUM", help="Incident severity")
    parser.add_argument("--assets", nargs="+", help="Affected assets")
    parser.add_argument("--triage", action="store_true", help="Run triage on incident")
    parser.add_argument("--contain", action="store_true", help="Run containment")
    parser.add_argument("--eradicate", action="store_true", help="Run eradication")
    parser.add_argument("--recover", action="store_true", help="Run recovery")
    parser.add_argument("--close", action="store_true", help="Close incident")
    parser.add_argument("--summary", help="Closing summary")
    parser.add_argument("--lesson", help="Add lessons learned")
    parser.add_argument("--incident", "-i", help="Incident ID to work with")
    parser.add_argument("--list-incidents", "-l", action="store_true", help="List incidents")
    parser.add_argument("--output", "-o", help="Output file for report (JSON)")
    
    args = parser.parse_args()

    responder = IncidentResponder()

    # Load existing incident if specified
    if args.incident:
        try:
            with open(INCIDENTS_FILE, 'r') as f:
                data = json.load(f)
            for inc in data["incidents"]:
                if inc["id"] == args.incident:
                    responder.incident = inc
                    break
            else:
                print(f"Incident {args.incident} not found.")
                sys.exit(1)
        except FileNotFoundError:
            print("No incidents found.")
            sys.exit(1)

    if args.list_incidents:
        try:
            with open(INCIDENTS_FILE, 'r') as f:
                data = json.load(f)
            print(f"\n🚨 Found {len(data['incidents'])} incidents:\n")
            for inc in data["incidents"][-20:]:
                print(f"  • {inc['id']}")
                print(f"    Title: {inc.get('title', 'N/A')}")
                print(f"    Severity: {inc.get('severity', 'N/A')}")
                print(f"    Status: {inc['status']}")
                print(f"    Time: {inc['created_at']}")
                print()
        except FileNotFoundError:
            print("No incidents found.")
        sys.exit(0)

    if args.create:
        responder.create_incident(
            title=args.create[0],
            description=args.create[1],
            severity=args.severity,
            affected_assets=args.assets
        )
        print(f"\n✅ Created incident: {responder.incident['id']}")
        print(responder.generate_report())
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(responder.incident, f, indent=2)
            print(f"\n📄 Incident saved to {args.output}")
        sys.exit(0)

    if args.triage:
        results = responder.triage()
        print("\n🔍 TRIAGE RESULTS:")
        print(json.dumps(results, indent=2))
        print("\n" + responder.generate_report())

    if args.contain:
        results = responder.contain()
        print("\n🔒 CONTAINMENT RESULTS:")
        print(json.dumps(results, indent=2))

    if args.eradicate:
        results = responder.eradicate()
        print("\n🧹 ERADICATION RESULTS:")
        print(json.dumps(results, indent=2))

    if args.recover:
        results = responder.recover()
        print("\n♻️ RECOVERY RESULTS:")
        print(json.dumps(results, indent=2))

    if args.lesson:
        responder.add_lesson(args.lesson)
        print(f"\n✅ Added lesson: {args.lesson}")

    if args.close:
        responder.close(args.summary or "")
        print("\n✅ INCIDENT CLOSED")
        print(responder.generate_report())

    # If no action specified, show current incident
    if not any([args.create, args.triage, args.contain, args.eradicate, 
                args.recover, args.close, args.list_incidents, args.lesson]):
        parser.print_help()


if __name__ == "__main__":
    main()
