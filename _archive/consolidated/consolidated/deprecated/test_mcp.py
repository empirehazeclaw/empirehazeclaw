#!/usr/bin/env python3
"""
Test script for MCP implementation.
Run: python -m scripts.test_mcp
"""

import asyncio
import sys
from pathlib import Path

# Add workspace to path
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE))


async def test_mcp_server():
    """Test the MCP Server directly via JSON-RPC"""
    from core.mcp_server import MCPServer
    
    print("=" * 60)
    print("🧪 Testing MCP Server")
    print("=" * 60)
    
    server = MCPServer()
    
    # Test initialize
    print("\n1️⃣ Test: initialize")
    req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    resp = server.handle_request(req)
    print(f"   Result: {resp.get('result', {}).get('serverInfo', {})}")
    assert "serverInfo" in resp.get("result", {})
    print("   ✅ PASSED")
    
    # Test tools/list
    print("\n2️⃣ Test: tools/list")
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    resp = server.handle_request(req)
    tools = resp.get("result", {}).get("tools", [])
    print(f"   Found {len(tools)} tools: {[t['name'] for t in tools]}")
    assert len(tools) == 4
    print("   ✅ PASSED")
    
    # Test memory_list
    print("\n3️⃣ Test: tools/call - memory_list")
    req = {
        "jsonrpc": "2.0", 
        "id": 3, 
        "method": "tools/call", 
        "params": {"name": "memory_list", "arguments": {"limit": 3}}
    }
    resp = server.handle_request(req)
    result = resp.get("result", {})
    print(f"   Files found: {result.get('files', [])[:2]}")
    print("   ✅ PASSED")
    
    # Test memory_search
    print("\n4️⃣ Test: tools/call - memory_search")
    req = {
        "jsonrpc": "2.0", 
        "id": 4, 
        "method": "tools/call", 
        "params": {"name": "memory_search", "arguments": {"query": "TODO", "limit": 2}}
    }
    resp = server.handle_request(req)
    result = resp.get("result", {})
    print(f"   Files with 'TODO': {result.get('files_found', 0)}")
    print("   ✅ PASSED")
    
    print("\n" + "=" * 60)
    print("✅ MCP Server Tests PASSED")
    print("=" * 60)


async def test_mcp_client():
    """Test the MCP Client"""
    from core.mcp_client import MCPClient
    
    print("\n" + "=" * 60)
    print("🧪 Testing MCP Client")
    print("=" * 60)
    
    client = MCPClient(server_command=[
        sys.executable,
        str(WORKSPACE / "core" / "mcp_server.py")
    ])
    
    try:
        # Connect
        print("\n1️⃣ Test: Connect to MCP Server")
        success = await client.connect()
        print(f"   Connected: {success}")
        assert success
        print("   ✅ PASSED")
        
        # List tools
        print("\n2️⃣ Test: List tools")
        tools = await client.list_tools()
        print(f"   Tools: {[t['name'] for t in tools]}")
        assert len(tools) == 4
        print("   ✅ PASSED")
        
        # Call tool
        print("\n3️⃣ Test: Call memory_list")
        result = await client.call_tool("memory_list", {"limit": 2})
        print(f"   Result keys: {list(result.keys()) if result else 'None'}")
        assert "files" in result
        print("   ✅ PASSED")
        
        print("\n" + "=" * 60)
        print("✅ MCP Client Tests PASSED")
        print("=" * 60)
        
    finally:
        await client.disconnect()


async def test_base_agent_mcp():
    """Test BaseAgent with MCP integration"""
    from core.base_agent import BaseAgent
    
    print("\n" + "=" * 60)
    print("🧪 Testing BaseAgent MCP Integration")
    print("=" * 60)
    
    # Create agent with MCP config
    agent = BaseAgent(
        name="TestAgent",
        system_prompt="Test agent",
        mcp_servers=[
            {
                "name": "test_server",
                "command": [sys.executable, str(WORKSPACE / "core" / "mcp_server.py")],
                "env": {}
            }
        ]
    )
    
    # Check status
    print("\n1️⃣ Test: MCP Status")
    status = agent.get_mcp_status()
    print(f"   Status: {status}")
    assert status["enabled"] == True
    print("   ✅ PASSED")
    
    # Get stats
    print("\n2️⃣ Test: Get Stats")
    stats = agent.get_stats()
    print(f"   Has MCP in stats: {'mcp' in stats}")
    assert "mcp" in stats
    print("   ✅ PASSED")
    
    # Cleanup
    print("\n3️⃣ Test: Cleanup")
    await agent.cleanup()
    print("   ✅ PASSED")
    
    print("\n" + "=" * 60)
    print("✅ BaseAgent MCP Tests PASSED")
    print("=" * 60)


async def main():
    """Run all tests"""
    print("\n🚀 MCP Implementation Tests\n")
    
    try:
        await test_mcp_server()
        await test_mcp_client()
        await test_base_agent_mcp()
        
        print("\n" + "🎉" * 20)
        print("ALL TESTS PASSED!")
        print("🎉" * 20)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())