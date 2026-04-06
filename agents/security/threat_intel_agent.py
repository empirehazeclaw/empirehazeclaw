#!/usr/bin/env python3
"""
🎯 Threat Intelligence Agent
收集、分析、关联威胁情报，支持多数据源集成。
"""

import argparse
import json
import logging
import os
import sys
import datetime
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "threat_intel.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ThreatIntel")

# Data directory
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/security")
DATA_DIR.mkdir(parents=True, exist_ok=True)

THREATS_FILE = DATA_DIR / "threats.json"
IOC_FILE = DATA_DIR / "indicators_of_compromise.json"
CAMPAIGNS_FILE = DATA_DIR / "campaigns.json"


class ThreatIntel:
    """威胁情报收集和分析。"""

    # 常见恶意软件哈希 (示例)
    KNOWN_MALWARE = {
        "44d88612fea8a8f36de82e1278abb02f": "EICAR-Test-File",
        "e3b0c44298fc1c149afbf4c8996fb924": "Empty file",
        "a7f0b56771a81c4e1e9d4f3c2d8e5f1a": "Generic-Trojan",
    }
    
    # 常见恶意域名模式
    SUSPICIOUS_TLDS = {".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top"}
    
    # 常见 C2 模式
    C2_PATTERNS = [
        r"^http://[a-z0-9.-]+\.tk",
        r"^http://[0-9.]+\.(4444|5555|6666|7777)",
        r"onion\.link|tor2web",
    ]

    def __init__(self):
        self.threats = []
        self.iocs = []
        self.campaigns = []
        self._load_data()

    def _load_data(self):
        """加载已存储的威胁数据。"""
        try:
            if THREATS_FILE.exists():
                with open(THREATS_FILE, 'r') as f:
                    self.threats = json.load(f).get("threats", [])
            
            if IOC_FILE.exists():
                with open(IOC_FILE, 'r') as f:
                    self.iocs = json.load(f).get("iocs", [])
            
            if CAMPAIGNS_FILE.exists():
                with open(CAMPAIGNS_FILE, 'r') as f:
                    self.campaigns = json.load(f).get("campaigns", [])
        except Exception as e:
            logger.warning(f"Could not load threat data: {e}")

    def _save_threats(self):
        """保存威胁数据。"""
        try:
            with open(THREATS_FILE, 'w') as f:
                json.dump({"threats": self.threats[-100:]}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save threats: {e}")

    def _save_iocs(self):
        """保存 IOC 数据。"""
        try:
            with open(IOC_FILE, 'w') as f:
                json.dump({"iocs": self.iocs[-500:]}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save IOCs: {e}")

    def calculate_hash(self, content: str) -> str:
        """计算字符串的 MD5 哈希。"""
        return hashlib.md5(content.encode()).hexdigest()

    def analyze_hash(self, hash_value: str) -> Dict:
        """分析哈希值。"""
        result = {
            "input": hash_value,
            "type": self._identify_hash_type(hash_value),
            "known_malware": None,
            "threat_level": "unknown",
            "details": []
        }
        
        # 检查已知恶意软件
        if hash_value.lower() in self.KNOWN_MALWARE:
            result["known_malware"] = self.KNOWN_MALWARE[hash_value.lower()]
            result["threat_level"] = "high"
            result["details"].append(f"Known malware: {result['known_malware']}")
        
        # 检查哈希类型
        if result["type"]:
            result["details"].append(f"Hash type: {result['type']}")
        
        return result

    def _identify_hash_type(self, hash_value: str) -> Optional[str]:
        """识别哈希类型。"""
        if not hash_value:
            return None
        
        length = len(hash_value)
        if length == 32:
            return "MD5"
        elif length == 40:
            return "SHA-1"
        elif length == 64:
            return "SHA-256"
        elif length == 128:
            return "SHA-512"
        return None

    def analyze_domain(self, domain: str) -> Dict:
        """分析域名。"""
        result = {
            "input": domain,
            "suspicious_tld": False,
            "suspicious_pattern": False,
            "typosquatting_candidates": [],
            "threat_level": "low",
            "details": []
        }
        
        # 检查 TLD
        for tld in self.SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                result["suspicious_tld"] = True
                result["threat_level"] = "medium"
                result["details"].append(f"Suspicious TLD: {tld}")
        
        # 检查模式
        for pattern in self.C2_PATTERNS:
            if re.match(pattern, domain, re.IGNORECASE):
                result["suspicious_pattern"] = True
                result["threat_level"] = "high"
                result["details"].append(f"Matches C2 pattern: {pattern}")
        
        # 生成 typosquatting 候选
        result["typosquatting_candidates"] = self._generate_typosquats(domain)
        
        return result

    def _generate_typosquats(self, domain: str) -> List[str]:
        """生成 typosquatting 候选域名。"""
        candidates = []
        
        if not domain or "." not in domain:
            return candidates
        
        try:
            parts = domain.rsplit(".", 1)
            name = parts[0]
            tld = parts[1] if len(parts) > 1 else ""
            
            # 字符替换
            for char in ["i", "l", "o", "e", "a"]:
                for replacement in ["1", "0"]:
                    if char in name:
                        candidates.append(name.replace(char, replacement) + "." + tld)
            
            # 字符插入
            for i in range(len(name)):
                for char in ["-", ".", "1"]:
                    candidates.append(name[:i] + char + name[i:] + "." + tld)
            
            # 字符删除
            for i in range(len(name)):
                if len(name) > 3:
                    candidates.append(name[:i] + name[i+1:] + "." + tld)
            
        except Exception as e:
            logger.debug(f"Typosquatting generation failed: {e}")
        
        return list(set(candidates))[:5]

    def analyze_ip(self, ip: str) -> Dict:
        """分析 IP 地址。"""
        result = {
            "input": ip,
            "is_private": self._is_private_ip(ip),
            "is_loopback": self._is_loopback_ip(ip),
            "threat_level": "info",
            "details": []
        }
        
        if result["is_private"]:
            result["details"].append("Private IP address")
        elif result["is_loopback"]:
            result["details"].append("Loopback address")
        
        # 检查常见恶意端口
        suspicious_ports = [4444, 5555, 6666, 31337]
        
        # 检查格式
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
            octets = [int(x) for x in ip.split(".")]
            if len(octets) == 4:
                if octets[0] in [192, 10, 172]:
                    result["details"].append("Common private/CGNAT range")
                elif octets[0] >= 224:
                    result["details"].append("Multicast/Reserved range")
        
        return result

    def _is_private_ip(self, ip: str) -> bool:
        """检查是否为私有 IP。"""
        try:
            parts = [int(x) for x in ip.split(".")]
            if len(parts) != 4:
                return False
            
            # 10.0.0.0/8
            if parts[0] == 10:
                return True
            # 172.16.0.0/12
            if parts[0] == 172 and 16 <= parts[1] <= 31:
                return True
            # 192.168.0.0/16
            if parts[0] == 192 and parts[1] == 168:
                return True
            # 169.254.0.0/16 (link-local)
            if parts[0] == 169 and parts[1] == 254:
                return True
            
            return False
        except:
            return False

    def _is_loopback_ip(self, ip: str) -> bool:
        """检查是否为回环地址。"""
        return ip.startswith("127.")

    def analyze_url(self, url: str) -> Dict:
        """分析 URL。"""
        result = {
            "input": url,
            "suspicious": False,
            "threat_level": "low",
            "indicators": [],
            "extracted_iocs": []
        }
        
        # 提取域名
        domain_match = re.search(r"https?://([^/]+)", url, re.IGNORECASE)
        if domain_match:
            domain = domain_match.group(1)
            result["extracted_iocs"].append({"type": "domain", "value": domain})
            
            # 分析域名
            domain_analysis = self.analyze_domain(domain)
            if domain_analysis["threat_level"] != "low":
                result["suspicious"] = True
                result["threat_level"] = domain_analysis["threat_level"]
                result["indicators"].extend(domain_analysis["details"])
        
        # 检查可疑模式
        suspicious_patterns = [
            (r"\.exe[?/]", "Executable download"),
            (r"\.zip[?/].*password", "Password-protected archive"),
            (r"@", "Possible email spoofing"),
            (r"bit\.ly|tinyurl|goo\.gl", "URL shortener"),
            (r"\.\./", "Path traversal attempt"),
            (r"<script", "Possible XSS"),
            (r"union.*select", "SQL injection attempt"),
        ]
        
        for pattern, desc in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                result["suspicious"] = True
                result["indicators"].append(f"Suspicious pattern: {desc}")
                if result["threat_level"] == "low":
                    result["threat_level"] = "medium"
        
        return result

    def analyze_file_path(self, path: str) -> Dict:
        """分析文件路径。"""
        result = {
            "path": path,
            "suspicious": False,
            "threat_level": "low",
            "indicators": []
        }
        
        # 可疑路径模式
        suspicious_patterns = [
            (r"/tmp/.*", "Temporary directory access"),
            (r"AppData.*Temp", "Windows temp files"),
            (r"\.\./", "Path traversal"),
            (r"\\\\.*\\\\.*\\\\", "UNC path"),
            (r"~.*\.sh$", "Shell script in home"),
            (r"\.(bat|cmd|vbs|ps1|scr|pif)$", "Windows script/executable"),
            (r"\.(vbscript|js|hta)$", "Script file"),
        ]
        
        for pattern, desc in suspicious_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                result["suspicious"] = True
                result["indicators"].append(desc)
                if result["threat_level"] == "low":
                    result["threat_level"] = "medium"
        
        # 检查可疑文件名
        suspicious_names = ["hack", "exploit", "backdoor", "rootkit", "keylog", "stealer"]
        path_lower = path.lower()
        for name in suspicious_names:
            if name in path_lower:
                result["suspicious"] = True
                result["threat_level"] = "high"
                result["indicators"].append(f"Suspicious keyword: {name}")
        
        return result

    def add_ioc(self, ioc_type: str, value: str, tags: List[str] = None, 
                threat_level: str = "unknown") -> Dict:
        """添加 IOC。"""
        ioc = {
            "id": f"ioc_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": ioc_type,
            "value": value,
            "tags": tags or [],
            "threat_level": threat_level,
            "first_seen": datetime.datetime.now().isoformat(),
            "last_seen": datetime.datetime.now().isoformat(),
            "confidence": "medium",
            "source": "manual"
        }
        
        # 检查是否已存在
        for existing in self.iocs:
            if existing["type"] == ioc_type and existing["value"] == value:
                existing["last_seen"] = ioc["last_seen"]
                existing["count"] = existing.get("count", 1) + 1
                self._save_iocs()
                return existing
        
        self.iocs.append(ioc)
        self._save_iocs()
        
        return ioc

    def add_threat(self, name: str, category: str, description: str,
                  severity: str = "MEDIUM", actors: List[str] = None,
                  malware: List[str] = None) -> Dict:
        """添加威胁信息。"""
        threat = {
            "id": f"threat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "name": name,
            "category": category,
            "description": description,
            "severity": severity,
            "actors": actors or [],
            "malware": malware or [],
            "created": datetime.datetime.now().isoformat(),
            "last_updated": datetime.datetime.now().isoformat(),
            "active": True
        }
        
        self.threats.append(threat)
        self._save_threats()
        
        return threat

    def correlate_iocs(self, iocs: List[Dict]) -> Dict:
        """关联 IOC。"""
        correlation = {
            "total_iocs": len(iocs),
            "by_type": {},
            "linked_threats": [],
            "sightings": 0
        }
        
        # 按类型分组
        for ioc in iocs:
            ioc_type = ioc.get("type", "unknown")
            if ioc_type not in correlation["by_type"]:
                correlation["by_type"][ioc_type] = []
            correlation["by_type"][ioc_type].append(ioc.get("value"))
        
        # 关联威胁
        for threat in self.threats:
            for ioc in iocs:
                value = ioc.get("value", "").lower()
                threat_name = threat.get("name", "").lower()
                
                if value in threat_name or any(
                    mal.lower() in value for mal in threat.get("malware", [])
                ):
                    if threat not in correlation["linked_threats"]:
                        correlation["linked_threats"].append(threat["name"])
        
        correlation["sightings"] = sum(ioc.get("count", 1) for ioc in iocs)
        
        return correlation

    def search_threats(self, query: str) -> List[Dict]:
        """搜索威胁。"""
        query_lower = query.lower()
        results = []
        
        for threat in self.threats:
            if (query_lower in threat.get("name", "").lower() or
                query_lower in threat.get("description", "").lower() or
                query_lower in threat.get("category", "").lower()):
                results.append(threat)
        
        return results

    def generate_threat_report(self, threat: Dict) -> str:
        """生成威胁报告。"""
        report = []
        report.append("=" * 60)
        report.append("🎯 THREAT INTELLIGENCE REPORT")
        report.append("=" * 60)
        report.append(f"Threat ID: {threat.get('id', 'N/A')}")
        report.append(f"Name: {threat.get('name', 'N/A')}")
        report.append(f"Category: {threat.get('category', 'N/A')}")
        report.append(f"Severity: {threat.get('severity', 'N/A')}")
        report.append(f"Status: {'Active' if threat.get('active') else 'Inactive'}")
        report.append("")
        
        if threat.get("description"):
            report.append("📝 DESCRIPTION:")
            report.append(f"  {threat['description']}")
            report.append("")
        
        if threat.get("actors"):
            report.append("🎭 ASSOCIATED ACTORS:")
            for actor in threat["actors"]:
                report.append(f"  • {actor}")
            report.append("")
        
        if threat.get("malware"):
            report.append("🐛 ASSOCIATED MALWARE:")
            for mal in threat["malware"]:
                report.append(f"  • {mal}")
            report.append("")
        
        report.append(f"Created: {threat.get('created', 'N/A')}")
        report.append(f"Last Updated: {threat.get('last_updated', 'N/A')}")
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)

    def get_threat_summary(self) -> str:
        """获取威胁摘要。"""
        summary = []
        summary.append("=" * 60)
        summary.append("🎯 THREAT INTELLIGENCE SUMMARY")
        summary.append("=" * 60)
        summary.append(f"Total Threats: {len(self.threats)}")
        summary.append(f"Total IOCs: {len(self.iocs)}")
        summary.append(f"Active Campaigns: {len([t for t in self.threats if t.get('active')])}")
        summary.append("")
        
        # 按严重性分组
        by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for threat in self.threats:
            sev = threat.get("severity", "INFO")
            if sev in by_severity:
                by_severity[sev] += 1
        
        summary.append("📊 BY SEVERITY:")
        for sev, count in by_severity.items():
            if count > 0:
                summary.append(f"  {sev}: {count}")
        summary.append("")
        
        # IOC 统计
        ioc_types = {}
        for ioc in self.iocs:
            t = ioc.get("type", "unknown")
            ioc_types[t] = ioc_types.get(t, 0) + 1
        
        if ioc_types:
            summary.append("🔍 IOC TYPES:")
            for t, count in ioc_types.items():
                summary.append(f"  {t}: {count}")
            summary.append("")
        
        # 最近活动
        if self.threats:
            summary.append("🕐 RECENT THREATS:")
            for threat in self.threats[-5:]:
                summary.append(f"  • [{threat['severity']}] {threat['name']}")
        
        summary.append("")
        summary.append("=" * 60)
        
        return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(
        description="🎯 Threat Intelligence Agent - Threat intel collection and analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --analyze-hash 44d88612fea8a8f36de82e1278abb02f
  %(prog)s --analyze-domain suspicious-site.xyz
  %(prog)s --analyze-ip 192.168.1.1
  %(prog)s --analyze-url "http://malware.com/payload.exe"
  %(prog)s --analyze-path "/tmp/suspicious_script.sh"
  %(prog)s --add-ioc domain evil-domain.xyz --tags "c2,malware" --threat-level high
  %(prog)s --add-threat "Emotet" --category "Malware" --severity HIGH
  %(prog)s --search "ransomware"
  %(prog)s --list-threats
  %(prog)s --summary
  
Note: This tool is for authorized threat intelligence activities only.
        """
    )
    
    parser.add_argument("--analyze-hash", help="Analyze file hash (MD5/SHA1/SHA256)")
    parser.add_argument("--analyze-domain", help="Analyze domain for threats")
    parser.add_argument("--analyze-ip", help="Analyze IP address")
    parser.add_argument("--analyze-url", help="Analyze URL for threats")
    parser.add_argument("--analyze-path", help="Analyze file path for threats")
    parser.add_argument("--add-ioc", nargs=2, metavar=("TYPE", "VALUE"),
                       help="Add IOC (type: hash|domain|ip|url|email)")
    parser.add_argument("--add-threat", help="Add threat intel entry")
    parser.add_argument("--category", default="Unknown", help="Threat category")
    parser.add_argument("--severity", choices=["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
                       default="MEDIUM", help="Threat severity")
    parser.add_argument("--description", help="Threat description")
    parser.add_argument("--tags", nargs="+", help="IOC tags")
    parser.add_argument("--threat-level", default="unknown",
                       choices=["critical", "high", "medium", "low", "info", "unknown"],
                       help="Threat level for IOC")
    parser.add_argument("--actors", nargs="+", help="Associated threat actors")
    parser.add_argument("--malware", nargs="+", help="Associated malware")
    parser.add_argument("--search", help="Search threat database")
    parser.add_argument("--list-threats", "-l", action="store_true", help="List all threats")
    parser.add_argument("--list-iocs", action="store_true", help="List all IOCs")
    parser.add_argument("--summary", "-s", action="store_true", help="Show threat summary")
    parser.add_argument("--correlate", help="Correlate IOCs from file (JSON)")
    parser.add_argument("--output", "-o", help="Output file for results (JSON)")
    
    args = parser.parse_args()

    intel = ThreatIntel()

    if args.analyze_hash:
        print(f"\n🔍 Analyzing hash: {args.analyze_hash}\n")
        result = intel.analyze_hash(args.analyze_hash)
        print(json.dumps(result, indent=2))

    elif args.analyze_domain:
        print(f"\n🔍 Analyzing domain: {args.analyze_domain}\n")
        result = intel.analyze_domain(args.analyze_domain)
        print(json.dumps(result, indent=2))
        
        if result.get("typosquatting_candidates"):
            print("\n🔀 Typosquatting candidates:")
            for candidate in result["typosquatting_candidates"]:
                print(f"  • {candidate}")

    elif args.analyze_ip:
        print(f"\n🔍 Analyzing IP: {args.analyze_ip}\n")
        result = intel.analyze_ip(args.analyze_ip)
        print(json.dumps(result, indent=2))

    elif args.analyze_url:
        print(f"\n🔍 Analyzing URL: {args.analyze_url}\n")
        result = intel.analyze_url(args.analyze_url)
        print(json.dumps(result, indent=2))

    elif args.analyze_path:
        print(f"\n🔍 Analyzing path: {args.analyze_path}\n")
        result = intel.analyze_file_path(args.analyze_path)
        print(json.dumps(result, indent=2))

    elif args.add_ioc:
        ioc_type, value = args.add_ioc
        print(f"\n➕ Adding IOC: {ioc_type} = {value}\n")
        result = intel.add_ioc(ioc_type, value, args.tags, args.threat_level)
        print("✅ IOC added:")
        print(json.dumps(result, indent=2))

    elif args.add_threat:
        print(f"\n➕ Adding threat: {args.add_threat}\n")
        result = intel.add_threat(
            name=args.add_threat,
            category=args.category,
            description=args.description or "No description provided",
            severity=args.severity,
            actors=args.actors,
            malware=args.malware
        )
        print("✅ Threat added:")
        print(intel.generate_threat_report(result))

    elif args.search:
        print(f"\n🔍 Searching for: {args.search}\n")
        results = intel.search_threats(args.search)
        print(f"Found {len(results)} matching threats:\n")
        for threat in results:
            print(f"  [{threat['severity']}] {threat['name']}")
            print(f"  Category: {threat['category']}")
            print()

    elif args.list_threats:
        print(intel.get_threat_summary())
        print("\n📋 THREAT DETAILS:")
        if intel.threats:
            for threat in intel.threats[-10:]:
                print(f"\n{intel.generate_threat_report(threat)}")
        else:
            print("\nNo threats in database.")

    elif args.list_iocs:
        print(f"\n🔍 Found {len(intel.iocs)} IOCs:\n")
        for ioc in intel.iocs[-20:]:
            print(f"  • [{ioc['type']}] {ioc['value']}")
            print(f"    Level: {ioc['threat_level']}, Tags: {', '.join(ioc.get('tags', []))}")
            print(f"    First seen: {ioc['first_seen']}")
            print()

    elif args.correlate:
        try:
            with open(args.correlate, 'r') as f:
                iocs_to_correlate = json.load(f).get("iocs", [])
            
            print(f"\n🔗 Correlating {len(iocs_to_correlate)} IOCs...\n")
            result = intel.correlate_iocs(iocs_to_correlate)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Error: {e}")

    elif args.summary:
        print(intel.get_threat_summary())

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
