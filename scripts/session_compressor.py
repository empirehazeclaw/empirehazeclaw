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

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
COMPRESSED_DIR = WORKSPACE / "data" / "compressed_sessions"
COMPRESSED_DIR.mkdir(parents=True, exist_ok=True)

class SessionCompressor:
    """Compress session into high-density memory."""
    
    def __init__(self):
        self.decisions = []
        self.patterns = []
        self.lessons = []
        self.errors = []
        
    def compress(self, session_data: dict) -> dict:
        """
        Compress session into summary.
        
        Input: Full session JSON (~10KB+)
        Output: Compressed summary (~200B)
        """
        summary = {
            "date": session_data.get("date", "unknown"),
            "duration": session_data.get("duration", "unknown"),
            "decisions": [],
            "patterns": [],
            "lessons": [],
            "error_count": 0,
            "success_count": 0,
            "token_stats": {},
            "compressed_at": datetime.now(timezone.utc).isoformat(),
            "original_size": 0,
            "compressed_size": 0
        }
        
        # Extract from messages if present
        messages = session_data.get("messages", [])
        original_size = len(json.dumps(session_data))
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "assistant":
                # Check for decisions
                if any(kw in content.lower() for kw in ["decided", "choosing", "going with", "will use"]):
                    summary["decisions"].append(self._extract_decision(content))
                
                # Check for success indicators
                if any(kw in content.lower() for kw in ["success", "completed", "done", "✅"]):
                    summary["success_count"] += 1
                
                # Check for error indicators
                if any(kw in content.lower() for kw in ["error", "failed", "issue", "❌"]):
                    summary["error_count"] += 1
                    self._extract_error(content, summary)
                
                # Check for patterns
                self._extract_patterns(content, summary)
                
                # Check for lessons
                if any(kw in content.lower() for kw in ["learned", "insight", "key finding"]):
                    summary["lessons"].append(self._extract_lesson(content))
        
        # Deduplicate
        summary["decisions"] = list(dict.fromkeys(summary["decisions"]))[:10]
        summary["patterns"] = list(dict.fromkeys(summary["patterns"]))[:10]
        summary["lessons"] = list(dict.fromkeys(summary["lessons"]))[:5]
        
        # Calculate compression
        compressed_size = len(json.dumps(summary))
        compression_ratio = (1 - compressed_size / max(1, original_size)) * 100
        
        summary["original_size"] = original_size
        summary["compressed_size"] = compressed_size
        summary["compression_ratio"] = f"{compression_ratio:.1f}%"
        
        return summary
    
    def _extract_decision(self, content: str) -> str:
        """Extract decision from content."""
        sentences = content.split(".")
        for s in sentences:
            if any(kw in s.lower() for kw in ["decided", "choosing", "going with", "will use"]):
                return s.strip()[:100]
        return content[:80].strip()
    
    def _extract_error(self, content: str, summary: dict):
        """Extract error info."""
        error_match = re.search(r"(error|failed)[:\s]+([^\n.]+)", content, re.IGNORECASE)
        if error_match:
            error_type = error_match.group(2).strip()[:50]
            summary.setdefault("errors", [])
            if error_type not in summary["errors"]:
                summary["errors"].append(error_type)
    
    def _extract_patterns(self, content: str, summary: dict):
        """Extract patterns from content."""
        patterns = [
            ("timeout", "timeout_handling"),
            ("retry", "retry_logic"),
            ("cache", "caching"),
            ("kg_update", "knowledge_graph"),
            ("cron", "scheduling"),
            ("reflection", "reflection_pattern"),
            ("token", "token_optimization"),
        ]
        
        for keyword, pattern_name in patterns:
            if keyword in content.lower():
                if pattern_name not in summary["patterns"]:
                    summary["patterns"].append(pattern_name)
    
    def _extract_lesson(self, content: str) -> str:
        """Extract lesson from content."""
        sentences = content.split(".")
        for s in sentences:
            if any(kw in s.lower() for kw in ["learned", "insight", "key finding"]):
                return s.strip()[:100]
        return content[:80].strip()
    
    def save_compressed(self, session_id: str, summary: dict) -> str:
        """Save compressed session."""
        output_file = COMPRESSED_DIR / f"{session_id}.summary.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        return str(output_file)


def parse_jsonl(path: Path) -> dict:
    """Parse JSONL file into a session dict."""
    messages = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    msg = json.loads(line)
                    messages.append(msg)
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


def main():
    """CLI interface."""
    compressor = SessionCompressor()
    args = sys.argv[1:]
    
    if "--stats" in args:
        print("SESSION COMPRESSION STATS")
        print("=" * 50)
        
        compressed_files = list(COMPRESSED_DIR.glob("*.summary.json"))
        total_original = 0
        total_compressed = 0
        
        for f in compressed_files:
            with open(f) as fp:
                data = json.load(fp)
            total_original += data.get("original_size", 0)
            total_compressed += data.get("compressed_size", 0)
        
        print(f"  Compressed sessions: {len(compressed_files)}")
        if total_original > 0:
            ratio = (1 - total_compressed / total_original) * 100
            print(f"  Total original: {total_original / 1024:.1f} KB")
            print(f"  Total compressed: {total_compressed / 1024:.1f} KB")
            print(f"  Compression ratio: {ratio:.1f}%")
        return
    
    if "--compress" in args:
        idx = args.index("--compress")
        session_file = args[idx + 1] if idx + 1 < len(args) else None
        
        if not session_file:
            print("Usage: --compress SESSION_FILE")
            return
        
        path = Path(session_file)
        if not path.exists():
            print(f"File not found: {session_file}")
            return
        
        # Parse JSONL
        session_data = parse_jsonl(path)
        
        summary = compressor.compress(session_data)
        
        session_id = path.stem
        saved_path = compressor.save_compressed(session_id, summary)
        
        print(f"Compressed: {session_id}")
        print(f"  Original: {summary['original_size'] / 1024:.1f} KB")
        print(f"  Compressed: {summary['compressed_size'] / 1024:.2f} KB")
        print(f"  Ratio: {summary['compression_ratio']}")
        print(f"  Decisions: {len(summary['decisions'])}")
        print(f"  Patterns: {len(summary['patterns'])}")
        print(f"  Saved to: {saved_path}")
        return
    
    if "--batch" in args:
        idx = args.index("--batch")
        session_dir = args[idx + 1] if idx + 1 < len(args) else None
        
        if not session_dir:
            print("Usage: --batch /path/to/sessions/")
            return
        
        dir_path = Path(session_dir)
        if not dir_path.exists():
            print(f"Directory not found: {session_dir}")
            return
        
        session_files = list(dir_path.glob("*.jsonl"))[:20]
        print(f"Compressing {len(session_files)} sessions...")
        
        results = []
        for sf in session_files:
            try:
                session_data = parse_jsonl(sf)
                summary = compressor.compress(session_data)
                saved = compressor.save_compressed(sf.stem, summary)
                results.append({
                    "session": sf.stem[:8],
                    "original_kb": summary['original_size'] / 1024,
                    "compressed_kb": summary['compressed_size'] / 1024,
                    "ratio": summary['compression_ratio']
                })
            except Exception as e:
                print(f"  Error on {sf.name}: {e}")
        
        print(f"\nCompressed {len(results)} sessions:")
        total_orig = sum(r['original_kb'] for r in results)
        total_comp = sum(r['compressed_kb'] for r in results)
        print(f"  Total original: {total_orig:.1f} KB")
        print(f"  Total compressed: {total_comp:.1f} KB")
        if total_orig > 0:
            print(f"  Overall ratio: {(1 - total_comp/total_orig)*100:.1f}%")
        return
    
    print("SESSION COMPRESSOR — Mem0-Style Memory Compression")
    print("=" * 50)
    print()
    print("Usage:")
    print("  --compress SESSION_FILE    # Compress single session")
    print("  --batch /path/to/sessions/ # Batch compress")
    print("  --stats                    # Show stats")
    print()
    print("Example:")
    print("  python3 session_compressor.py --compress session_123.jsonl")


if __name__ == "__main__":
    main()
