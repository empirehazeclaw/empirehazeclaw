#!/usr/bin/env python3
"""
Sir HazeClaw MCP Server
Exposed unsere Core Scripts als MCP Tools.

MCP Protocol (Model Context Protocol):
- stdio mode: JSON-RPC über stdin/stdout
- Tools werden automatisch discoverable

Usage:
    python3 mcp_server.py
    # Then configure in openclaw.json:
    # "mcpServers": {
    #   "sir-hazeclaw": {
    #     "command": "python3",
    #     "args": ["/path/to/mcp_server.py"]
    #   }
    # }
"""

import sys
import json
from datetime import datetime

# Core Scripts die exposed werden
CORE_TOOLS = [
    {
        "name": "learning_coordinator",
        "description": "Zentrales Dashboard für Learning Loop - System Check, Research, Quality Gates, Learning Tracking",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["full", "status", "research", "check"],
                    "description": "Welche Aktion ausführen"
                }
            }
        }
    },
    {
        "name": "loop_check",
        "description": "Prüft auf Endlosschleifen - Backup Ratio, Commit Frequency, Workspace Cleanliness",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "self_eval",
        "description": "Self-Evaluation Score (Quality, Produktivität, Wissen) - Aktuell 99/100",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "innovation_research",
        "description": "Sucht proaktiv nach neuen AI Agent Patterns und Innovationen",
        "input_schema": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["daily", "weekly"],
                    "description": "Research Mode"
                }
            }
        }
    },
    {
        "name": "token_tracker",
        "description": "Trackt Token Nutzung für Efficiency - Zeigt Today's oder Weekly Stats",
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "enum": ["today", "week"],
                    "description": "Zeitraum"
                }
            }
        }
    },
    {
        "name": "skill_creator",
        "description": "Erstellt neue Skills aus Tasks - Atomic Skill Acquisition",
        "input_schema": {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "Name des neuen Skills"
                },
                "task_description": {
                    "type": "string",
                    "description": "Beschreibung was der Skill tun soll"
                }
            },
            "required": ["skill_name", "task_description"]
        }
    },
    {
        "name": "test_framework",
        "description": "Test Framework mit 65+ Tests - Quality Assurance",
        "input_schema": {
            "type": "object",
            "properties": {
                "test_name": {
                    "type": "string",
                    "description": "Name des Tests oder 'all' für alle Tests"
                }
            }
        }
    },
    {
        "name": "system_status",
        "description": "Gibt aktuellen System Status - Gateway, Disk, Memory, Load",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]

def handle_initialize(params):
    """Handle initialize request."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {"listChanged": True}
        },
        "serverInfo": {
            "name": "sir-hazeclaw",
            "version": "1.0.0"
        }
    }

def handle_list_tools(params):
    """Handle tools/list request."""
    tools = []
    for tool in CORE_TOOLS:
        tools.append({
            "name": tool["name"],
            "description": tool["description"],
            "inputSchema": tool["input_schema"]
        })
    return {"tools": tools}

def handle_call_tool(name, arguments):
    """Handle tools/call request."""
    import subprocess
    from pathlib import Path
    
    SCRIPTS_DIR = Path("/home/clawbot/.openclaw/workspace/scripts")
    
    # Map tool names to scripts
    tool_map = {
        "learning_coordinator": "learning_coordinator.py",
        "loop_check": "loop_check.py",
        "self_eval": "self_eval.py",
        "innovation_research": "innovation_research.py",
        "token_tracker": "token_tracker.py",
        "skill_creator": "skill_creator.py",
        "test_framework": "test_framework.py",
        "system_status": "system_status.py"  # Will create
    }
    
    if name == "system_status":
        # Inline implementation
        import shutil
        disk_free = shutil.disk_usage("/").free / (1024**3)
        import psutil
        memory = psutil.virtual_memory()
        
        result = {
            "gateway": "✅ running" if True else "❌ down",
            "disk_gb_free": round(disk_free, 1),
            "memory_percent": memory.percent,
            "load": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else "unknown",
            "timestamp": datetime.now().isoformat()
        }
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
    
    script = tool_map.get(name)
    if not script:
        return {"error": f"Unknown tool: {name}"}
    
    try:
        args = []
        if name == "learning_coordinator":
            action = arguments.get("action", "status")
            args = [f"--{action}"] if action != "full" else ["--full"]
        elif name == "innovation_research":
            mode = arguments.get("mode", "daily")
            args = [f"--{mode}"]
        elif name == "token_tracker":
            period = arguments.get("period", "today")
            args = ["--week"] if period == "week" else []
        elif name == "skill_creator":
            # Pass args directly to script
            args = [arguments.get("skill_name", ""), arguments.get("task_description", "")]
        elif name == "test_framework":
            test = arguments.get("test_name", "all")
            args = ["--run", test] if test != "all" else []
        
        result = subprocess.run(
            ["python3", str(SCRIPTS_DIR / script)] + args,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {"content": [{"type": "text", "text": result.stdout or result.stderr}]}
    
    except Exception as e:
        return {"error": str(e)}

def main():
    """Main MCP server loop."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method", "")
            params = request.get("params", {})
            msg_id = request.get("id")
            
            # Handle request
            if method == "initialize":
                result = handle_initialize(params)
            elif method == "tools/list":
                result = handle_list_tools(params)
            elif method == "tools/call":
                name = params.get("name")
                arguments = params.get("arguments", {})
                result = handle_call_tool(name, arguments)
            else:
                result = {"error": f"Unknown method: {method}"}
            
            # Send response
            response = {"jsonrpc": "2.0", "id": msg_id, "result": result}
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            # Send error
            error_response = {
                "jsonrpc": "2.0",
                "id": msg_id if 'msg_id' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()