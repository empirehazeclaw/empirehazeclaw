# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## 🎭 Ralph Loop Skill (2026-04-20)

### Skill Location
```
skills/ralph_loop/
├── SKILL.md                          # Complete Ralph Loop documentation
└── scripts/
    └── ralph_loop_adapter.py         # CLI tool for Ralph Loop patterns
```

### Ralph Loop Core Principle
```
Traditional Agent:  Observation → Reasoning → Acting → [LLM: fertig? → EXIT]
Ralph Loop:        Observation → Reasoning → Acting → [STOP HOOK: fertig? → NEIN → re-inject]
```

### Key Concepts
- **Stop Hook**: Intercepted exit attempts, re-injects prompt if not complete
- **Completion Promise**: `<promise>COMPLETE</promise>` als exit signal
- **Max-Iteration Safety**: Immer setzen, infinite loops sind gefährlich
- **Clean Context**: Jede Iteration = fresh AI instance
- **Learnings File**: `memory/ralph_learnings.md` für cross-iteration persistence

### Usage
```bash
# Check-only mode
python3 skills/ralph_loop/scripts/ralph_loop_adapter.py check --check "python3 score_checker.py"

# Full Ralph Loop
python3 skills/ralph_loop/scripts/ralph_loop_adapter.py loop <task_name> \
    --check "python3 score_checker.py" \
    --action "python3 learning_step.py" \
    --max-iterations 20

# Show learnings
python3 skills/ralph_loop/scripts/ralph_loop_adapter.py learnings
```

### Relevance für Sir HazeClaw
Bestehende Systeme die bereits Ralph-ähnlich arbeiten:
- Learning Loop v3 (Iteration → Score Check → Plateau Detection)
- Agent Executor (Queue-basiert, fresh instances)
- Health Agent (Check → Report → Self-heal)

## 🎤 Voice / Audio

### Whisper (Speech-to-Text)
**Schnellste Option:** `faster-whisper` mit `tiny` model
```python
from faster_whisper import WhisperModel
model = WhisperModel('tiny', device='cpu', compute_type='int8')
segments, info = model.transcribe('<file>.ogg', language='de')
text = ''.join([s.text for s in list(segments)])
```
- Load: ~0.6s | Transcribe: ~1s | **Total: ~2s** (30x schneller als original whisper)

**Alternativ:** whisper CLI (langsamer)
```bash
whisper "<audio-file>.ogg" --model base --language German --output_dir /tmp
```

### TTS
See TTS tool — configured and working.

---

## 🔄 System Integration (2026-04-16)

### Event Bus
```bash
python3 /workspace/scripts/event_bus.py stats           # Event Stats
python3 /workspace/scripts/event_bus.py list --type kg_update  # Filter
```

### Monitoring
```bash
python3 /workspace/scripts/integration_dashboard.py     # Full Dashboard
python3 /workspace/scripts/integration_dashboard.py --check  # Quick Check
python3 /workspace/scripts/stagnation_detector.py --check all  # Stagnation
```

### Evolver
```bash
bash /workspace/scripts/run_smart_evolver.sh            # Smart Evolver
```

### Backup Locations
- `backups/weekly_backup_*/` — Automated weekly (Sonntag 04:00 UTC)
- `backups/post_integration_20260416_210413/` — Post-Integration Full
- `backups/integration_backup_20260416_185449/` — Pre-Integration Backup
- `backups/core_ultralight_kg_stale_*.json` — Old KG (stale, kann gelöscht werden)

### New Scripts (2026-04-16)
| Script | Purpose |
|--------|---------|
| `learning_to_kg_sync.py` | Bridge Learning Loop → KG |
| `event_bus.py` | Cross-system event pub/sub |
| `stagnation_detector.py` | Monitor stagnation |
| `evolver_signal_bridge.py` | Feed signals to Evolver |
| `evolver_stagnation_breaker.py` | Force gene diversity |
| `integration_dashboard.py` | Unified monitoring |

---

## 🎯 Obsidian Integration (2026-04-19)

### Vault Setup
```
Vault Path: /home/clawbot/obsidian-vault/
CLI Tool:   notesmd (v0.3.5) → ~/.local/bin/notesmd
Config:     ~/.config/obsidian/obsidian.json
```

### Vault Structure
```
obsidian-vault/
├── README.md           # Index + navigation
├── daily/              # Daily notes (TEMPLATE.md + 2026-04-19.md)
├── notes/              # Core notes (MEMORY.md, USER.md)
├── tasks/              # Tasks & projects
├── system/             # System documentation
├── sync.sh             # Git commit + push
└── export_memory.sh    # Auto-export from MEMORY.md
```

### Sync Mechanism
```bash
# Manual sync
bash /home/clawbot/obsidian-vault/sync.sh

# Auto-export memory → vault (hourly via cron)
bash /home/clawbot/obsidian-vault/export_memory.sh
```

### For Nico (Tomorrow)
1. Install Obsidian from https://obsidian.md
2. Clone vault: `git clone https://github.com/empirehazeclaw/obsidian-vault.git`
3. Open vault in Obsidian
4. Install Excalidraw plugin in Obsidian (community plugins)
5. Done — all notes sync automatically via git hook

---

## 🎨 Excalidraw Integration (2026-04-19)

### CLI Tool
```bash
excalidraw-cli --help        # Commands: create, export, reference, checkpoint
excalidraw-cli reference     # Show element format reference
```

### Generate Diagrams
```bash
# Create from JSON
excalidraw-cli create --json '[{"type":"rectangle","x":100,"y":100,"width":200,"height":100}]' output.excalidraw

# Auto-generate architecture diagram
/home/clawbot/obsidian-vault/diagrams/generate_architecture.sh
```

### Stored Diagrams
```
obsidian-vault/diagrams/
├── sir-hazeclaw-architecture.excalidraw  # System architecture
├── generate_architecture.sh              # Auto-generate script
└── architecture.excalidraw.json          # Backup JSON
```

### Excalidraw Element Colors
| Color | Hex | Use |
|-------|-----|-----|
| Blue | `#a5d8ff` | Primary / CEO |
| Green | `#b2f2bb` | Success / Agents |
| Orange | `#ffd8a8` | Warning / Learning |
| Purple | `#d0bfff` | Processing / KG |
| Teal | `#c3fae8` | Data / Event Bus |
