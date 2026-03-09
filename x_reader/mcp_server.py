# -*- coding: utf-8 -*-
"""
x-reader MCP Server module.

Provides `create_mcp_server()` to build a configured FastMCP instance
with all x-reader tools registered, and `run_server()` to start it.

Usage via CLI:
    x-reader mcp                        # stdio transport
    x-reader mcp --transport sse        # SSE transport
"""

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

from x_reader.reader import UniversalReader
from x_reader.schema import UnifiedInbox


def create_mcp_server(host: str = "127.0.0.1", port: int = 8000) -> tuple[FastMCP, UniversalReader]:
    """Create and return a configured FastMCP instance and reader.

    Args:
        host: Host to bind when using SSE/streamable-http transport.
        port: Port to bind when using SSE/streamable-http transport.

    Returns:
        A (FastMCP, UniversalReader) tuple with all MCP tools registered.
    """
    mcp = FastMCP(
        "x-reader",
        instructions="Universal content reader — give it any URL, get structured content back.",
        host=host,
        port=port,
    )

    reader = UniversalReader(inbox=UnifiedInbox())

    @mcp.tool()
    async def read_url(url: str) -> str:
        """
        Read content from any URL and return structured result.

        Supports: YouTube, Bilibili, X/Twitter, WeChat, Xiaohongshu,
        Telegram, RSS, and any generic web page.

        Returns JSON with: title, content, url, source_type, platform metadata.
        """
        import json

        content = await reader.read(url)
        result = content.to_dict()
        return json.dumps(result, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def read_batch(urls: list[str]) -> str:
        """
        Read multiple URLs concurrently. Returns JSON array of results.

        Failed URLs are logged but don't block other results.
        """
        import json

        contents = await reader.read_batch(urls)
        results = [c.to_dict() for c in contents]
        return json.dumps(results, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def list_inbox() -> str:
        """
        List all items in the content inbox.

        Returns JSON array of previously fetched content.
        """
        import json

        items = [item.to_dict() for item in reader.inbox.items]
        return json.dumps(items, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def detect_platform(url: str) -> str:
        """
        Detect which platform a URL belongs to.

        Returns the platform name: youtube, bilibili, twitter, wechat,
        xhs, telegram, rss, or generic.
        """
        return reader._detect_platform(url)

    return mcp, reader


def run_server(transport: str = "stdio", host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the MCP server.

    Args:
        transport: Transport mode, "stdio", "sse", or "streamable-http".
        host: Host to bind when using SSE/streamable-http transport.
        port: Port to bind when using SSE/streamable-http transport.
    """
    mcp, _reader = create_mcp_server(host=host, port=port)
    mcp.run(transport=transport)
