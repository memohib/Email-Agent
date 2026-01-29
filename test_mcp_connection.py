# # Testing MCP Server

# ## Option 1: Let the Client Handle It (Recommended)

# The MCP client automatically starts the server when needed:

# ```python
# # The client does this automatically:
# # 1. Spawns server process: python mcp_servers/gmail_mcp_server/server.py
# # 2. Connects via stdio
# # 3. Calls tools
# # 4. Disconnects and kills server process
# ```

# Just run your main workflow:
# ```bash
# python app/main.py
# ```

# ---

# ## Option 2: Run Server Manually for Testing

# ### Start the Gmail MCP Server

# ```bash
# cd mcp_servers/gmail_mcp_server
# python server.py
# ```

# The server will start and wait for stdio input from an MCP client.

# ### Test with MCP Inspector (Optional)

# If you have the MCP inspector installed:

# ```bash
# npx @modelcontextprotocol/inspector python mcp_servers/gmail_mcp_server/server.py
# ```

# This opens a web UI to test your MCP server tools interactively.

# ---

# ## Option 3: Test Client Connection

# Create a test script to verify the MCP client can connect:

# ```python
# # test_mcp_connection.py
import asyncio
from app.mcp import MCPClient, get_server_path

async def test_connection():
    client = MCPClient()
    
    try:
        # Get server path
        server_path = get_server_path("gmail")
        print(f"Connecting to: {server_path}")
        
        # Connect
        await client.connect(server_path)
        print("✅ Connected!")
        
        # List tools
        tools = await client.list_tools()
        print(f"\n📋 Available tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
    finally:
        await client.disconnect()
        print("\n✅ Disconnected")

if __name__ == "__main__":
    asyncio.run(test_connection())
# ```

# Run it:
# ```bash
# python test_mcp_connection.py
# ```

# ---

# ## How It Works

# ```
# Your App (execute_action)
#   ↓ calls _invoke_mcp_tool("gmail.reply_thread", {...})
#   ↓
# MCPClient.connect(server_path)
#   ↓ spawns subprocess: python server.py
#   ↓ connects via stdin/stdout
#   ↓
# MCP Server Process (server.py)
#   ↓ receives tool call via stdio
#   ↓ executes gmail_reply_thread()
#   ↓ returns result via stdio
#   ↓
# MCPClient.disconnect()
#   ↓ kills server process
# ```

# The server is **ephemeral** - it starts when needed and stops when done!
