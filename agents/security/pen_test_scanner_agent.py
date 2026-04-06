#!/usr/bin/env python3
"""
Penetration Test Scanner Agent
Performs basic pen testing: port scanning, service detection, vulnerability checks
"""

import argparse
import json
import logging
import os
import socket
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "pen_test_scanner.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("PenTestScanner")


class PenTestScanner:
    def __init__(self, target: str, ports: Optional[str] = None, output_file: Optional[str] = None):
        self.target = target
        self.ports = self._parse_ports(ports)
        self.output_file = output_file or f"/home/clawbot/.openclaw/workspace/data/pen_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.results = {
            "target": target,
            "scan_time": datetime.now().isoformat(),
            "ports": {},
            "vulnerabilities": [],
            "summary": {}
        }
        Path("/home/clawbot/.openclaw/workspace/data").mkdir(parents=True, exist_ok=True)
        
    def _parse_ports(self, ports: Optional[str]) -> List[int]:
        """Parse port range string into list of ports"""
        if not ports:
            # Default common ports
            return [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 
                    3306, 3389, 5432, 5900, 8080, 8443]
        ports_list = []
        for part in ports.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                ports_list.extend(range(int(start), int(end) + 1))
            else:
                ports_list.append(int(part))
        return ports_list
    
    def _resolve_hostname(self, hostname: str) -> str:
        """Resolve hostname to IP address"""
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            logger.error(f"Cannot resolve hostname: {hostname}")
            raise ValueError(f"Cannot resolve hostname: {hostname}")
    
    def _check_port_open(self, host: str, port: int, timeout: float = 1.0) -> bool:
        """Check if a single port is open"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def _get_service_name(self, port: int) -> str:
        """Get common service name for a port"""
        services = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
            465: "SMTPS", 587: "SMTP-Submission", 993: "IMAPS",
            995: "POP3S", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
            5900: "VNC", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt"
        }
        return services.get(port, "Unknown")
    
    def _scan_port_thread(self, host: str, port: int, results: Dict):
        """Thread worker for port scanning"""
        if self._check_port_open(host, port):
            results[port] = {
                "state": "open",
                "service": self._get_service_name(port)
            }
            logger.info(f"Port {port} is OPEN ({results[port]['service']})")
    
    def scan_ports(self) -> Dict[int, Dict]:
        """Scan all specified ports on target"""
        host = self._resolve_hostname(self.target)
        logger.info(f"Starting port scan on {self.target} ({host})")
        
        results = {}
        threads = []
        
        for port in self.ports:
            t = threading.Thread(target=self._scan_port_thread, args=(host, port, results))
            threads.append(t)
            t.start()
            
            # Limit concurrent threads
            if len(threads) >= 50:
                for t in threads:
                    t.join()
                threads = []
        
        # Wait for remaining threads
        for t in threads:
            t.join()
        
        self.results["ports"] = results
        return results
    
    def _detect_vulnerabilities(self):
        """Detect basic vulnerabilities based on open ports and services"""
        vulnerabilities = []
        
        for port, info in self.results["ports"].items():
            service = info.get("service", "").lower()
            
            # FTP checks
            if port == 21:
                vulnerabilities.append({
                    "port": port,
                    "severity": "medium",
                    "type": "ftp_anonymous",
                    "description": "FTP service detected - check if anonymous login is allowed",
                    "recommendation": "Disable anonymous FTP access if not required"
                })
            
            # Telnet checks
            if port == 23:
                vulnerabilities.append({
                    "port": port,
                    "severity": "high",
                    "type": "telnet_insecure",
                    "description": "Telnet transmits data in cleartext",
                    "recommendation": "Replace Telnet with SSH for secure remote access"
                })
            
            # SSH checks
            if port == 22:
                vulnerabilities.append({
                    "port": port,
                    "severity": "low",
                    "type": "ssh_available",
                    "description": "SSH service is available",
                    "recommendation": "Ensure SSH is configured with key-based authentication"
                })
            
            # HTTP checks
            if port in [80, 8080]:
                vulnerabilities.append({
                    "port": port,
                    "severity": "medium",
                    "type": "http_unencrypted",
                    "description": "HTTP service does not use encryption",
                    "recommendation": "Consider redirecting HTTP to HTTPS"
                })
            
            # Database ports
            if port in [3306, 5432]:
                vulnerabilities.append({
                    "port": port,
                    "severity": "high",
                    "type": "database_exposed",
                    "description": f"{service} database port is exposed",
                    "recommendation": "Ensure database is not directly accessible from internet"
                })
            
            # RDP
            if port == 3389:
                vulnerabilities.append({
                    "port": port,
                    "severity": "medium",
                    "type": "rdp_exposed",
                    "description": "RDP is accessible",
                    "recommendation": "Use VPN or Network Level Authentication (NLA)"
                })
            
            # VNC
            if port == 5900:
                vulnerabilities.append({
                    "port": port,
                    "severity": "high",
                    "type": "vnc_insecure",
                    "description": "VNC service detected - often unencrypted",
                    "recommendation": "Use SSH tunnel for VNC or disable if not required"
                })
        
        self.results["vulnerabilities"] = vulnerabilities
        return vulnerabilities
    
    def generate_summary(self):
        """Generate scan summary"""
        open_ports = len(self.results["ports"])
        vuln_counts = {"high": 0, "medium": 0, "low": 0}
        
        for vuln in self.results["vulnerabilities"]:
            sev = vuln.get("severity", "low")
            if sev in vuln_counts:
                vuln_counts[sev] += 1
        
        self.results["summary"] = {
            "total_ports_scanned": len(self.ports),
            "open_ports": open_ports,
            "vulnerabilities_found": len(self.results["vulnerabilities"]),
            "by_severity": vuln_counts,
            "scan_status": "completed"
        }
        
    def save_results(self):
        """Save scan results to JSON file"""
        with open(self.output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Results saved to {self.output_file}")
    
    def run(self):
        """Execute full pen test scan"""
        try:
            logger.info(f"Starting penetration test scan on {self.target}")
            self.scan_ports()
            self._detect_vulnerabilities()
            self.generate_summary()
            self.save_results()
            
            print(f"\n{'='*60}")
            print(f"PENETRATION TEST SCAN COMPLETE")
            print(f"{'='*60}")
            print(f"Target: {self.target}")
            print(f"Open Ports Found: {self.results['summary']['open_ports']}")
            print(f"Vulnerabilities: {self.results['summary']['vulnerabilities_found']}")
            print(f"  - High: {self.results['summary']['by_severity']['high']}")
            print(f"  - Medium: {self.results['summary']['by_severity']['medium']}")
            print(f"  - Low: {self.results['summary']['by_severity']['low']}")
            print(f"Results saved to: {self.output_file}")
            print(f"{'='*60}\n")
            
            return self.results
            
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Penetration Test Scanner - Scan ports and detect basic vulnerabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s example.com                    Scan common ports on example.com
  %(prog)s 192.168.1.1 --ports 22,80,443  Scan specific ports
  %(prog)s 10.0.0.1 --ports 1-1000        Scan port range
  %(prog)s localhost --output report.json Custom output file
        """
    )
    parser.add_argument("target", help="Target host or IP address to scan")
    parser.add_argument("--ports", "-p", help="Ports to scan (default: common ports). Example: 22,80,443 or 1-1000")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        scanner = PenTestScanner(args.target, args.ports, args.output)
        scanner.run()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nScan interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
