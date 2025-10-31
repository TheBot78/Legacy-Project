import pytest
from io import StringIO
import sys
from rpc.server.util import log


class TestRPCServerUtil:
    """Tests for RPC server util module."""

    def test_log_simple_message(self, capsys):
        """Test logging a simple message."""
        log("Test message")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] Test message\n"

    def test_log_empty_message(self, capsys):
        """Test logging an empty message."""
        log("")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] \n"

    def test_log_message_with_spaces(self, capsys):
        """Test logging a message with spaces."""
        log("This is a test message with spaces")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] This is a test message with spaces\n"

    def test_log_message_with_special_characters(self, capsys):
        """Test logging a message with special characters."""
        log("Message with special chars: !@#$%^&*()")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] Message with special chars: !@#$%^&*()\n"

    def test_log_message_with_unicode(self, capsys):
        """Test logging a message with unicode characters."""
        log("Unicode message: Héllo wörld! 🌍")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] Unicode message: Héllo wörld! 🌍\n"

    def test_log_message_with_newlines(self, capsys):
        """Test logging a message with newlines."""
        log("Line 1\nLine 2\nLine 3")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] Line 1\nLine 2\nLine 3\n"

    def test_log_message_with_tabs(self, capsys):
        """Test logging a message with tabs."""
        log("Message\twith\ttabs")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] Message\twith\ttabs\n"

    def test_log_numeric_string(self, capsys):
        """Test logging a numeric string."""
        log("12345")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] 12345\n"

    def test_log_json_like_string(self, capsys):
        """Test logging a JSON-like string."""
        log('{"key": "value", "number": 42}')
        captured = capsys.readouterr()
        assert captured.out == '[RPC] {"key": "value", "number": 42}\n'

    def test_log_multiple_calls(self, capsys):
        """Test multiple log calls."""
        log("First message")
        log("Second message")
        log("Third message")
        captured = capsys.readouterr()
        expected = (
            "[RPC] First message\n"
            "[RPC] Second message\n"
            "[RPC] Third message\n"
        )
        assert captured.out == expected

    def test_log_long_message(self, capsys):
        """Test logging a very long message."""
        long_message = "A" * 1000
        log(long_message)
        captured = capsys.readouterr()
        assert captured.out == f"[RPC] {long_message}\n"

    def test_log_message_with_quotes(self, capsys):
        """Test logging a message with quotes."""
        log('Message with "double" and \'single\' quotes')
        captured = capsys.readouterr()
        assert captured.out == '[RPC] Message with "double" and \'single\' quotes\n'

    def test_log_message_with_backslashes(self, capsys):
        """Test logging a message with backslashes."""
        log("Path: C:\\Users\\test\\file.txt")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] Path: C:\\Users\\test\\file.txt\n"

    def test_log_error_message(self, capsys):
        """Test logging an error message."""
        log("ERROR: Something went wrong")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] ERROR: Something went wrong\n"

    def test_log_info_message(self, capsys):
        """Test logging an info message."""
        log("INFO: Server started on port 8080")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] INFO: Server started on port 8080\n"

    def test_log_debug_message(self, capsys):
        """Test logging a debug message."""
        log("DEBUG: Processing request with ID 12345")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] DEBUG: Processing request with ID 12345\n"

    def test_log_warning_message(self, capsys):
        """Test logging a warning message."""
        log("WARNING: Deprecated function used")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] WARNING: Deprecated function used\n"

    def test_log_with_formatting_characters(self, capsys):
        """Test logging a message with formatting characters."""
        log("Value: %s, Number: %d, Float: %f")
        captured = capsys.readouterr()
        assert captured.out == "[RPC] Value: %s, Number: %d, Float: %f\n"

    def test_log_preserves_message_type(self):
        """Test that log function expects string input."""
        # The function signature expects str, so we test with string
        # This test ensures the function works as designed
        try:
            log("Valid string message")
            # If we get here, the function accepted the string as expected
            assert True
        except Exception:
            # If an exception occurs, the test should fail
            assert False, "log function should accept string messages"

    def test_log_whitespace_message(self, capsys):
        """Test logging a message with only whitespace."""
        log("   \t\n   ")
        captured = capsys.readouterr()
        assert captured.out == "[RPC]    \t\n   \n"