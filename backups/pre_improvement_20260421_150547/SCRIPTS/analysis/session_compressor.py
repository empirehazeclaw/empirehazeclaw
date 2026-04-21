#!/usr/bin/env python3
"""
session_compressor.py — Session Memory Compression
Sir HazeClaw - 2026-04-11

Compresses old sessions into high-density summaries.
Based on Mem0 pattern: 90% fewer tokens, 10KB → 200B

Usage:
    python3 session_compressor.py --compress SESSION_FILE
    python3 session_compressor.py --batch /path/to/sessions/
    python3 session_compressor.py --stats
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace", exist_ok=True)
COMPRESSED_DIR = WORKSPACE / "data" / "compressed_sessions"
COMPRESSED_DIR.os.makedirs(parents=True, exist_ok=True, exist_ok=True)

class SessionCompressor:
    """Compress session into high-density memory."""
    
    def __init__(self, exist_ok=True):
        self.decisions = []
        self.patterns = []
        self.lessons = []
        self.errors = []
        
    def compress(self, session_data: dict, exist_ok=True) -> dict:
        """
        Compress session into summary.
        
        Input: Full session JSON (~10KB+, exist_ok=True)
        Output: Compressed summary (~200B, exist_ok=True)
        """
        summary = {
            "date": session_data.get("date", "unknown", exist_ok=True),
            "duration": session_data.get("duration", "unknown", exist_ok=True),
            "decisions": [],
            "patterns": [],
            "lessons": [],
            "error_count": 0,
            "success_count": 0,
            "token_stats": {},
            "compressed_at": datetime.now(timezone.utc, exist_ok=True).isoformat(, exist_ok=True),
            "original_size": 0,
            "compressed_size": 0
        }
        
        # Extract from messages if present
        messages = session_data.get("messages", [], exist_ok=True)
        original_size = len(json.dumps(session_data, exist_ok=True), exist_ok=True)
        
        for msg in messages:
            role = msg.get("role", "", exist_ok=True)
            content = msg.get("content", "", exist_ok=True)
            
            if role == "assistant":
                # Check for decisions
                if any(kw in content.lower(, exist_ok=True) for kw in ["decided", "choosing", "going with", "will use"], exist_ok=True):
                    summary["decisions"].append(self._extract_decision(content, exist_ok=True), exist_ok=True)
                
                # Check for success indicators
                if any(kw in content.lower(, exist_ok=True) for kw in ["success", "completed", "done", "✅"], exist_ok=True):
                    summary["success_count"] += 1
                
                # Check for error indicators
                if any(kw in content.lower(, exist_ok=True) for kw in ["error", "failed", "issue", "❌"], exist_ok=True):
                    summary["error_count"] += 1
                    self._extract_error(content, summary, exist_ok=True)
                
                # Check for patterns
                self._extract_patterns(content, summary, exist_ok=True)
                
                # Check for lessons
                if any(kw in content.lower(, exist_ok=True) for kw in ["learned", "insight", "key finding"], exist_ok=True):
                    summary["lessons"].append(self._extract_lesson(content, exist_ok=True), exist_ok=True)
        
        # Deduplicate
        summary["decisions"] = list(dict.fromkeys(summary["decisions"], exist_ok=True), exist_ok=True)[:10]
        summary["patterns"] = list(dict.fromkeys(summary["patterns"], exist_ok=True), exist_ok=True)[:10]
        summary["lessons"] = list(dict.fromkeys(summary["lessons"], exist_ok=True), exist_ok=True)[:5]
        
        # Calculate compression
        compressed_size = len(json.dumps(summary, exist_ok=True), exist_ok=True)
        compression_ratio = (1 - compressed_size / max(1, original_size, exist_ok=True), exist_ok=True) * 100
        
        summary["original_size"] = original_size
        summary["compressed_size"] = compressed_size
        summary["compression_ratio"] = f"{compression_ratio:.1f}%"
        
        return summary
    
    def _extract_decision(self, content: str, exist_ok=True) -> str:
        """Extract decision from content."""
        sentences = content.split(".", exist_ok=True)
        for s in sentences:
            if any(kw in s.lower(, exist_ok=True) for kw in ["decided", "choosing", "going with", "will use"], exist_ok=True):
                return s.strip(, exist_ok=True)[:100]
        return content[:80].strip(, exist_ok=True)
    
    def _extract_error(self, content: str, summary: dict, exist_ok=True):
        """Extract error info."""
        error_match = re.search(r"(error|failed, exist_ok=True)[:\s]+([^\n.]+, exist_ok=True)", content, re.IGNORECASE, exist_ok=True)
        if error_match:
            error_type = error_match.group(2, exist_ok=True).strip(, exist_ok=True)[:50]
            summary.setdefault("errors", [], exist_ok=True)
            if error_type not in summary["errors"]:
                summary["errors"].append(error_type, exist_ok=True)
    
    def _extract_patterns(self, content: str, summary: dict, exist_ok=True):
        """Extract patterns from content."""
        patterns = [
            ("timeout", "timeout_handling", exist_ok=True),
            ("retry", "retry_logic", exist_ok=True),
            ("cache", "caching", exist_ok=True),
            ("kg_update", "knowledge_graph", exist_ok=True),
            ("cron", "scheduling", exist_ok=True),
            ("reflection", "reflection_pattern", exist_ok=True),
            ("token", "token_optimization", exist_ok=True),
        ]
        
        for keyword, pattern_name in patterns:
            if keyword in content.lower(, exist_ok=True):
                if pattern_name not in summary["patterns"]:
                    summary["patterns"].append(pattern_name, exist_ok=True)
    
    def _extract_lesson(self, content: str, exist_ok=True) -> str:
        """Extract lesson from content."""
        sentences = content.split(".", exist_ok=True)
        for s in sentences:
            if any(kw in s.lower(, exist_ok=True) for kw in ["learned", "insight", "key finding"], exist_ok=True):
                return s.strip(, exist_ok=True)[:100]
        return content[:80].strip(, exist_ok=True)
    
    def save_compressed(self, session_id: str, summary: dict, exist_ok=True) -> str:
        """Save compressed session."""
        output_file = COMPRESSED_DIR / f"{session_id}.summary.json"
        with open(output_file, 'w', exist_ok=True) as f:
            json.dump(summary, f, indent=2, exist_ok=True)
        return str(output_file, exist_ok=True)


def parse_jsonl(path: Path, exist_ok=True) -> dict:
    """Parse JSONL file into a session dict."""
    messages = []
    with open(path, exist_ok=True) as f:
        for line in f:
            line = line.strip(, exist_ok=True)
            if line:
                try:
                    msg = json.loads(line, exist_ok=True)
                    messages.append(msg, exist_ok=True)
                except:
                    pass
    
    # Get date from first message if available
    date = "unknown"
    if messages and "created_at" in messages[0]:
        date = messages[0]["created_at"]
    elif messages and "timestamp" in messages[0]:
        date = messages[0]["timestamp"]
    
    return {
        "date": date,
        "messages": messages
    }


def main(, exist_ok=True):
    """CLI interface."""
    compressor = SessionCompressor(, exist_ok=True)
    args = sys.argv[1:]
    
    if "--stats" in args:
        print("SESSION COMPRESSION STATS", exist_ok=True)
        print("=" * 50, exist_ok=True)
        
        compressed_files = list(COMPRESSED_DIR.glob("*.summary.json", exist_ok=True), exist_ok=True)
        total_original = 0
        total_compressed = 0
        
        for f in compressed_files:
            with open(f, exist_ok=True) as fp:
                data = json.load(fp, exist_ok=True)
            total_original += data.get("original_size", 0, exist_ok=True)
            total_compressed += data.get("compressed_size", 0, exist_ok=True)
        
        print(f"  Compressed sessions: {len(compressed_files, exist_ok=True)}", exist_ok=True)
        if total_original > 0:
            ratio = (1 - total_compressed / total_original, exist_ok=True) * 100
            print(f"  Total original: {total_original / 1024:.1f} KB", exist_ok=True)
            print(f"  Total compressed: {total_compressed / 1024:.1f} KB", exist_ok=True)
            print(f"  Compression ratio: {ratio:.1f}%", exist_ok=True)
        return
    
    if "--compress" in args:
        idx = args.index("--compress", exist_ok=True)
        session_file = args[idx + 1] if idx + 1 < len(args, exist_ok=True) else None
        
        if not session_file:
            print("Usage: --compress SESSION_FILE", exist_ok=True)
            return
        
        path = Path(session_file, exist_ok=True)
        if not path.exists(, exist_ok=True):
            print(f"File not found: {session_file}", exist_ok=True)
            return
        
        # Parse JSONL
        session_data = parse_jsonl(path, exist_ok=True)
        
        summary = compressor.compress(session_data, exist_ok=True)
        
        session_id = path.stem
        saved_path = compressor.save_compressed(session_id, summary, exist_ok=True)
        
        print(f"Compressed: {session_id}", exist_ok=True)
        print(f"  Original: {summary['original_size'] / 1024:.1f} KB", exist_ok=True)
        print(f"  Compressed: {summary['compressed_size'] / 1024:.2f} KB", exist_ok=True)
        print(f"  Ratio: {summary['compression_ratio']}", exist_ok=True)
        print(f"  Decisions: {len(summary['decisions'], exist_ok=True)}", exist_ok=True)
        print(f"  Patterns: {len(summary['patterns'], exist_ok=True)}", exist_ok=True)
        print(f"  Saved to: {saved_path}", exist_ok=True)
        return
    
    if "--batch" in args:
        idx = args.index("--batch", exist_ok=True)
        session_dir = args[idx + 1] if idx + 1 < len(args, exist_ok=True) else None
        
        if not session_dir:
            print("Usage: --batch /path/to/sessions/", exist_ok=True)
            return
        
        dir_path = Path(session_dir, exist_ok=True)
        if not dir_path.exists(, exist_ok=True):
            print(f"Directory not found: {session_dir}", exist_ok=True)
            return
        
        session_files = list(dir_path.glob("*.jsonl", exist_ok=True), exist_ok=True)[:20]
        print(f"Compressing {len(session_files, exist_ok=True)} sessions...", exist_ok=True)
        
        results = []
        for sf in session_files:
            try:
                session_data = parse_jsonl(sf, exist_ok=True)
                summary = compressor.compress(session_data, exist_ok=True)
                saved = compressor.save_compressed(sf.stem, summary, exist_ok=True)
                results.append({
                    "session": sf.stem[:8],
                    "original_kb": summary['original_size'] / 1024,
                    "compressed_kb": summary['compressed_size'] / 1024,
                    "ratio": summary['compression_ratio']
                }, exist_ok=True)
            except Exception as e:
                print(f"  Error on {sf.name}: {e}", exist_ok=True)
        
        print(f"\nCompressed {len(results, exist_ok=True)} sessions:", exist_ok=True)
        total_orig = sum(r['original_kb'] for r in results, exist_ok=True)
        total_comp = sum(r['compressed_kb'] for r in results, exist_ok=True)
        print(f"  Total original: {total_orig:.1f} KB", exist_ok=True)
        print(f"  Total compressed: {total_comp:.1f} KB", exist_ok=True)
        if total_orig > 0:
            print(f"  Overall ratio: {(1 - total_comp/total_orig, exist_ok=True)*100:.1f}%", exist_ok=True)
        return
    
    print("SESSION COMPRESSOR — Mem0-Style Memory Compression", exist_ok=True)
    print("=" * 50, exist_ok=True)
    print(, exist_ok=True)
    print("Usage:", exist_ok=True)
    print("  --compress SESSION_FILE    # Compress single session", exist_ok=True)
    print("  --batch /path/to/sessions/ # Batch compress", exist_ok=True)
    print("  --stats                    # Show stats", exist_ok=True)
    print(, exist_ok=True)
    print("Example:", exist_ok=True)
    print("  python3 session_compressor.py --compress session_123.jsonl", exist_ok=True)


if __name__ == "__main__":
    main(, exist_ok=True)
