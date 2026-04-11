# 🔍 Path Verification Skill
**Created:** 2026-04-11
**Category:** debugging
**Priority:** HIGH

## Problem
`not found` Errors weil Pfade nicht existieren oder falsch geschrieben sind.

## Golden Rule
**"Verify BEFORE exec — not after!"**

## Path Verification Workflow

### Step 1: Check Existence
```bash
# Vor jedem exec mit Pfad:
ls -la /path/to/file  # File existiert?

# Oder für Verzeichnisse:
ls -d /path/to/dir/   # Verzeichnis existiert?
```

### Step 2: Find Missing Files
```bash
# Wenn File nicht existiert:
find /workspace -name "filename*" 2>/dev/null

# Oder:
find /home/clawbot/.openclaw/workspace -name "*part_of_name*"
```

### Step 3: Validate Path Structure
```python
# Immer absolute Pfade:
✅ /home/clawbot/.openclaw/workspace/scripts/script.py
❌ ~/workspace/scripts/script.py  # Keine ~ expansion!

# Check ob parent dirs existieren:
Path("/完整/pfad").parent.exists()
```

---

## Common "Not Found" Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| `script.py not found` | Falscher Pfad | `ls` im richtigen Verzeichnis |
| `No such file` | Tippfehler | Case-sensitive prüfen |
| `Path escapes sandbox` | Sicherheitsblock | Nur workspace-Pfade |
| `File exists not` | Read-Instead-Write | `read()` first, then `edit()` |

---

## Anti-Patterns

❌ ** NICHT:
- Annahme dass File existiert
- `~` in Pfaden
- Relative Pfade ohne cwd-Prüfung
- case-sensitive Ignorierung

✅ ** SONDERN:
- Immer erst `ls` oder `find`
- Absolute Pfade
- Case-sensitive prüfen
- Exakte Schreibweise

---

## Quick Verification Script

```python
from pathlib import Path

def verify_path(path: str) -> bool:
    """Verifiziert ob Pfad existiert."""
    p = Path(path)
    
    if not p.exists():
        print(f"❌ Not found: {path}")
        # Try to find similar
        parent = p.parent
        if parent.exists():
            print(f"   Similar in {parent}:")
            for f in parent.glob("*"):
                if p.name.split('.')[0] in f.name:
                    print(f"   - {f.name}")
        return False
    
    return True

# Usage:
if verify_path("/path/to/script.py"):
    exec_file("/path/to/script.py")
```

---

## Workflow Checklist

- [ ] Pfad ist absolut (nicht `~`)
- [ ] Schreibweise ist exakt
- [ ] Parent-Verzeichnis existiert
- [ ] File existiert (`ls`)
- [ ] Berechtigungen korrekt

---

## Metrics

**Path Error Rate:**
```
(not_found_errors / total_path_ops) × 100
```

Ziel: < 5%

---

*Sir HazeClaw — Path Verification Master*
