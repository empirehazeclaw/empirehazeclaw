# ⚡ Autonomous Coding Skill
**Created:** 2026-04-11
**Category:** coding
**Times Used:** 0

## When to Use
When implementing scripts, fixing bugs, or creating new functionality.

## Workflow
```
1. REQUIREMENT - Was muss das Script tun?
2. DESIGN - Kurzer Plan, max 3 Steps
3. IMPLEMENT - Code schreiben
4. TEST - Script ausführen
5. REFINE - Debug falls nötig
6. COMMIT - Git commit mit Message
```

## Golden Rules
- **Einfachheit > Komplexität**
- **Erst tun, dann dokumentieren**
- **Testen bevor Commit**

## Script Template
```python
#!/usr/bin/env python3
"""
[Script Name] - [Kurzbeschreibung]
Usage: python3 [script].py [args]
"""

import sys
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

def main():
    # TODO: Implement
    pass

if __name__ == "__main__":
    main()
```

## Anti-Patterns (Vermeiden)
- ❌ Keine Skripte ohne Tests
- ❌ Nicht 10 Varianten bevor eine funktioniert
- ❌ Nicht vergessen zu committen

## Success Criteria
- [ ] Script funktioniert
- [ ] Getestet
- [ ] Committed
- [ ] Dokumentiert (wenn nötig)
