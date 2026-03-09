# -*- coding: utf-8 -*-
"""Tests for cmd_mcp() in x_reader.cli — property-based and unit tests."""

import sys
from unittest.mock import patch, MagicMock
import pytest
from hypothesis import given, strategies as st, settings

from x_reader.cli import cmd_mcp


def _run_cmd_mcp_with_mock(args: list[str]) -> MagicMock:
    """Run cmd_mcp(args) with run_server mocked, return the mock."""
    mock_run = MagicMock()
    with patch("x_reader.mcp_server.run_server", mock_run):
        cmd_mcp(args)
    return mock_run


# ---------------------------------------------------------------------------
# Property-Based Tests
# ---------------------------------------------------------------------------

class TestProperty1ArgumentParsing:
    """Property 1: 参数解析正确性

    **Validates: Requirements 2.1**
    """

    @given(
        transport=st.sampled_from(["stdio", "sse"]),
        host=st.text(
            alphabet=st.characters(whitelist_categories=("L", "N", "P")),
            min_size=1,
            max_size=50,
        ),
        port=st.integers(min_value=1, max_value=65535),
    )
    @settings(max_examples=100)
    def test_parsed_args_match_input(self, transport, host, port):
        """cmd_mcp() forwards parsed args to run_server() unchanged."""
        args = ["--transport", transport, "--host", host, "--port", str(port)]
        mock_run = _run_cmd_mcp_with_mock(args)
        mock_run.assert_called_once_with(transport, host, port)


# ---------------------------------------------------------------------------
# Unit Tests
# ---------------------------------------------------------------------------

class TestCmdMcpUnitTests:

    def test_default_args(self):
        """cmd_mcp([]) uses defaults: stdio, 127.0.0.1, 8000."""
        mock_run = _run_cmd_mcp_with_mock([])
        mock_run.assert_called_once_with("stdio", "127.0.0.1", 8000)

    def test_sse_with_custom_host_port(self):
        """cmd_mcp parses --transport sse --host 0.0.0.0 --port 9000."""
        args = ["--transport", "sse", "--host", "0.0.0.0", "--port", "9000"]
        mock_run = _run_cmd_mcp_with_mock(args)
        mock_run.assert_called_once_with("sse", "0.0.0.0", 9000)

    def test_invalid_transport_exits(self):
        with pytest.raises(SystemExit) as exc_info:
            cmd_mcp(["--transport", "grpc"])
        assert exc_info.value.code == 1

    def test_invalid_transport_message(self, capsys):
        with pytest.raises(SystemExit):
            cmd_mcp(["--transport", "grpc"])
        captured = capsys.readouterr()
        assert "无效的 transport 模式: grpc" in captured.out

    def test_invalid_port_exits(self):
        with pytest.raises(SystemExit) as exc_info:
            cmd_mcp(["--port", "abc"])
        assert exc_info.value.code == 1

    def test_invalid_port_message(self, capsys):
        with pytest.raises(SystemExit):
            cmd_mcp(["--port", "abc"])
        captured = capsys.readouterr()
        assert "无效的端口号: abc" in captured.out

    def test_mcp_dependency_missing(self, capsys):
        saved = sys.modules.get("x_reader.mcp_server")
        sys.modules["x_reader.mcp_server"] = None

        try:
            with pytest.raises(SystemExit) as exc_info:
                cmd_mcp([])
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "MCP 依赖未安装" in captured.out
            assert "pip install x-reader[mcp]" in captured.out
        finally:
            if saved is not None:
                sys.modules["x_reader.mcp_server"] = saved
            else:
                sys.modules.pop("x_reader.mcp_server", None)


# ---------------------------------------------------------------------------
# Property 3: 延迟导入隔离性
# ---------------------------------------------------------------------------

class TestProperty3LazyImportIsolation:

    @given(command=st.sampled_from(["list", "clear"]))
    @settings(max_examples=100)
    def test_non_mcp_commands_do_not_import_mcp_server(self, command):
        saved = sys.modules.pop("x_reader.mcp_server", None)

        try:
            with patch.object(sys, "argv", ["x-reader", command]):
                with patch("x_reader.cli.cmd_list"), \
                     patch("x_reader.cli.cmd_clear"):
                    from x_reader.cli import main
                    main()

            assert "x_reader.mcp_server" not in sys.modules
        finally:
            if saved is not None:
                sys.modules["x_reader.mcp_server"] = saved


# ---------------------------------------------------------------------------
# Help text
# ---------------------------------------------------------------------------

class TestHelpTextIncludesMcp:

    def test_help_text_contains_mcp(self, capsys):
        with patch.object(sys, "argv", ["x-reader"]):
            from x_reader.cli import main
            main()

        captured = capsys.readouterr()
        assert "mcp" in captured.out
