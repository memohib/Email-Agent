"""
MCP Server Configuration

Maps service names to MCP server script paths.
"""

import os

# Base directory for MCP servers
MCP_SERVERS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "mcp_servers")

# Service to server path mapping
MCP_SERVERS = {
    "gmail": os.path.join(MCP_SERVERS_DIR, "gmail_mcp_server", "server.py"),
    # Add more servers as needed
    # "calendar": os.path.join(MCP_SERVERS_DIR, "calendar_mcp_server", "server.py"),
}

def get_server_path(service: str) -> str:
    """Get the absolute path to an MCP server script."""
    if service not in MCP_SERVERS:
        raise ValueError(f"Unknown MCP service: {service}")
    
    path = os.path.abspath(MCP_SERVERS[service])
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"MCP server not found: {path}")
    
    return path
