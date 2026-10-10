from datetime import datetime

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("MyFirstMCP")


@mcp.tool()
def say_hello(name: str) -> str:
    """Say hello to a person."""
    return f"Hello {name}"


@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def get_current_time() -> str:
    """Get current server date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
