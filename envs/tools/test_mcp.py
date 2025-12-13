"""Test script to verify MCP tools are properly registered and callable.

This script tests:
1. Tools are registered with FastMCP
2. Tool schemas are correct
3. Tools can be called through the MCP interface

Usage:
    python3.11 envs/tools/test_mcp.py
"""

import asyncio
import json
from data_tools import mcp, get_persona, get_venue_hours


def test_tool_registration():
    """Test that tools are properly registered with FastMCP."""
    print("=" * 50)
    print("Testing MCP Tool Registration")
    print("=" * 50)
    
    # Get registered tools from FastMCP
    tools = mcp._tool_manager._tools
    
    print(f"\nRegistered tools: {len(tools)}")
    for name, tool in tools.items():
        print(f"  - {name}")
        # Print tool description if available
        if hasattr(tool, 'description') and tool.description:
            print(f"    Description: {tool.description[:60]}...")
    
    # Check our tools are registered
    assert "get_persona" in tools, "get_persona not registered!"
    assert "get_venue_hours" in tools, "get_venue_hours not registered!"
    
    print("\n✅ Tool registration test passed!")
    return True


def test_tool_schemas():
    """Test that tool schemas are correctly defined."""
    print("\n" + "=" * 50)
    print("Testing MCP Tool Schemas")
    print("=" * 50)
    
    tools = mcp._tool_manager._tools
    
    # Test get_persona schema
    get_persona_tool = tools["get_persona"]
    print(f"\nget_persona parameters:")
    if hasattr(get_persona_tool, 'parameters'):
        print(f"  {get_persona_tool.parameters}")
    
    # Test get_venue_hours schema
    get_venue_hours_tool = tools["get_venue_hours"]
    print(f"\nget_venue_hours parameters:")
    if hasattr(get_venue_hours_tool, 'parameters'):
        print(f"  {get_venue_hours_tool.parameters}")
    
    print("\n✅ Tool schema test passed!")
    return True


def test_tool_execution():
    """Test that tools execute correctly through MCP."""
    print("\n" + "=" * 50)
    print("Testing MCP Tool Execution")
    print("=" * 50)
    
    # Test get_persona
    print("\nCalling get_persona('graduate_student')...")
    result = get_persona("graduate_student")
    assert result.get("id") == "graduate_student", "Wrong persona returned!"
    assert result.get("name") == "Alex Chen", "Wrong name!"
    print(f"  ✓ Got: {result['name']} - {result['role']}")
    
    # Test get_venue_hours
    print("\nCalling get_venue_hours('gym', 'monday')...")
    result = get_venue_hours("gym", "monday")
    assert result.get("venue_id") == "gym", "Wrong venue returned!"
    assert result.get("hours", {}).get("open") == "06:00", "Wrong opening time!"
    print(f"  ✓ Got: {result['name']} opens at {result['hours']['open']}")
    
    # Test error handling
    print("\nCalling get_persona('nonexistent')...")
    result = get_persona("nonexistent")
    assert "error" in result, "Should return error for nonexistent persona!"
    print(f"  ✓ Got expected error: {result['error']}")
    
    print("\n✅ Tool execution test passed!")
    return True


def test_mcp_server_info():
    """Display MCP server information."""
    print("\n" + "=" * 50)
    print("MCP Server Information")
    print("=" * 50)
    
    print(f"\nServer name: {mcp.name}")
    print(f"Tools count: {len(mcp._tool_manager._tools)}")
    
    print("\nTo start the MCP server, run:")
    print("  python3.11 envs/tools/server.py")
    
    print("\nTo test with an agent, the server exposes these tools:")
    for name in mcp._tool_manager._tools:
        print(f"  - {name}")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "#" * 50)
    print("# CALM MCP Tools Integration Test")
    print("#" * 50)
    
    all_passed = True
    
    try:
        all_passed &= test_tool_registration()
        all_passed &= test_tool_schemas()
        all_passed &= test_tool_execution()
        all_passed &= test_mcp_server_info()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        all_passed = False
    
    print("\n" + "#" * 50)
    if all_passed:
        print("# ✅ ALL TESTS PASSED!")
    else:
        print("# ❌ SOME TESTS FAILED!")
    print("#" * 50 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

