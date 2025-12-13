"""MCP Server for CALM environment tools.

Run this to start the FastMCP server that exposes tools for agents to use.

Usage:
    python3.11 envs/tools/server.py
"""

from data_tools import mcp

if __name__ == "__main__":
    print("Starting CALM MCP Server...")
    print("Available tools: get_persona, get_venue_hours")
    print("Press Ctrl+C to stop")
    mcp.run()

