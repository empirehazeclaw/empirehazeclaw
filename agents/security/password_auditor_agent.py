#!/usr/bin/env python3
"""
Password Auditor Agent
Audits password strength, checks against common password lists,
analyzes password hashes, and generates security reports
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sqlite3
import string
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "password_auditor.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("PasswordAuditor")

# Common weak passwords (top 100)
COMMON_PASSWORDS = {
    "123456", "password", "12345678", "qwerty", "123456789",
    "12345", "1234", "111111", "1234567", "dragon",
    "123123", "baseball", "iloveyou", "trustno1", "sunshine",
    "master", "welcome", "shadow", "ashley", "football",
    "jesus", "michael", "ninja", "mustang", "password1",
    "password123", "admin", "admin123", "root", "pass",
    "letmein", "hello", "monkey", "login", "starwars",
    "princess", "qwerty123", "solo", "password1!", "password12",
    "welcome1", "welcome123", "changeme", "secret", "passw0rd",
    "p@ssw0rd", "p@ssword", "pass123", "pass1234", "test",
    "test123", "guest", "guest123", "qwertyuiop", "abcd1234",
    "000000", "666666", "696969", "jordan", "jordan123",
    "hunter", "hunter2", "buster", "soccer", "harley",
    "batman", "andrew", "tigger", "summer", "michael2",
    "jordan23", "a1b2c3", "q1w2e3", "z1x2c3", "Password1",
    "Password123", "P@ssword1", "P@ssword123", "Admin123", "root123",
    "toor", "master123", "administrator", "admin1234", "server",
    "sql", "mysql", "postgres", "oracle", "backup",
    "support", "helpdesk", "ftp", "ssh", "telnet"
}

# Hash patterns for identification
HASH_PATTERNS = {
    "md5": (r"^[a-f0-9]{32}$", "MD5"),
    "sha1": (r"^[a-f0-9]{40}$", "SHA-1"),
    "sha256": (r"^[a-f0-9]{64}$", "SHA-256"),
    "sha512": (r"^[a-f0-9]{128}$", "SHA-512"),
    "bcrypt": (r"^\$2[aby]?\$\d{1,2}\$[./A-Za-z0-9]{53}$", "bcrypt"),
    "argon2": (r"^\$argon2", "Argon2"),
}


class PasswordAuditor:
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir or "/home/clawbot/.openclaw/workspace/data")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.audit_file = self.output_dir / f"password_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.hashes_file = self.output_dir / f"password_hashes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        self.results = {
            "audit_time": datetime.now().isoformat(),
            "passwords_checked": 0,
            "weak_passwords": [],
            "strong_passwords": [],
            "hashes_analyzed": [],
            "statistics": {},
            "recommendations": []
        }
        
        # DB for storing audit results
        self.db_path = self.output_dir / "password_audit.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for audit results"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS audit_results
                     (id INTEGER PRIMARY KEY, password TEXT, hash TEXT, 
                      strength TEXT, score INTEGER, checked_at TEXT)''')
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
    
    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits"""
        if not password:
            return 0.0
        
        charset_size = 0
        if any(c.islower() for c in password):
            charset_size += 26
        if any(c.isupper() for c in password):
            charset_size += 26
        if any(c.isdigit() for c in password):
            charset_size += 10
        if any(c in string.punctuation for c in password):
            charset_size += 32
        
        if charset_size == 0:
            return 0.0
        
        entropy = len(password) * (charset_size.bit_length() - 1)
        return entropy
    
    def _check_password_strength(self, password: str) -> Tuple[str, int, Dict]:
        """Check password strength and return rating"""
        score = 0
        details = {
            "length": len(password),
            "has_lower": False,
            "has_upper": False,
            "has_digit": False,
            "has_special": False,
            "has_common_pattern": False
        }
        
        # Length checks
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        if len(password) >= 20:
            score += 1
        
        # Character type checks
        if any(c.islower() for c in password):
            score += 1
            details["has_lower"] = True
        if any(c.isupper() for c in password):
            score += 1
            details["has_upper"] = True
        if any(c.isdigit() for c in password):
            score += 1
            details["has_digit"] = True
        if any(c in string.punctuation for c in password):
            score += 2
            details["has_special"] = True
        
        # Pattern checks
        if password.lower() in COMMON_PASSWORDS:
            score -= 10
            details["has_common_pattern"] = True
        
        # Sequential characters
        if re.search(r'(.)\1{2,}', password):  # Repeated chars
            score -= 1
        
        if re.search(r'(012|123|234|345|456|567|678|789)', password):
            score -= 1
        
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            score -= 1
        
        # Keyboard patterns
        if re.search(r'(qwerty|asdf|zxcv|qazwsx)', password.lower()):
            score -= 2
            details["has_common_pattern"] = True
        
        # Normalize score
        score = max(0, min(10, score))
        
        if score >= 8:
            strength = "strong"
        elif score >= 5:
            strength = "medium"
        else:
            strength = "weak"
        
        return strength, score, details
    
    def _identify_hash(self, hash_value: str) -> Optional[str]:
        """Identify hash type from pattern"""
        for hash_type, (pattern, name) in HASH_PATTERNS.items():
            if re.match(pattern, hash_value.strip()):
                return name
        return None
    
    def _crack_hash(self, hash_value: str, wordlist: Optional[List[str]] = None) -> Optional[str]:
        """Try to crack a hash using common passwords"""
        words = wordlist or list(COMMON_PASSWORDS)
        
        hash_lower = hash_value.lower()
        
        for word in words:
            # Try plain
            if hashlib.md5(word.encode()).hexdigest() == hash_lower:
                return word
            if hashlib.sha1(word.encode()).hexdigest() == hash_lower:
                return word
            if hashlib.sha256(word.encode()).hexdigest() == hash_lower:
                return word
        
        return None
    
    def audit_password(self, password: str) -> Dict:
        """Audit a single password"""
        strength, score, details = self._check_password_strength(password)
        entropy = self._calculate_entropy(password)
        
        result = {
            "password": password[:3] + "***" if len(password) > 3 else "***",
            "length": len(password),
            "strength": strength,
            "score": score,
            "entropy": round(entropy, 2),
            "details": details,
            "is_common": password.lower() in COMMON_PASSWORDS,
            "audited_at": datetime.now().isoformat()
        }
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO audit_results VALUES (NULL, ?, '', ?, ?, ?)",
                 (password, strength, score, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        logger.info(f"Audited password: {result['password']} - {strength} (score: {score})")
        
        return result
    
    def audit_passwords_from_file(self, filename: str) -> List[Dict]:
        """Audit passwords from a file"""
        path = Path(filename)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        
        passwords = []
        
        if path.suffix == '.json':
            with open(path) as f:
                data = json.load(f)
                if isinstance(data, list):
                    passwords = data
                elif isinstance(data, dict):
                    passwords = data.get("passwords", [])
        else:
            with open(path) as f:
                passwords = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        results = []
        for pwd in passwords:
            result = self.audit_password(pwd)
            results.append(result)
            
            if result["is_common"] or result["score"] < 5:
                self.results["weak_passwords"].append(result)
            else:
                self.results["strong_passwords"].append(result)
        
        self.results["passwords_checked"] = len(passwords)
        return results
    
    def audit_hash_file(self, filename: str) -> List[Dict]:
        """Analyze password hashes from a file"""
        path = Path(filename)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        
        hashes = []
        
        if path.suffix == '.json':
            with open(path) as f:
                data = json.load(f)
                if isinstance(data, list):
                    hashes = [h if isinstance(h, str) else h.get("hash", "") for h in data]
                elif isinstance(data, dict):
                    hashes = data.get("hashes", [])
        else:
            with open(path) as f:
                hashes = [line.strip().split(':')[-1] if ':' in line else line.strip() 
                          for line in f if line.strip() and not line.startswith('#')]
        
        results = []
        cracked_count = 0
        
        for hash_val in hashes:
            hash_val = hash_val.strip()
            if not hash_val:
                continue
            
            hash_type = self._identify_hash(hash_val)
            cracked = self._crack_hash(hash_val)
            
            result = {
                "hash": hash_val[:8] + "..." if len(hash_val) > 8 else hash_val,
                "hash_type": hash_type or "Unknown",
                "cracked": cracked is not None,
                "plaintext": cracked[:3] + "***" if cracked else None,
                "analyzed_at": datetime.now().isoformat()
            }
            results.append(result)
            
            if cracked:
                cracked_count += 1
                logger.warning(f"CRACKED: {hash_type} hash -> {cracked}")
        
        self.results["hashes_analyzed"] = results
        
        return results
    
    def _generate_statistics(self) -> Dict:
        """Generate audit statistics"""
        total = self.results["passwords_checked"]
        
        if total == 0:
            return {}
        
        weak_count = len(self.results["weak_passwords"])
        strong_count = len(self.results["strong_passwords"])
        
        scores = [p["score"] for p in self.results["weak_passwords"] + self.results["strong_passwords"]]
        
        stats = {
            "total_passwords": total,
            "weak_passwords": weak_count,
            "strong_passwords": strong_count,
            "weak_percentage": round(weak_count / total * 100, 1) if total > 0 else 0,
            "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0
        }
        
        self.results["statistics"] = stats
        return stats
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        stats = self.results.get("statistics", {})
        
        weak_pct = stats.get("weak_percentage", 0)
        
        if weak_pct > 50:
            recommendations.append("CRITICAL: Over 50% of passwords are weak. Implement mandatory password complexity requirements.")
        elif weak_pct > 20:
            recommendations.append("WARNING: Significant portion of weak passwords detected. Consider password policy enforcement.")
        
        recommendations.append("Enforce minimum 12-character passwords with mixed character types")
        recommendations.append("Implement multi-factor authentication (MFA) where possible")
        recommendations.append("Use a password manager to generate and store unique passwords")
        recommendations.append("Regularly audit and rotate service accounts")
        recommendations.append("Consider implementing password blacklisting for common variants")
        recommendations.append("Educate users on password security and phishing awareness")
        
        self.results["recommendations"] = recommendations
        return recommendations
    
    def save_results(self):
        """Save audit results to JSON file"""
        with open(self.audit_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Audit results saved to {self.audit_file}")
        
        # Save separate cracked hashes report
        if self.results["hashes_analyzed"]:
            cracked_hashes = [h for h in self.results["hashes_analyzed"] if h["cracked"]]
            if cracked_hashes:
                cracked_file = self.output_dir / "cracked_hashes.json"
                with open(cracked_file, 'w') as f:
                    json.dump(cracked_hashes, f, indent=2)
                logger.info(f"Cracked hashes saved to {cracked_file}")
    
    def print_report(self):
        """Print audit report to console"""
        stats = self.results.get("statistics", {})
        
        print(f"\n{'='*60}")
        print(f"PASSWORD AUDIT REPORT")
        print(f"{'='*60}")
        print(f"Audit Time: {self.results['audit_time']}")
        print(f"\nPassword Statistics:")
        print(f"  Total Checked: {stats.get('total_passwords', 0)}")
        print(f"  Weak: {stats.get('weak_passwords', 0)} ({stats.get('weak_percentage', 0)}%)")
        print(f"  Strong: {stats.get('strong_passwords', 0)}")
        print(f"  Average Score: {stats.get('average_score', 0)}/10")
        
        if self.results.get("weak_passwords"):
            print(f"\nWeak Passwords Found ({len(self.results['weak_passwords'])}):")
            for pwd in self.results["weak_passwords"][:5]:
                print(f"  - {pwd['password']} (score: {pwd['score']}/10)")
            if len(self.results["weak_passwords"]) > 5:
                print(f"  ... and {len(self.results['weak_passwords']) - 5} more")
        
        if self.results.get("hashes_analyzed"):
            cracked = [h for h in self.results["hashes_analyzed"] if h["cracked"]]
            print(f"\nHash Analysis:")
            print(f"  Total Hashes: {len(self.results['hashes_analyzed'])}")
            print(f"  Cracked: {len(cracked)}")
            if cracked:
                print(f"  Cracked Hashes:")
                for h in cracked[:5]:
                    print(f"    - {h['hash_type']}: {h['plaintext']}")
        
        print(f"\nRecommendations:")
        for rec in self.results.get("recommendations", [])[:5]:
            print(f"  - {rec}")
        
        print(f"\nFiles Generated:")
        print(f"  - {self.audit_file}")
        print(f"  - {self.db_path}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Password Auditor - Check password strength and security",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --check "MyStr0ng!Pass"     Check single password
  %(prog)s --file passwords.txt        Audit password file
  %(prog)s --hash-file hashes.txt       Analyze password hashes
  %(prog)s --batch                      Run batch with demo data
        """
    )
    parser.add_argument("--check", "-c", help="Check a single password")
    parser.add_argument("--file", "-f", help="File containing passwords (JSON or .txt)")
    parser.add_argument("--hash-file", "--hash", help="File containing password hashes")
    parser.add_argument("--output", "-o", help="Output directory (default: data/)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    auditor = PasswordAuditor(args.output)
    
    try:
        if args.check:
            result = auditor.audit_password(args.check)
            print(f"\nPassword: {result['password']}")
            print(f"Strength: {result['strength'].upper()}")
            print(f"Score: {result['score']}/10")
            print(f"Entropy: {result['entropy']} bits")
            print(f"Common: {'Yes' if result['is_common'] else 'No'}")
            
        elif args.file:
            auditor.audit_passwords_from_file(args.file)
            auditor._generate_statistics()
            auditor._generate_recommendations()
            auditor.save_results()
            auditor.print_report()
            
        elif args.hash_file:
            auditor.audit_hash_file(args.hash_file)
            auditor.save_results()
            auditor.print_report()
            
        else:
            # Demo mode
            print("Running demo audit...")
            demo_passwords = [
                "123456", "Password123!", "admin", "MyV3ryStr0ng!P@ssw0rd",
                "qwerty", "Summer2024!", "letmein", "X#9kL$mN@2pQ!"
            ]
            
            for pwd in demo_passwords:
                result = auditor.audit_password(pwd)
                if result["is_common"] or result["score"] < 5:
                    auditor.results["weak_passwords"].append(result)
                else:
                    auditor.results["strong_passwords"].append(result)
            
            auditor.results["passwords_checked"] = len(demo_passwords)
            auditor._generate_statistics()
            auditor._generate_recommendations()
            auditor.save_results()
            auditor.print_report()
            
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
