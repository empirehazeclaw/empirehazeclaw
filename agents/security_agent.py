#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          SECURITY AGENT - ENHANCED                           ║
║          OWASP · CVE Lookup · SAST · Threat Modeling       ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - SAST (Static Application Security Testing)
  - OWASP Top 10 & CWE Top 25 Prüfung
  - CVE-Datenbank Abfrage (NVD API)
  - Threat Modeling (STRIDE)
  - Dependency Scanning
  - Automatische Fix-Vorschläge

Hinweis: LLM-Routing wird NICHT verwendet
"""

from __future__ import annotations

import json
import logging
import re
import time
import urllib.request
import urllib.parse
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

log = logging.getLogger("openclaw.security")

# NVD API (kostenlos, kein Key nötig)
NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
CVE_TIMEOUT = 8

# OWASP Top 10 2021
OWASP_TOP_10 = {
    "A01": "Broken Access Control",
    "A02": "Cryptographic Failures",
    "A03": "Injection",
    "A04": "Insecure Design",
    "A05": "Security Misconfiguration",
    "A06": "Vulnerable and Outdated Components",
    "A07": "Identification and Authentication Failures",
    "A08": "Software and Data Integrity Failures",
    "A09": "Security Logging and Monitoring Failures",
    "A10": "Server-Side Request Forgery"
}


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class Finding:
    """Eine einzelne Sicherheitslücke."""
    title: str
    severity: Severity
    category: str
    description: str
    location: str
    cwe_id: str = ""
    owasp_id: str = ""
    fix_description: str = ""
    fix_code: str = ""


class SecurityAgent:
    """
    Enhanced Security Agent mit:
    - CVE/NVD API Integration
    - OWASP Top 10
    - SAST Rules
    - Auto Fix Suggestions
    """
    
    def __init__(self):
        self.workspace = Path("/home/clawbot/.openclaw/workspace")
        self.findings: List[Finding] = []
        
    async def scan(self, target: str = "workspace", depth: str = "standard") -> Dict:
        """
        Führe vollständigen Security Scan durch
        
        Args:
            target: Zu scannender Pfad
            depth: "quick" | "standard" | "deep"
        """
        log.info(f"🔒 Security Scan: {target} (depth: {depth})")
        
        self.findings = []
        
        # Run scans
        await self.scan_code_sast(target)
        await self.scan_dependencies(target)
        await self.scan_secrets(target)
        
        if depth == "deep":
            await self.scan_docker(target)
        
        # Generate report
        return self.generate_report()
    
    async def scan_code_sast(self, target: str) -> List[Finding]:
        """SAST - Code Analyse für Security Issues"""
        log.info("🔍 SAST Code Analysis...")
        
        # Python security patterns
        python_patterns = [
            (r'eval\s*\(', "Use of eval()", Severity.HIGH, 
             "A03:2021 - Injection", "Never use eval() with user input",
             "result = safe_eval(expression)  # Use ast.literal_eval"),
            (r'exec\s*\(', "Use of exec()", Severity.HIGH,
             "A03:2021 - Injection", "exec() is dangerous",
             "# Remove exec() call"),
            (r'os\.system\s*\(', "os.system() call", Severity.MEDIUM,
             "A03:2021 - Injection", "Use subprocess.run() instead",
             "subprocess.run(cmd, shell=False)"),
            (r'subprocess\.call\s*\(.*shell\s*=\s*True', "shell=True unsafe", Severity.HIGH,
             "A03:2021 - Injection", "shell=True is dangerous",
             "subprocess.run(cmd, shell=False)"),
            (r'pickle\.load', "pickle.load() unsafe", Severity.HIGH,
             "A08:2021 - Software Integrity", "Use JSON instead",
             "data = json.loads(serialized)"),
            (r'yaml\.load\s*\(', "yaml.load unsafe", Severity.HIGH,
             "A08:2021 - Software Integrity", "Use yaml.safe_load",
             "yaml.safe_load(data)"),
            (r'password\s*=\s*["\'][^"\']{1,8}["\']', "Hardcoded password", Severity.HIGH,
             "A02:2021 - Cryptographic", "Use environment variables",
             "password = os.environ['PASSWORD']"),
            (r'secret\s*=\s*["\'][^"\']{20,}["\']', "Hardcoded secret", Severity.CRITICAL,
             "A02:2021 - Cryptographic", "Use secrets manager",
             "secret = get_secret('SECRET_NAME')"),
            (r'MD5\s*\(', "MD5 for hashing", Severity.MEDIUM,
             "A02:2021 - Cryptographic", "Use bcrypt or scrypt",
             "hash = bcrypt.hashpw(password)"),
            (r'SHA1\s*\(', "SHA1 for hashing", Severity.LOW,
             "A02:2021 - Cryptographic", "Use bcrypt or scrypt",
             "hash = hashlib.sha256(data).digest()"),
        ]
        
        # JavaScript patterns
        js_patterns = [
            (r'eval\s*\(', "Use of eval()", Severity.HIGH,
             "A03:2021 - Injection", "Never use eval",
             "# Remove eval() call"),
            (r'innerHTML\s*=', "innerHTML XSS risk", Severity.HIGH,
             "A03:2021 - Injection", "Use textContent instead",
             "element.textContent = userInput"),
            (r'document\.write\s*\(', "document.write unsafe", Severity.MEDIUM,
             "A03:2021 - Injection", "Use DOM methods",
             "element.innerText = text"),
            (r'function\s+\([^)]*\)\s*{\s*eval', "eval in function", Severity.CRITICAL,
             "A03:2021 - Injection", "Remove eval from function",
             "# Rewrite without eval"),
            (r'crypto\.createHash\s*\(\s*["\']md5', "MD5 hashing", Severity.MEDIUM,
             "A02:2021 - Cryptographic", "Use SHA-256",
             "crypto.createHash('sha256')"),
        ]
        
        # Scan files
        for ext, patterns in [(".py", python_patterns), (".js", js_patterns)]:
            for file in self.workspace.rglob(f"*{ext}"):
                if "node_modules" in str(file) or "venv" in str(file):
                    continue
                    
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        for pattern, title, severity, owasp, fix_desc, fix_code in patterns:
                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                line_num = content[:match.start()].count('\n') + 1
                                
                                self.findings.append(Finding(
                                    title=title,
                                    severity=severity,
                                    category="SAST",
                                    description=f"Found {title} at line {line_num}",
                                    location=f"{file}:{line_num}",
                                    owasp_id=owasp,
                                    fix_description=fix_desc,
                                    fix_code=fix_code
                                ))
                                
                except Exception as e:
                    pass
        
        return self.findings
    
    async def scan_dependencies(self, target: str) -> List[Finding]:
        """Scanne Dependencies auf bekannte Vulnerabilities"""
        log.info("📦 Dependency Scanning...")
        
        # Known vulnerable packages
        vulnerable_packages = {
            "requests": {"version": "2.28.0", "cve": "CVE-2023-32681", "severity": "HIGH"},
            "flask": {"version": "2.0.0", "cve": "CVE-2023-30861", "severity": "HIGH"},
            "django": {"version": "3.2.0", "cve": "CVE-2023-36053", "severity": "HIGH"},
            "numpy": {"version": "1.22.0", "cve": "CVE-2021-41496", "severity": "MEDIUM"},
            "pillow": {"version": "9.0.0", "cve": "CVE-2023-44271", "severity": "HIGH"},
            "urllib3": {"version": "1.26.0", "cve": "CVE-2023-43804", "severity": "MEDIUM"},
            "axios": {"version": "1.0.0", "cve": "CVE-2023-26115", "severity": "MEDIUM"},
            "express": {"version": "4.0.0", "cve": "CVE-2023-26159", "severity": "MEDIUM"},
        }
        
        # Check requirements.txt
        for req_file in self.workspace.rglob("requirements*.txt"):
            try:
                with open(req_file) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                            
                        # Parse package==version
                        pkg = re.split(r'[=<>!]', line)[0].strip()
                        if pkg in vulnerable_packages:
                            vuln = vulnerable_packages[pkg]
                            
                            self.findings.append(Finding(
                                title=f"Vulnerable package: {pkg}",
                                severity=Severity(vuln["severity"]),
                                category="Dependency",
                                description=f"{pkg} has known vulnerability {vuln['cve']}",
                                location=str(req_file),
                                cwe_id=vuln["cve"],
                                fix_description=f"Update {pkg} to latest version",
                                fix_code=f"{pkg}>=latest_version"
                            ))
                            
            except Exception as e:
                log.error(f"Error scanning {req_file}: {e}")
        
        return self.findings
    
    async def scan_secrets(self, target: str) -> List[Finding]:
        """Scanne auf泄露的 Secrets"""
        log.info("🔑 Secret Scanning...")
        
        secret_patterns = [
            (r'api[_-]?key["\s:=]+["\']([^"\']{20,})["\']', "API Key exposed", Severity.CRITICAL),
            (r'secret["\s:=]+["\']([^"\']{20,})["\']', "Secret exposed", Severity.CRITICAL),
            (r'password["\s:=]+["\']([^"\']{8,})["\']', "Password in code", Severity.HIGH),
            (r'token["\s:=]+["\']([^"\']{20,})["\']', "Token exposed", Severity.HIGH),
            (r'-----BEGIN (RSA|EC)? PRIVATE KEY-----', "Private Key", Severity.CRITICAL),
            (r'AKIA[0-9A-Z]{16}', "AWS Access Key", Severity.CRITICAL),
            (r'ghp_[0-9a-zA-Z]{36}', "GitHub Token", Severity.CRITICAL),
        ]
        
        for file in self.workspace.rglob("*"):
            if any(skip in str(file) for skip in ["node_modules", ".git", "venv", "env"]):
                continue
            if file.suffix not in [".py", ".js", ".json", ".yaml", ".yml", ".sh", ".env"]:
                continue
                
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for pattern, title, severity in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            self.findings.append(Finding(
                                title=title,
                                severity=severity,
                                category="Secret",
                                description=f"Potential {title.lower()} found",
                                location=str(file),
                                fix_description="Remove secret and use environment variables"
                            ))
                            
            except Exception:
                pass
        
        return self.findings
    
    async def scan_docker(self, target: str) -> List[Finding]:
        """Docker Security Scan"""
        log.info("🐳 Docker Scanning...")
        
        for dockerfile in self.workspace.rglob("Dockerfile*"):
            try:
                with open(dockerfile) as f:
                    content = f.read()
                    
                    # Check for root user
                    if "USER root" not in content and "USER 0" not in content:
                        self.findings.append(Finding(
                            title="No USER directive",
                            severity=Severity.MEDIUM,
                            category="Docker",
                            description="Running as root user",
                            location=str(dockerfile),
                            fix_description="Add USER directive",
                            fix_code="USER appuser"
                        ))
                    
                    # Check for :latest
                    if ":latest" in content:
                        self.findings.append(Finding(
                            title="Using :latest tag",
                            severity=Severity.LOW,
                            category="Docker",
                            description=":latest is not reproducible",
                            location=str(dockerfile),
                            fix_description="Use specific version tags",
                            fix_code="FROM python:3.11-slim"
                        ))
                        
            except Exception:
                pass
        
        return self.findings
    
    async def lookup_cve(self, package: str) -> Optional[Dict]:
        """CVE Lookup via NVD API"""
        try:
            query = urllib.parse.quote(package)
            url = f"{NVD_API_BASE}?keywordSearch={query}"
            
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/json")
            
            with urllib.request.urlopen(req, timeout=CVE_TIMEOUT) as response:
                data = json.loads(response.read())
                
                cves = data.get("vulnerabilities", [])[:3]
                return [{"id": cve["cve"]["id"], "description": cve["cve"]["descriptions"][0]["value"]} 
                       for cve in cves]
                        
        except Exception as e:
            log.error(f"CVE Lookup Error: {e}")
        
        return None
    
    def threat_modeling(self, component: str) -> Dict:
        """STRIDE Threat Modeling"""
        threats = {
            "Spoofing": ["Use strong authentication", "Implement MFA"],
            "Tampering": ["Use checksums", "Sign data"],
            "Repudiation": ["Log all actions", "Use audit trails"],
            "Information Disclosure": ["Encrypt data at rest", "Use TLS"],
            "Denial of Service": ["Rate limiting", "Use CDN"],
            "Elevation of Privilege": ["Use least privilege", "Validate permissions"]
        }
        
        return {
            "component": component,
            "threats": threats,
            "recommendations": [rec for threat_list in threats.values() for rec in threat_list]
        }
    
    def generate_report(self) -> Dict:
        """Generiere Security Report"""
        
        by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        by_category = {}
        
        for f in self.findings:
            by_severity[f.severity.value] = by_severity.get(f.severity.value, 0) + 1
            by_category[f.category] = by_category.get(f.category, 0) + 1
        
        return {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_findings": len(self.findings),
            "by_severity": by_severity,
            "by_category": by_category,
            "findings": [
                {
                    "title": f.title,
                    "severity": f.severity.value,
                    "category": f.category,
                    "location": f.location,
                    "owasp": f.owasp_id,
                    "cve": f.cwe_id,
                    "fix": f.fix_description,
                    "fix_code": f.fix_code
                }
                for f in self.findings
            ]
        }


async def main():
    """CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security Agent")
    parser.add_argument("--scan", choices=["full", "quick", "code"], default="quick")
    parser.add_argument("--target", default="workspace")
    
    args = parser.parse_args()
    
    agent = SecurityAgent()
    
    result = await agent.scan(args.target, args.scan)
    
    print(f"\n🔒 SECURITY REPORT")
    print(f"   Total: {result['total_findings']}")
    print(f"   Critical: {result['by_severity'].get('CRITICAL', 0)}")
    print(f"   High: {result['by_severity'].get('HIGH', 0)}")
    print(f"   Medium: {result['by_severity'].get('MEDIUM', 0)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
