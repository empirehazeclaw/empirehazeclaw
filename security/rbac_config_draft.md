# RBAC Implementation für openclaw.json
# SECURITY OFFICER — EmpireHazeClaw Fleet
# Datum: 2026-04-08
# Status: BEREIT FÜR IMPLEMENTIERUNG (CEO muss bestätigen)

# =============================================================================
# TEIL 1: GLOBAL SECURITY DEFAULTS
# =============================================================================

"tools": {
  # Basis-Profil: ERLAUBT NUR SICHERE TOOLS
  # Weitere Restriktionen via allow/deny Listen
  "profile": "safe",

  # Globale Tool-Allowlist (WHITELIST = nur diese Tools sind erlaubt)
  # Ergänzt profile, wird nicht überschrieben
  "allow": [
    "read",
    "write",
    "edit",
    "sessions_send",
    "sessions_list",
    "sessions_history",
    "memory_search",
    "memory_get",
    "cron",
    "subagents",
    "web_search",
    "web_fetch",
    "image",
    "image_generate"
  ],

  # Explizite DENYLIST (deny gewinnt IMMER über allow)
  "deny": [
    # Diese Tools sind DEAKTIVIERT bis auf per-agent Erlaubnis
    "exec",              # Shell-Commands — NUR mit Approval
    "tts",              # Text-to-Speech — NUR CEO
    "message",          # Externes Messaging — NUR CEO + Security (nach Approval)
    "music_generate",   # Audio-Generation
    "video_generate"    # Video-Generation
  ]
},

# =============================================================================
# TEIL 2: PER-AGENT CONFIGURATION
# =============================================================================

"agents": {
  "defaults": {
    # SANDBOX STANDARDMÄSSIG AKTIV
    "sandbox": {
      "mode": "all",
      "workspaceAccess": "own"
    },
    # HEARTBEAT FÜR ALLE AGENTS
    "heartbeat": {
      "every": "30m",
      "target": "last",
      "lightContext": true
    }
  },

  "list": [
    # ---------------------------------------------------------
    # CEO — Master Orchestrator (ADMIN)
    # ---------------------------------------------------------
    {
      "id": "ceo",
      "tools": {
        "allow": ["*"],          # Alle Tools erlaubt
        "deny": []
      },
      "sandbox": {
        "mode": "off"           # CEO braucht Full Access für Orchestrierung
      }
    },

    # ---------------------------------------------------------
    # SECURITY OFFICER — Audit + Investigation
    # ---------------------------------------------------------
    {
      "id": "security_officer",
      "workspace": "/home/clawbot/.openclaw/workspace/security",
      "tools": {
        "allow": [
          "read", "write", "edit",
          "exec",                 # Für Scanner
          "web_search", "web_fetch",
          "sessions_send", "sessions_list", "sessions_history",
          "memory_search", "memory_get",
          "cron", "subagents"
        ],
        "deny": [
          "tts",
          "music_generate",
          "video_generate"
        ],
        # EXEC SECURITY: Nur erlaubte Verzeichnisse
        "exec": {
          "allow": ["python3", "bash", "sh", "ls", "cat", "grep", "find", "head", "tail"],
          "dir": ["/home/clawbot/.openclaw/workspace/security"]
        }
      },
      "sandbox": {
        "mode": "all",
        "workspaceAccess": "own"
      }
    },

    # ---------------------------------------------------------
    # BUILDER — Coding + Scripts
    # ---------------------------------------------------------
    {
      "id": "builder",
      "workspace": "/home/clawbot/.openclaw/workspace/builder",
      "tools": {
        "allow": [
          "read", "write", "edit",
          "exec",                 # Scripts ausführen
          "sessions_send", "sessions_list",
          "memory_search", "memory_get",
          "cron"
        ],
        "deny": [
          "web_search", "web_fetch",  # Kein Surfen beim Coden
          "tts",
          "music_generate",
          "video_generate",
          "message"
        ],
        "exec": {
          "allow": ["python3", "bash", "sh", "node", "npm", "git", "ls", "cat", "grep"],
          "dir": ["/home/clawbot/.openclaw/workspace/builder", "/home/clawbot/.openclaw/workspace/scripts"]
        }
      },
      "sandbox": {
        "mode": "all",
        "workspaceAccess": "own"
      }
    },

    # ---------------------------------------------------------
    # DATA MANAGER — Memory + DB
    # ---------------------------------------------------------
    {
      "id": "data_manager",
      "workspace": "/home/clawbot/.openclaw/workspace/data",
      "tools": {
        "allow": [
          "read", "write", "edit",
          "exec",                 # DB-Operationen
          "sessions_send", "sessions_list",
          "memory_search", "memory_get",
          "cron"
        ],
        "deny": [
          "web_search", "web_fetch",
          "tts", "message",
          "music_generate",
          "video_generate"
        ],
        "exec": {
          "allow": ["python3", "bash", "ls", "cat", "grep", "sqlite3"],
          "dir": ["/home/clawbot/.openclaw/workspace/data", "/home/clawbot/.openclaw/workspace/memory"]
        }
      },
      "sandbox": {
        "mode": "all",
        "workspaceAccess": "own"
      }
    },

    # ---------------------------------------------------------
    # RESEARCH — Web + Recherche
    # ---------------------------------------------------------
    {
      "id": "research",
      "workspace": "/home/clawbot/.openclaw/workspace/research",
      "tools": {
        "allow": [
          "read", "write",
          "web_search", "web_fetch",
          "sessions_send", "sessions_list",
          "memory_search", "memory_get"
        ],
        "deny": [
          "exec",               # KEINE Shell Commands
          "edit",               # Nur Lesen, kein direktes Edit (Review-Prozess)
          "tts", "message",
          "music_generate",
          "video_generate"
        ]
      },
      "sandbox": {
        "mode": "all",
        "workspaceAccess": "own"
      }
    },

    # ---------------------------------------------------------
    # QC OFFICER — Validation only
    # ---------------------------------------------------------
    {
      "id": "qc_officer",
      "workspace": "/home/clawbot/.openclaw/workspace/qc",
      "tools": {
        "allow": [
          "read", "write",
          "sessions_send", "sessions_list", "sessions_history",
          "memory_search", "memory_get",
          "cron"
        ],
        "deny": [
          "exec",
          "web_search", "web_fetch",
          "edit",               # QC liest + validiert, editiert NICHT
          "tts", "message",
          "music_generate",
          "video_generate"
        ]
      },
      "sandbox": {
        "mode": "all",
        "workspaceAccess": "own"
      }
    }
  ]
},

# =============================================================================
# TEIL 3: SANDBOX + GATEWAY HARDENING
# =============================================================================

"gateway": {
  "port": 18789,
  "mode": "local",
  "bind": "loopback",
  "auth": {
    "mode": "token",
    "token": "***CURRENT***"
  },
  "tailscale": {
    "mode": "off"
  },
  "nodes": {
    # KRITISCH: Diese Commands sind FÜR ALLE geblockt
    "denyCommands": [
      "rm",                  # Immer mit Nachfrage
      "rmdir",               # Verzeichnis-Löschung
      "shutdown",            # System-Shutdown
      "reboot",              # Neustart
      "halt",                # Stop
      "mkfs",                # Filesystem erstellen
      "dd",                  # Direct drive access
      ":!",                  # Shell-Escape
      ">/dev/sda",           # Direct disk write
      "|bash",               # Pipe to bash
      ";bash",               # Semicolon bash
      "$(bash",              # Command substitution
      "`bash"                # Backtick execution
    ]
  }
},

# =============================================================================
# TEIL 4: INPUT VALIDATION (für exec und andere Tools)
# =============================================================================

# Hinweis: Input-Validation wird durch das Builder-Script implementiert
#builder/input_validation.js — muss als Hook oder Pre-Tool-Call integriert werden
#Dies ist eine KONFIGURATIONS-REFERENZ, keine Code-Änderung

# =============================================================================
# ROLLBACK-PLAN
# =============================================================================
# Bei Problemen:
# 1. openclaw gateway stop
# 2. Backup der config einspielen
# 3. openclaw gateway start
#
# Backup erstellen:
# cp /home/clawbot/.openclaw/openclaw.json /home/clawbot/.openclaw/openclaw.json.backup.2026-04-08
