#!/usr/bin/env python3
"""
Config Manager Agent - Operations
Manages configuration files with versioning, validation and diff viewing.
Based on SOUL.md principles: clarity, reliability, controlled changes.
"""

import argparse
import hashlib
import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "config_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ConfigManager")

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_INDEX_FILE = DATA_DIR / "config_index.json"
CONFIG_BACKUPS_DIR = Path("/home/clawbot/.openclaw/workspace/config_backups")
CONFIG_BACKUPS_DIR.mkdir(parents=True, exist_ok=True)


def load_config_index() -> dict:
    """Load configuration index."""
    try:
        if CONFIG_INDEX_FILE.exists():
            with open(CONFIG_INDEX_FILE, 'r') as f:
                return json.load(f)
        return {"configs": [], "groups": {}}
    except Exception as e:
        logger.error(f"Failed to load config index: {e}")
        return {"configs": [], "groups": {}}


def save_config_index(data: dict) -> bool:
    """Save configuration index."""
    try:
        with open(CONFIG_INDEX_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save config index: {e}")
        return False


def calculate_checksum(filepath: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        return ""


def register_config(filepath: str, name: str, group: str = "default",
                   description: str = "") -> dict:
    """Register a configuration file for tracking."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {filepath}")
    
    data = load_config_index()
    
    # Check if already registered
    for cfg in data["configs"]:
        if cfg["filepath"] == str(path):
            raise ValueError(f"Config already registered: {filepath}")
    
    config_id = len(data["configs"]) + 1
    checksum = calculate_checksum(path)
    
    config = {
        "id": config_id,
        "name": name,
        "filepath": str(path),
        "group": group,
        "description": description,
        "checksum": checksum,
        "registered_at": datetime.utcnow().isoformat(),
        "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
        "versions": []
    }
    
    # Create initial version backup
    version_id = 1
    version_file = CONFIG_BACKUPS_DIR / f"config_{config_id}_v{version_id}.json"
    with open(version_file, 'w') as f:
        json.dump({
            "version": version_id,
            "content": path.read_text(),
            "checksum": checksum,
            "timestamp": datetime.utcnow().isoformat()
        }, f, indent=2)
    
    config["versions"].append({
        "version": version_id,
        "checksum": checksum,
        "backup_file": str(version_file),
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Add group if new
    if group not in data["groups"]:
        data["groups"][group] = []
    data["groups"][group].append(config_id)
    data["configs"].append(config)
    
    if save_config_index(data):
        logger.info(f"Registered config #{config_id}: {name}")
        return config
    raise Exception("Failed to save config index")


def get_config(config_id: int) -> Optional[Dict]:
    """Get configuration details."""
    data = load_config_index()
    for cfg in data.get("configs", []):
        if cfg["id"] == config_id:
            return cfg
    return None


def list_configs(group: Optional[str] = None) -> List[Dict]:
    """List registered configurations."""
    data = load_config_index()
    
    if group:
        config_ids = data.get("groups", {}).get(group, [])
        configs = [cfg for cfg in data.get("configs", []) if cfg["id"] in config_ids]
    else:
        configs = data.get("configs", [])
    
    configs.sort(key=lambda x: x.get("registered_at", ""), reverse=True)
    return configs


def update_config(config_id: int, new_filepath: Optional[str] = None) -> Optional[Dict]:
    """Update a configuration file (track changes)."""
    data = load_config_index()
    
    for i, cfg in enumerate(data["configs"]):
        if cfg["id"] == config_id:
            path = Path(new_filepath) if new_filepath else Path(cfg["filepath"])
            
            if not path.exists():
                raise FileNotFoundError(f"Config file not found: {path}")
            
            old_checksum = cfg["checksum"]
            new_checksum = calculate_checksum(path)
            
            if old_checksum == new_checksum:
                logger.info(f"Config #{config_id} unchanged")
                return cfg
            
            # Create new version backup
            version_id = len(cfg["versions"]) + 1
            version_file = CONFIG_BACKUPS_DIR / f"config_{config_id}_v{version_id}.json"
            with open(version_file, 'w') as f:
                json.dump({
                    "version": version_id,
                    "content": path.read_text(),
                    "checksum": new_checksum,
                    "timestamp": datetime.utcnow().isoformat()
                }, f, indent=2)
            
            # Update config record
            cfg["checksum"] = new_checksum
            cfg["last_modified"] = datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            if new_filepath:
                cfg["filepath"] = str(path)
            
            cfg["versions"].append({
                "version": version_id,
                "checksum": new_checksum,
                "backup_file": str(version_file),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            if save_config_index(data):
                logger.info(f"Updated config #{config_id} to version {version_id}")
                return cfg
            return None
    
    return None


def view_version(config_id: int, version: int) -> Optional[str]:
    """View a specific version of a configuration."""
    data = load_config_index()
    
    for cfg in data.get("configs", []):
        if cfg["id"] == config_id:
            for v in cfg.get("versions", []):
                if v["version"] == version:
                    version_file = Path(v["backup_file"])
                    if version_file.exists():
                        with open(version_file, 'r') as f:
                            content = json.load(f)["content"]
                        return content
            return None
    
    return None


def rollback_config(config_id: int, version: int) -> bool:
    """Rollback configuration to a specific version."""
    content = view_version(config_id, version)
    if content is None:
        return False
    
    config = get_config(config_id)
    if not config:
        return False
    
    path = Path(config["filepath"])
    try:
        path.write_text(content)
        update_config(config_id)
        logger.info(f"Rolled back config #{config_id} to version {version}")
        return True
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        return False


def validate_config(config_id: int) -> Dict:
    """Validate configuration file."""
    config = get_config(config_id)
    if not config:
        return {"valid": False, "error": "Config not found"}
    
    path = Path(config["filepath"])
    if not path.exists():
        return {"valid": False, "error": "File missing", "file_exists": False}
    
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "file_exists": True,
        "checksum_valid": True
    }
    
    # Verify checksum
    current_checksum = calculate_checksum(path)
    if current_checksum != config["checksum"]:
        result["valid"] = False
        result["checksum_valid"] = False
        result["errors"].append("Checksum mismatch - file has been modified")
    
    # Try to parse as JSON if applicable
    if path.suffix in [".json"]:
        try:
            with open(path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            result["valid"] = False
            result["errors"].append(f"Invalid JSON: {e}")
    
    return result


def diff_configs(config_id: int, version1: int, version2: int) -> Optional[str]:
    """Show diff between two versions of a configuration."""
    content1 = view_version(config_id, version1)
    content2 = view_version(config_id, version2)
    
    if content1 is None or content2 is None:
        return None
    
    lines1 = content1.splitlines()
    lines2 = content2.splitlines()
    
    diff_lines = [f"Diff: Config #{config_id} v{version1} vs v{version2}"]
    diff_lines.append("=" * 40)
    
    max_lines = max(len(lines1), len(lines2))
    for i in range(max_lines):
        l1 = lines1[i] if i < len(lines1) else ""
        l2 = lines2[i] if i < len(lines2) else ""
        
        if l1 != l2:
            if i < len(lines1):
                diff_lines.append(f"- {l1}")
            if i < len(lines2):
                diff_lines.append(f"+ {l2}")
        else:
            diff_lines.append(f"  {l1}")
    
    return "\n".join(diff_lines)


def unregister_config(config_id: int, keep_backups: bool = True) -> bool:
    """Unregister a configuration."""
    data = load_config_index()
    
    for i, cfg in enumerate(data["configs"]):
        if cfg["id"] == config_id:
            group = cfg.get("group")
            if group and group in data["groups"]:
                data["groups"][group] = [gid for gid in data["groups"][group] if gid != config_id]
            
            if not keep_backups:
                for v in cfg.get("versions", []):
                    backup_file = Path(v["backup_file"])
                    if backup_file.exists():
                        backup_file.unlink()
            
            del data["configs"][i]
            if save_config_index(data):
                logger.info(f"Unregistered config #{config_id}")
                return True
            return False
    
    return False


def get_stats() -> Dict:
    """Get configuration statistics."""
    data = load_config_index()
    configs = data.get("configs", [])
    
    stats = {
        "total_configs": len(configs),
        "by_group": {},
        "total_versions": sum(len(c.get("versions", [])) for c in configs),
        "total_backups": sum(len(c.get("versions", [])) for c in configs),
    }
    
    for cfg in configs:
        group = cfg.get("group", "default")
        stats["by_group"][group] = stats["by_group"].get(group, 0) + 1
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Config Manager Agent - Manage configuration files with versioning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s register --file /home/clawbot/.openclaw/workspace/config.json --name "main-config" --group "app"
  %(prog)s list --group app
  %(prog)s get --id 1
  %(prog)s update --id 1
  %(prog)s validate --id 1
  %(prog)s view --id 1 --version 2
  %(prog)s rollback --id 1 --version 1
  %(prog)s diff --id 1 --v1 1 --v2 3
  %(prog)s unregister --id 1
  %(prog)s stats
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register
    reg_parser = subparsers.add_parser("register", help="Register a config file")
    reg_parser.add_argument("--file", "-f", required=True, help="Path to config file")
    reg_parser.add_argument("--name", "-n", required=True, help="Config name")
    reg_parser.add_argument("--group", "-g", default="default", help="Config group")
    reg_parser.add_argument("--description", "-d", default="", help="Description")

    # List
    list_parser = subparsers.add_parser("list", help="List registered configs")
    list_parser.add_argument("--group", "-g", help="Filter by group")

    # Get
    get_parser = subparsers.add_parser("get", help="Get config details")
    get_parser.add_argument("--id", "-i", type=int, required=True, help="Config ID")

    # Update
    update_parser = subparsers.add_parser("update", help="Update config (detect changes)")
    update_parser.add_argument("--id", "-i", type=int, required=True, help="Config ID")
    update_parser.add_argument("--file", "-f", help="New file path")

    # Validate
    validate_parser = subparsers.add_parser("validate", help="Validate a config")
    validate_parser.add_argument("--id", "-i", type=int, required=True, help="Config ID")

    # View
    view_parser = subparsers.add_parser("view", help="View a specific version")
    view_parser.add_argument("--id", "-i", type=int, required=True, help="Config ID")
    view_parser.add_argument("--version", "-v", type=int, required=True, help="Version number")

    # Rollback
    rollback_parser = subparsers.add_parser("rollback", help="Rollback to version")
    rollback_parser.add_argument("--id", "-i", type=int, required=True, help="Config ID")
    rollback_parser.add_argument("--version", "-v", type=int, required=True, help="Version number")

    # Diff
    diff_parser = subparsers.add_parser("diff", help="Compare two versions")
    diff_parser.add_argument("--id", "-i", type=int, required=True, help="Config ID")
    diff_parser.add_argument("--v1", type=int, required=True, help="Version 1")
    diff_parser.add_argument("--v2", type=int, required=True, help="Version 2")

    # Unregister
    unreg_parser = subparsers.add_parser("unregister", help="Unregister a config")
    unreg_parser.add_argument("--id", "-i", type=int, required=True, help="Config ID")
    unreg_parser.add_argument("--keep-backups", action="store_true", help="Keep backup files")

    # Stats
    subparsers.add_parser("stats", help="Show statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "register":
            config = register_config(
                filepath=args.file,
                name=args.name,
                group=args.group,
                description=args.description
            )
            print(f"✅ Registered config #{config['id']}: {config['name']}")
            print(f"   File: {config['filepath']}")
            print(f"   Group: {config['group']}")
            print(f"   Versions: {len(config['versions'])}")

        elif args.command == "list":
            configs = list_configs(group=getattr(args, 'group', None))
            if not configs:
                print("No configs registered.")
            else:
                print(f"Found {len(configs)} config(s):\n")
                for cfg in configs:
                    print(f"  #{cfg['id']} | {cfg.get('group', 'default'):12} | {cfg['name']}")
                    print(f"         {cfg['filepath']}")
                    print(f"         Versions: {len(cfg.get('versions', []))} | Checksum: {cfg['checksum'][:12]}...")

        elif args.command == "get":
            cfg = get_config(args.id)
            if cfg:
                print(f"\nConfig #{cfg['id']}")
                print(f"  Name: {cfg['name']}")
                print(f"  Group: {cfg['group']}")
                print(f"  File: {cfg['filepath']}")
                print(f"  Description: {cfg['description']}")
                print(f"  Registered: {cfg['registered_at']}")
                print(f"  Last Modified: {cfg['last_modified']}")
                print(f"  Current Checksum: {cfg['checksum']}")
                print(f"  Versions: {len(cfg.get('versions', []))}")
            else:
                print(f"Config #{args.id} not found.")
                return 1

        elif args.command == "update":
            cfg = update_config(args.id, new_filepath=getattr(args, 'file', None))
            if cfg:
                print(f"✅ Updated config #{cfg['id']}")
                print(f"   New checksum: {cfg['checksum']}")
                print(f"   Total versions: {len(cfg.get('versions', []))}")
            else:
                print(f"Config #{args.id} not found.")
                return 1

        elif args.command == "validate":
            result = validate_config(args.id)
            if result["valid"]:
                print("✅ Config is valid")
            else:
                print("❌ Config validation failed:")
                for err in result.get("errors", []):
                    print(f"   - {err}")
            if result.get("warnings"):
                print("\nWarnings:")
                for w in result.get("warnings", []):
                    print(f"   - {w}")
            return 0 if result["valid"] else 1

        elif args.command == "view":
            content = view_version(args.id, args.version)
            if content is not None:
                print(f"\nConfig #{args.id} - Version {args.version}")
                print("=" * 40)
                print(content)
            else:
                print(f"Version {args.version} not found for config #{args.id}.")
                return 1

        elif args.command == "rollback":
            if rollback_config(args.id, args.version):
                print(f"✅ Rolled back config #{args.id} to version {args.version}")
            else:
                print(f"❌ Rollback failed. Check version number.")
                return 1

        elif args.command == "diff":
            diff = diff_configs(args.id, args.v1, args.v2)
            if diff:
                print(diff)
            else:
                print("Could not generate diff. Check version numbers.")
                return 1

        elif args.command == "unregister":
            if unregister_config(args.id, keep_backups=getattr(args, 'keep_backups', False)):
                print(f"✅ Unregistered config #{args.id}")
            else:
                print(f"Config #{args.id} not found.")
                return 1

        elif args.command == "stats":
            stats = get_stats()
            print("\n⚙️  Configuration Statistics")
            print(f"  Total Configs: {stats['total_configs']}")
            print(f"  Total Versions: {stats['total_versions']}")
            print(f"  Total Backups: {stats['total_backups']}")
            print("  By Group:")
            for grp, count in stats["by_group"].items():
                print(f"    {grp}: {count}")

        return 0

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return 1
    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
