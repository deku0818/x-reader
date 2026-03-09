# -*- coding: utf-8 -*-
"""Unit tests for x_reader.mcp_server module."""

import inspect

from mcp.server.fastmcp import FastMCP

from x_reader.mcp_server import create_mcp_server, run_server
from x_reader.reader import UniversalReader


class TestCreateMcpServer:
    """Tests for create_mcp_server()."""

    def test_returns_fastmcp_and_reader(self):
        """create_mcp_server() returns a (FastMCP, UniversalReader) tuple."""
        result = create_mcp_server()
        assert isinstance(result, tuple)
        assert len(result) == 2
        mcp, reader = result
        assert isinstance(mcp, FastMCP)
        assert isinstance(reader, UniversalReader)

    def test_registers_four_tools(self):
        """The FastMCP instance has exactly 4 registered tools."""
        mcp, _ = create_mcp_server()
        tools = mcp._tool_manager.list_tools()
        assert len(tools) == 4

    def test_registered_tool_names(self):
        """The 4 registered tools have the expected names."""
        mcp, _ = create_mcp_server()
        tools = mcp._tool_manager.list_tools()
        tool_names = {t.name for t in tools}
        expected = {"read_url", "read_batch", "list_inbox", "detect_platform"}
        assert tool_names == expected


class TestRunServerSignature:
    """Tests for run_server() function signature."""

    def test_run_server_signature_params(self):
        """run_server() has the correct parameter names and defaults."""
        sig = inspect.signature(run_server)
        params = sig.parameters

        assert "transport" in params
        assert params["transport"].default == "stdio"

        assert "host" in params
        assert params["host"].default == "127.0.0.1"

        assert "port" in params
        assert params["port"].default == 8000

    def test_run_server_return_annotation(self):
        """run_server() is annotated to return None."""
        sig = inspect.signature(run_server)
        assert sig.return_annotation is None



