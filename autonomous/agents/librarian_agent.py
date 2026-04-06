#!/usr/bin/env python3
"""
📚 LIBRARIAN AGENT
==================
Scans, organizes, and categorizes the knowledge base.
Builds the central INDEX.md and extracts decisions/learnings.
"""

import os
import re
from pathlib import Path
from datetime import datetime

WORKSPACE_DIR = Path("/home/clawbot/.openclaw/workspace")
MEMORY_DIR = WORKSPACE_DIR / "memory"
DATA_DIR = WORKSPACE_DIR / "data"

# Sub-directories
DIRS = {
    "decisions": MEMORY_DIR / "decisions",
    "learnings": MEMORY_DIR / "learnings",
    "archive": MEMORY_DIR / "archive",
    "projects": WORKSPACE_DIR / "projects"
}

def setup_dirs():
    for d in DIRS.values():
        d.mkdir(parents=True, exist_ok=True)

def process_memory_files():
    """Extract decisions and learnings from daily memory files"""
    print("📚 Scanne tägliche Memory-Dateien...")
    
    for file_path in MEMORY_DIR.glob("*.md"):
        # Skip special files
        if file_path.name in ["MEMORY.md", "INDEX.md"] or not re.match(r'\d{4}-\d{2}-\d{2}\.md', file_path.name):
            continue
            
        with open(file_path, "r") as f:
            content = f.read()
            
        # Extract decisions
        decisions = re.findall(r'### DECISION[^\n]*\n(.*?)(?=###|$)', content, re.DOTALL)
        if decisions:
            date_str = file_path.stem
            dec_file = DIRS["decisions"] / f"{date_str}_decisions.md"
            with open(dec_file, "w") as f:
                f.write(f"# Decisions from {date_str}\n\n")
                for d in decisions:
                    f.write(f"{d.strip()}\n\n---\n")
            print(f"  ✅ Extrahierte {len(decisions)} Decisions aus {file_path.name}")
            
        # Extract learnings
        learnings = re.findall(r'### LEARNING[^\n]*\n(.*?)(?=###|$)', content, re.DOTALL)
        if learnings:
            date_str = file_path.stem
            lrn_file = DIRS["learnings"] / f"{date_str}_learnings.md"
            with open(lrn_file, "w") as f:
                f.write(f"# Learnings from {date_str}\n\n")
                for l in learnings:
                    f.write(f"{l.strip()}\n\n---\n")
            print(f"  ✅ Extrahierte {len(learnings)} Learnings aus {file_path.name}")

def build_master_index():
    """Build a central INDEX.md mapping everything"""
    print("📚 Erstelle zentralen INDEX.md...")
    
    index_content = [
        "# 📚 EMPIREHAZECLAW MASTER INDEX",
        f"*Zuletzt aktualisiert: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n",
        "## 🏗️ Aktive Projekte",
    ]
    
    # Scan Projects
    if DIRS["projects"].exists():
        for p in DIRS["projects"].iterdir():
            if p.is_dir() and not p.name.startswith('.'):
                index_content.append(f"- **{p.name.title()}** (`projects/{p.name}/`)")
    
    index_content.extend([
        "\n## 🧠 Wichtige Entscheidungen (Decisions)",
    ])
    
    # Scan Decisions
    if DIRS["decisions"].exists():
        for d in sorted(DIRS["decisions"].glob("*.md"), reverse=True)[:10]:
            index_content.append(f"- [{d.stem}](memory/decisions/{d.name})")

    index_content.extend([
        "\n## 📈 Gelernte Lektionen (Learnings)",
    ])
    
    # Scan Learnings
    if DIRS["learnings"].exists():
        for l in sorted(DIRS["learnings"].glob("*.md"), reverse=True)[:10]:
            index_content.append(f"- [{l.stem}](memory/learnings/{l.name})")

    index_content.extend([
        "\n## 🗄️ Daten & Assets",
    ])
    
    # Scan Data
    if DATA_DIR.exists():
        for f in DATA_DIR.glob("*.json"):
            index_content.append(f"- `{f.name}`")

    index_file = WORKSPACE_DIR / "INDEX.md"
    with open(index_file, "w") as f:
        f.write("\n".join(index_content))
    
    print(f"  ✅ INDEX.md erfolgreich erstellt! ({len(index_content)} Zeilen)")

def run():
    print(f"[{datetime.now().isoformat()}] 🤓 Librarian Agent startet...")
    setup_dirs()
    process_memory_files()
    build_master_index()
    print("✅ Wissensdatenbank aufgeräumt und kategorisiert.")

if __name__ == "__main__":
    run()
