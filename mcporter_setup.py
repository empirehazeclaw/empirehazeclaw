#!/usr/bin/env python3
"""MCPorter - MCP Servers Management"""
import subprocess
import sys
import json

def list_servers():
    """List available MCP servers"""
    result = subprocess.run(["mcporter", "list"], capture_output=True, text=True)
    return result.stdout

def add_server(name, config):
    """Add MCP server"""
    cmd = ["mcporter", "add", name, "--config", json.dumps(config)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def call_server(server, tool, args):
    """Call MCP server tool"""
    cmd = ["mcporter", "call", server, tool, json.dumps(args)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

# Popular MCP servers to add
SUGGESTED_SERVERS = {
    "filesystem": {"type": "stdio", "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]},
    "git": {"type": "stdio", "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]},
    "memory": {"type": "stdio", "command": "npx", "args": ["-y", "@modelcontextprotocol/server-memory"]},
}

if __name__ == "__main__":
    print("=== 🔌 MCPORTER SETUP ===")
    print(list_servers())
    print("\nSuggested servers to add:")
    for name in SUGGESTED_SERVERS:
        print(f"  - {name}")
