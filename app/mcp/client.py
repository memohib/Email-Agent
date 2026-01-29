"""
MCP Client Wrapper

Provides a simple interface to connect to MCP servers and invoke tools.
"""

import asyncio
from typing import Optional, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """
    MCP Client for connecting to and invoking tools from MCP servers.
    """
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.connected_server: Optional[str] = None
    
    async def connect(self, server_script_path: str):
        """
        Connect to an MCP server.
        
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        # Determine command based on file extension
        if server_script_path.endswith('.py'):
            command = "python"
        elif server_script_path.endswith('.js'):
            command = "node"
        else:
            raise ValueError("Server script must be a .py or .js file")
        
        # Set up server parameters
        import os
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=os.environ.copy()  # Inherit environment variables
        )
        
        # Connect via stdio
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        
        # Create session
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        
        # Initialize session
        await self.session.initialize()
        
        self.connected_server = server_script_path
    
    async def list_tools(self) -> list:
        """
        List available tools from the connected server.
        
        Returns:
            List of tool objects with name, description, and input schema
        """
        if not self.session:
            raise RuntimeError("Not connected to any MCP server")
        
        response = await self.session.list_tools()
        return response.tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the connected MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        if not self.session:
            raise RuntimeError("Not connected to any MCP server")
        
        result = await self.session.call_tool(tool_name, arguments)
        return result
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        await self.exit_stack.aclose()
        self.session = None
        self.connected_server = None
    
    def __repr__(self):
        status = f"connected to {self.connected_server}" if self.session else "disconnected"
        return f"<MCPClient {status}>"
