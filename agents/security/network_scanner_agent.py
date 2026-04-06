#!/usr/bin/env python3
"""
Network Scanner Agent
Discovers hosts on a network, performs port scanning, service detection,
and generates network topology maps
"""

import argparse
import json
import logging
import os
import socket
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "network_scanner.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("NetworkScanner")


@dataclass
class Host:
    """Represents a discovered host"""
    ip: str
    hostname: Optional[str] = None
    mac: Optional[str] = None
    vendor: Optional[str] = None
    status: str = "unknown"
    ports: Dict[int, Dict] = field(default_factory=dict)
    os_guess: Optional[str] = None
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())


class NetworkScanner:
    # Common ports and their services
    PORT_SERVICES = {
        20: "FTP-Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
        53: "DNS", 67: "DHCP", 68: "DHCP", 69: "TFTP", 80: "HTTP",
        110: "POP3", 119: "NNTP", 123: "NTP", 135: "MSRPC", 137: "NetBIOS-NS",
        138: "NetBIOS-DGM", 139: "NetBIOS-SSN", 143: "IMAP", 161: "SNMP",
        162: "SNMP-Trap", 389: "LDAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS",
        514: "Syslog", 587: "SMTP-Submission", 636: "LDAPS", 993: "IMAPS",
        995: "POP3S", 1433: "MSSQL", 1521: "Oracle", 3306: "MySQL",
        3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 5901: "VNC-1",
        6379: "Redis", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 9200: "Elasticsearch",
        27017: "MongoDB"
    }
    
    # OS fingerprinting heuristics
    OS_HINTS = {
        "windows": ["smb", "microsoft-ds", "rdp", "msrpc"],
        "linux": ["ssh", "linux", "unix"],
        "router": ["http", "cisco", "mikrotik", "routeros"],
        "printer": ["printer", "jetdirect", "pjl"],
        "iot": ["mqtt", "coap", "zigbee"]
    }
    
    def __init__(self, target: Optional[str] = None, output_file: Optional[str] = None):
        self.target = target
        self.output_file = output_file or f"/home/clawbot/.openclaw/workspace/data/network_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        Path("/home/clawbot/.openclaw/workspace/data").mkdir(parents=True, exist_ok=True)
        
        self.hosts: Dict[str, Host] = {}
        self.scan_results = {
            "scan_time": datetime.now().isoformat(),
            "target": target or "local_network",
            "hosts": [],
            "summary": {},
            "topology": {}
        }
        
        self._lock = threading.Lock()
    
    def _get_local_network(self) -> tuple:
        """Get local network interface and subnet"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Assume /24 subnet
            parts = local_ip.split('.')
            network = f"{parts[0]}.{parts[1]}.{parts[2]}"
            return local_ip, f"{network}.0/24"
        except Exception:
            return "127.0.0.1", "127.0.0.0/24"
    
    def _ping_host(self, ip: str, timeout: float = 1.0) -> bool:
        """Ping a host using system ping"""
        try:
            # Try with count=1 and timeout
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback: try to connect to common port
            return self._check_port_quick(ip, 80) or self._check_port_quick(ip, 443) or self._check_port_quick(ip, 22)
    
    def _check_port_quick(self, ip: str, port: int, timeout: float = 0.5) -> bool:
        """Quickly check if a port is reachable"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def _resolve_hostname(self, ip: str) -> Optional[str]:
        """Resolve IP to hostname"""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except (socket.herror, socket.gaierror):
            return None
    
    def _get_service_name(self, port: int) -> str:
        """Get service name for port"""
        return self.PORT_SERVICES.get(port, "unknown")
    
    def _guess_os(self, port_info: Dict) -> Optional[str]:
        """Guess OS based on open ports and services"""
        services_found = set()
        
        for port, info in port_info.items():
            service = info.get("service", "").lower()
            services_found.add(service)
        
        for os_name, signatures in self.OS_HINTS.items():
            if any(sig in services_found for sig in signatures):
                return os_name
        
        return "unknown"
    
    def _scan_port(self, ip: str, port: int, timeout: float = 1.0) -> Optional[Dict]:
        """Scan a single port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                return {
                    "state": "open",
                    "service": self._get_service_name(port),
                    "port": port
                }
        except Exception:
            pass
        return None
    
    def _discover_host(self, ip: str) -> Optional[Host]:
        """Discover a single host"""
        logger.info(f"Discovering host: {ip}")
        
        if not self._ping_host(ip):
            return None
        
        host = Host(ip=ip, status="up")
        
        # Try to resolve hostname
        host.hostname = self._resolve_hostname(ip)
        
        # Quick port scan for common ports
        common_ports = [22, 80, 443, 445, 3389, 8080]
        
        for port in common_ports:
            result = self._scan_port(ip, port)
            if result:
                host.ports[port] = result
        
        if host.ports:
            host.os_guess = self._guess_os(host.ports)
        
        host.last_seen = datetime.now().isoformat()
        
        logger.info(f"Host discovered: {ip} ({host.hostname or 'unknown'}) - {len(host.ports)} ports open")
        
        return host
    
    def _scan_host_ports(self, ip: str, ports: List[int]) -> Dict[int, Dict]:
        """Scan multiple ports on a host"""
        results = {}
        
        def scan_port(port):
            return port, self._scan_port(ip, port)
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(scan_port, p): p for p in ports}
            for future in as_completed(futures):
                try:
                    port, result = future.result()
                    if result:
                        results[port] = result
                except Exception:
                    pass
        
        return results
    
    def scan_network(self, network: Optional[str] = None, ports: Optional[List[int]] = None) -> Dict[str, Host]:
        """Scan a network range"""
        if not network:
            _, network = self._get_local_network()
        
        logger.info(f"Starting network scan: {network}")
        
        # Parse network
        if '/' in network:
            base_ip, mask = network.split('/')
            parts = base_ip.split('.')
            network_prefix = f"{parts[0]}.{parts[1]}.{parts[2]}"
            start = 1
            end = 254
        else:
            network_prefix = network
            start = 1
            end = 1
        
        # Generate IP list
        if end == 1 and '.' in network:
            parts = network.split('.')
            if len(parts) == 4:
                network_prefix = f"{parts[0]}.{parts[1]}.{parts[2]}"
                host_last = int(parts[3])
                start = host_last
                end = host_last
        
        ip_list = [f"{network_prefix}.{i}" for i in range(start, end + 1)]
        
        # Scan hosts in parallel
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = {executor.submit(self._discover_host, ip): ip for ip in ip_list}
            
            for future in as_completed(futures):
                try:
                    host = future.result()
                    if host:
                        with self._lock:
                            self.hosts[host.ip] = host
                except Exception as e:
                    logger.error(f"Error scanning host: {e}")
        
        # Full port scan on discovered hosts if ports specified
        if ports:
            for ip, host in self.hosts.items():
                logger.info(f"Performing detailed port scan on {ip}")
                host.ports = self._scan_host_ports(ip, ports)
        
        return self.hosts
    
    def scan_host(self, ip: str, ports: Optional[List[int]] = None) -> Host:
        """Scan a single host in detail"""
        if ports is None:
            ports = list(self.PORT_SERVICES.keys())
        
        host = Host(ip=ip, status="up")
        host.hostname = self._resolve_hostname(ip)
        host.ports = self._scan_host_ports(ip, ports)
        host.os_guess = self._guess_os(host.ports)
        host.last_seen = datetime.now().isoformat()
        
        self.hosts[ip] = host
        return host
    
    def generate_summary(self) -> Dict:
        """Generate scan summary"""
        total_hosts = len(self.hosts)
        hosts_up = sum(1 for h in self.hosts.values() if h.status == "up")
        
        all_ports = set()
        services = Counter()
        
        for host in self.hosts.values():
            for port, info in host.ports.items():
                all_ports.add(port)
                services[info.get("service", "unknown")] += 1
        
        os_counts = Counter()
        for host in self.hosts.values():
            if host.os_guess:
                os_counts[host.os_guess] += 1
        
        summary = {
            "total_hosts": total_hosts,
            "hosts_up": hosts_up,
            "unique_ports": len(all_ports),
            "top_services": dict(services.most_common(5)),
            "os_distribution": dict(os_counts),
            "scan_duration": f"{(datetime.now() - datetime.fromisoformat(self.scan_results['scan_time'])).total_seconds():.1f}s"
        }
        
        self.scan_results["summary"] = summary
        return summary
    
    def generate_topology(self) -> Dict:
        """Generate simple network topology"""
        topology = {
            "nodes": [],
            "links": []
        }
        
        local_ip, _ = self._get_local_network()
        
        for ip, host in self.hosts.items():
            node = {
                "id": ip,
                "label": host.hostname or ip,
                "type": host.os_guess or "unknown",
                "status": host.status,
                "ports": list(host.ports.keys())
            }
            topology["nodes"].append(node)
            
            # Link to gateway (simplified)
            if ip != local_ip:
                topology["links"].append({
                    "source": local_ip,
                    "target": ip,
                    "type": "direct"
                })
        
        self.scan_results["topology"] = topology
        return topology
    
    def save_results(self):
        """Save scan results to JSON"""
        # Convert hosts to serializable format
        self.scan_results["hosts"] = [
            {
                "ip": h.ip,
                "hostname": h.hostname,
                "mac": h.mac,
                "vendor": h.vendor,
                "status": h.status,
                "ports": h.ports,
                "os_guess": h.os_guess,
                "last_seen": h.last_seen
            }
            for h in self.hosts.values()
        ]
        
        self.generate_summary()
        self.generate_topology()
        
        with open(self.output_file, 'w') as f:
            json.dump(self.scan_results, f, indent=2)
        
        logger.info(f"Scan results saved to {self.output_file}")
    
    def print_results(self):
        """Print scan results to console"""
        summary = self.scan_results.get("summary", {})
        
        print(f"\n{'='*60}")
        print(f"NETWORK SCAN RESULTS")
        print(f"{'='*60}")
        print(f"Scan Time: {self.scan_results['scan_time']}")
        print(f"\nSummary:")
        print(f"  Total Hosts: {summary.get('total_hosts', 0)}")
        print(f"  Hosts Up: {summary.get('hosts_up', 0)}")
        print(f"  Unique Ports: {summary.get('unique_ports', 0)}")
        
        print(f"\nOS Distribution:")
        for os_type, count in summary.get("os_distribution", {}).items():
            print(f"  - {os_type}: {count}")
        
        print(f"\nTop Services:")
        for service, count in summary.get("top_services", {}).items():
            print(f"  - {service}: {count}")
        
        print(f"\nDiscovered Hosts:")
        for host_data in self.scan_results.get("hosts", []):
            print(f"\n  {host_data['ip']} ({host_data['hostname'] or 'unknown'})")
            print(f"    OS: {host_data['os_guess'] or 'unknown'}")
            print(f"    Status: {host_data['status']}")
            if host_data['ports']:
                open_ports = [f"{p}({v['service']})" for p, v in host_data['ports'].items()]
                print(f"    Open Ports: {', '.join(open_ports[:10])}")
        
        print(f"\nResults saved to: {self.output_file}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Network Scanner - Discover hosts and scan ports on a network",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --scan-network 192.168.1.0/24     Scan entire network
  %(prog)s --scan-host 192.168.1.1            Scan single host
  %(prog)s --discover                           Discover local network
  %(prog)s --scan-network 10.0.0.0/24 --ports 22,80,443 Full port scan
        """
    )
    parser.add_argument("--scan-network", "-n", help="Network to scan (CIDR notation)")
    parser.add_argument("--scan-host", help="Single host to scan")
    parser.add_argument("--discover", "-d", action="store_true", help="Discover local network")
    parser.add_argument("--ports", "-p", help="Ports to scan (comma-separated)")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    scanner = NetworkScanner(args.scan_network or args.scan_host, args.output)
    
    try:
        if args.scan_host:
            ports = [int(p) for p in args.ports.split(',')] if args.ports else None
            scanner.scan_host(args.scan_host, ports)
        elif args.scan_network:
            ports = [int(p) for p in args.ports.split(',')] if args.ports else None
            scanner.scan_network(args.scan_network, ports)
        elif args.discover:
            scanner.scan_network()
        else:
            # Default: discover local network
            print("No target specified, discovering local network...")
            scanner.scan_network()
        
        scanner.save_results()
        scanner.print_results()
        
    except KeyboardInterrupt:
        print("\nScan interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
