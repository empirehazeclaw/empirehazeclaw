#!/usr/bin/env python3
"""
Backup Manager Agent - Operations
Manages data backups with scheduling, verification and restore capabilities.
Based on SOUL.md principles: data safety, efficiency, reliability.
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import tarfile
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "backup_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BackupManager")

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR = Path("/home/clawbot/.openclaw/workspace/backups")
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_INDEX_FILE = DATA_DIR / "backup_index.json"


def load_backup_index() -> dict:
    """Load backup index."""
    try:
        if BACKUP_INDEX_FILE.exists():
            with open(BACKUP_INDEX_FILE, 'r') as f:
                return json.load(f)
        return {"backups": [], "schedules": []}
    except Exception as e:
        logger.error(f"Failed to load backup index: {e}")
        return {"backups": [], "schedules": []}


def save_backup_index(data: dict) -> bool:
    """Save backup index."""
    try:
        with open(BACKUP_INDEX_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save backup index: {e}")
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
        logger.error(f"Failed to calculate checksum: {e}")
        return ""


def create_backup(name: str, paths: List[str], backup_type: str = "full",
                  compression: str = "gzip", destination: Optional[str] = None,
                  exclude_patterns: Optional[List[str]] = None) -> dict:
    """Create a backup of specified paths."""
    data = load_backup_index()
    backup_id = len(data["backups"]) + 1
    timestamp = datetime.utcnow().isoformat()
    
    # Generate backup filename
    safe_name = name.replace(" ", "_").lower()
    filename = f"{safe_name}_{timestamp.replace(':', '-')}.tar.gz"
    dest_path = Path(destination) if destination else BACKUPS_DIR
    dest_path.mkdir(parents=True, exist_ok=True)
    backup_file = dest_path / filename
    
    # Create archive
    try:
        with tarfile.open(backup_file, "w:gz" if compression == "gzip" else ("w:bz2" if compression == "bzip2" else "w")) as tar:
            for path_str in paths:
                path = Path(path_str)
                if not path.exists():
                    raise ValueError(f"Path does not exist: {path_str}")
                
                # Handle exclude patterns
                if exclude_patterns:
                    import fnmatch
                    should_exclude = any(fnmatch.fnmatch(str(path), pattern) for pattern in exclude_patterns)
                    if should_exclude:
                        continue
                
                tar.add(path, arcname=path.name)
        
        # Calculate checksum
        checksum = calculate_checksum(backup_file)
        size = backup_file.stat().st_size
        
        backup = {
            "id": backup_id,
            "name": name,
            "paths": paths,
            "type": backup_type,
            "compression": compression,
            "filename": filename,
            "filepath": str(backup_file),
            "checksum": checksum,
            "size": size,
            "created_at": timestamp,
            "verified": False,
            "status": "completed"
        }
        
        data["backups"].append(backup)
        if save_backup_index(data):
            logger.info(f"Created backup #{backup_id}: {name}")
            return backup
        raise Exception("Failed to save backup index")
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        # Clean up partial backup
        if backup_file.exists():
            backup_file.unlink()
        raise


def verify_backup(backup_id: int) -> bool:
    """Verify backup integrity using checksum."""
    data = load_backup_index()
    
    for backup in data["backups"]:
        if backup["id"] == backup_id:
            filepath = Path(backup["filepath"])
            if not filepath.exists():
                backup["status"] = "missing"
                save_backup_index(data)
                return False
            
            current_checksum = calculate_checksum(filepath)
            if current_checksum == backup["checksum"]:
                backup["verified"] = True
                backup["status"] = "verified"
                backup["verified_at"] = datetime.utcnow().isoformat()
                save_backup_index(data)
                logger.info(f"Backup #{backup_id} verified successfully")
                return True
            else:
                backup["status"] = "corrupted"
                save_backup_index(data)
                logger.error(f"Backup #{backup_id} checksum mismatch")
                return False
    
    return False


def restore_backup(backup_id: int, destination: str) -> bool:
    """Restore a backup to specified destination."""
    data = load_backup_index()
    
    for backup in data["backups"]:
        if backup["id"] == backup_id:
            filepath = Path(backup["filepath"])
            if not filepath.exists():
                logger.error(f"Backup file not found: {filepath}")
                return False
            
            dest_path = Path(destination)
            dest_path.mkdir(parents=True, exist_ok=True)
            
            try:
                comp = backup.get('compression', 'gzip')
                read_mode = f"r:gz" if comp == "gzip" else (f"r:bz2" if comp == "bzip2" else "r:*")
                with tarfile.open(filepath, read_mode) as tar:
                    tar.extractall(dest_path)
                
                logger.info(f"Restored backup #{backup_id} to {destination}")
                backup["last_restored"] = datetime.utcnow().isoformat()
                save_backup_index(data)
                return True
            except Exception as e:
                logger.error(f"Restore failed: {e}")
                return False
    
    return False


def list_backups(backup_type: Optional[str] = None, verified_only: bool = False,
                 limit: int = 50) -> List[Dict]:
    """List backups with optional filters."""
    data = load_backup_index()
    backups = data.get("backups", [])
    
    if backup_type:
        backups = [b for b in backups if b.get("type") == backup_type]
    if verified_only:
        backups = [b for b in backups if b.get("verified")]
    
    backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return backups[:limit]


def delete_backup(backup_id: int, delete_files: bool = True) -> bool:
    """Delete a backup record and optionally the backup file."""
    data = load_backup_index()
    
    for i, backup in enumerate(data["backups"]):
        if backup["id"] == backup_id:
            # Delete file if exists
            if delete_files:
                filepath = Path(backup["filepath"])
                if filepath.exists():
                    filepath.unlink()
            
            del data["backups"][i]
            if save_backup_index(data):
                logger.info(f"Deleted backup #{backup_id}")
                return True
            return False
    
    return False


def cleanup_old_backups(keep_count: int = 10, older_than_days: Optional[int] = None) -> int:
    """Clean up old backups, keeping most recent."""
    data = load_backup_index()
    backups = data.get("backups", [])
    
    # Sort by date descending
    backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    to_delete = []
    deleted_count = 0
    
    # Keep specified count of most recent
    if len(backups) > keep_count:
        to_delete.extend(backups[keep_count:])
    
    # Also delete older than specified days
    if older_than_days:
        cutoff = datetime.utcnow() - timedelta(days=older_than_days)
        for backup in backups:
            created = datetime.fromisoformat(backup.get("created_at", "2000-01-01"))
            if created < cutoff:
                if backup not in to_delete:
                    to_delete.append(backup)
    
    # Delete duplicates
    to_delete_ids = [b["id"] for b in to_delete]
    data["backups"] = [b for b in backups if b["id"] not in to_delete_ids]
    
    if save_backup_index(data):
        for b in to_delete:
            filepath = Path(b["filepath"])
            if filepath.exists():
                filepath.unlink()
            deleted_count += 1
            logger.info(f"Cleaned up old backup: {b['name']}")
    
    return deleted_count


def get_stats() -> Dict:
    """Get backup statistics."""
    data = load_backup_index()
    backups = data.get("backups", [])
    
    stats = {
        "total_backups": len(backups),
        "total_size": sum(b.get("size", 0) for b in backups),
        "verified": len([b for b in backups if b.get("verified")]),
        "corrupted": len([b for b in backups if b.get("status") == "corrupted"]),
        "missing": len([b for b in backups if b.get("status") == "missing"]),
        "by_type": {},
        "oldest": None,
        "newest": None
    }
    
    for b in backups:
        btype = b.get("type", "unknown")
        stats["by_type"][btype] = stats["by_type"].get(btype, 0) + 1
    
    if backups:
        sorted_backups = sorted(backups, key=lambda x: x.get("created_at", ""))
        stats["oldest"] = sorted_backups[0].get("created_at")
        stats["newest"] = sorted_backups[-1].get("created_at")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Backup Manager Agent - Manage data backups",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --name "workspace-backup" --paths /home/clawbot/.openclaw/workspace --type full
  %(prog)s create --name "data-only" --paths /home/clawbot/.openclaw/workspace/data --type incremental
  %(prog)s verify --id 1
  %(prog)s restore --id 1 --destination /tmp/restore
  %(prog)s list --verified-only
  %(prog)s delete --id 1
  %(prog)s cleanup --keep 5 --older-than 30
  %(prog)s stats
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create
    create_parser = subparsers.add_parser("create", help="Create a backup")
    create_parser.add_argument("--name", "-n", required=True, help="Backup name")
    create_parser.add_argument("--paths", "-p", nargs="+", required=True, help="Paths to backup")
    create_parser.add_argument("--type", "-t", choices=["full", "incremental", "differential"],
                               default="full", help="Backup type")
    create_parser.add_argument("--compression", "-c", choices=["gzip", "bzip2", "none"],
                               default="gzip", help="Compression type")
    create_parser.add_argument("--destination", "-d", help="Custom destination directory")
    create_parser.add_argument("--exclude", nargs="*", help="Exclude patterns (glob)")

    # Verify
    verify_parser = subparsers.add_parser("verify", help="Verify backup integrity")
    verify_parser.add_argument("--id", "-i", type=int, required=True, help="Backup ID")

    # Restore
    restore_parser = subparsers.add_parser("restore", help="Restore a backup")
    restore_parser.add_argument("--id", "-i", type=int, required=True, help="Backup ID")
    restore_parser.add_argument("--destination", "-d", required=True, help="Restore destination")

    # List
    list_parser = subparsers.add_parser("list", help="List backups")
    list_parser.add_argument("--type", "-t", help="Filter by type")
    list_parser.add_argument("--verified-only", action="store_true", help="Show only verified")
    list_parser.add_argument("--limit", "-l", type=int, default=50, help="Limit results")

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete a backup")
    delete_parser.add_argument("--id", "-i", type=int, required=True, help="Backup ID")
    delete_parser.add_argument("--keep-files", action="store_true", help="Keep backup files")

    # Cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old backups")
    cleanup_parser.add_argument("--keep", type=int, default=10, help="Number of backups to keep")
    cleanup_parser.add_argument("--older-than", type=int, help="Delete older than N days")

    # Stats
    subparsers.add_parser("stats", help="Show backup statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "create":
            backup = create_backup(
                name=args.name,
                paths=args.paths,
                backup_type=args.type,
                compression=args.compression,
                destination=args.destination,
                exclude_patterns=args.exclude
            )
            size_mb = backup["size"] / (1024 * 1024)
            print(f"✅ Created backup #{backup['id']}: {backup['name']}")
            print(f"   File: {backup['filepath']}")
            print(f"   Size: {size_mb:.2f} MB")
            print(f"   Checksum: {backup['checksum'][:16]}...")

        elif args.command == "verify":
            if verify_backup(args.id):
                print(f"✅ Backup #{args.id} verified successfully")
            else:
                print(f"❌ Backup #{args.id} verification failed")
                return 1

        elif args.command == "restore":
            print(f"🔄 Restoring backup #{args.id} to {args.destination}...")
            if restore_backup(args.id, args.destination):
                print(f"✅ Backup restored successfully to {args.destination}")
            else:
                print(f"❌ Restore failed")
                return 1

        elif args.command == "list":
            backups = list_backups(
                backup_type=args.type if hasattr(args, 'type') and args.type else None,
                verified_only=args.verified_only if hasattr(args, 'verified_only') else False,
                limit=args.limit if hasattr(args, 'limit') else 50
            )
            if not backups:
                print("No backups found.")
            else:
                print(f"Found {len(backups)} backup(s):\n")
                for b in backups:
                    status = "✅" if b.get("verified") else ("❌" if b.get("status") == "corrupted" else "⏳")
                    size_mb = b.get("size", 0) / (1024 * 1024)
                    print(f"  {status} #{b['id']} | {b.get('type', '?'):12} | {size_mb:8.2f} MB | {b['name']}")
                    print(f"         {b.get('created_at', '?')}")

        elif args.command == "delete":
            if delete_backup(args.id, delete_files=not getattr(args, 'keep_files', False)):
                print(f"✅ Deleted backup #{args.id}")
            else:
                print(f"Backup #{args.id} not found.")
                return 1

        elif args.command == "cleanup":
            count = cleanup_old_backups(
                keep_count=args.keep,
                older_than_days=args.older_than if hasattr(args, 'older_than') else None
            )
            print(f"✅ Cleaned up {count} old backup(s)")

        elif args.command == "stats":
            stats = get_stats()
            print("\n💾 Backup Statistics")
            print(f"  Total Backups: {stats['total_backups']}")
            total_size_gb = stats['total_size'] / (1024 * 1024 * 1024)
            print(f"  Total Size: {total_size_gb:.2f} GB")
            print(f"  Verified: {stats['verified']}")
            print(f"  Corrupted: {stats['corrupted']}")
            print(f"  Missing: {stats['missing']}")
            print(f"  Oldest: {stats['oldest'] or 'None'}")
            print(f"  Newest: {stats['newest'] or 'None'}")
            print("  By Type:")
            for btype, count in stats["by_type"].items():
                print(f"    {btype}: {count}")

        return 0

    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
