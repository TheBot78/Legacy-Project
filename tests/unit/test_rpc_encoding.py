import json
import pytest
from rpc.encoding import encode, decode


class TestEncoding:
    """Tests for RPC encoding module."""

    def test_encode_simple_dict(self):
        """Test encoding a simple dictionary."""
        data = {"key": "value", "number": 42}
        result = encode(data)
        assert isinstance(result, str)
        assert json.loads(result) == data

    def test_encode_list(self):
        """Test encoding a list."""
        data = [1, 2, 3, "test"]
        result = encode(data)
        assert isinstance(result, str)
        assert json.loads(result) == data

    def test_encode_string(self):
        """Test encoding a string."""
        data = "hello world"
        result = encode(data)
        assert isinstance(result, str)
        assert json.loads(result) == data

    def test_encode_number(self):
        """Test encoding a number."""
        data = 42
        result = encode(data)
        assert isinstance(result, str)
        assert json.loads(result) == data

    def test_encode_boolean(self):
        """Test encoding a boolean."""
        data = True
        result = encode(data)
        assert isinstance(result, str)
        assert json.loads(result) == data

    def test_encode_none(self):
        """Test encoding None."""
        data = None
        result = encode(data)
        assert isinstance(result, str)
        assert json.loads(result) == data

    def test_encode_nested_structure(self):
        """Test encoding a nested structure."""
        data = {
            "users": [
                {"id": 1, "name": "Alice", "active": True},
                {"id": 2, "name": "Bob", "active": False}
            ],
            "meta": {"total": 2, "page": 1}
        }
        result = encode(data)
        assert isinstance(result, str)
        assert json.loads(result) == data

    def test_decode_simple_dict(self):
        """Test decoding a simple dictionary."""
        json_str = '{"key": "value", "number": 42}'
        result = decode(json_str)
        expected = {"key": "value", "number": 42}
        assert result == expected

    def test_decode_list(self):
        """Test decoding a list."""
        json_str = '[1, 2, 3, "test"]'
        result = decode(json_str)
        expected = [1, 2, 3, "test"]
        assert result == expected

    def test_decode_string(self):
        """Test decoding a string."""
        json_str = '"hello world"'
        result = decode(json_str)
        expected = "hello world"
        assert result == expected

    def test_decode_number(self):
        """Test decoding a number."""
        json_str = '42'
        result = decode(json_str)
        expected = 42
        assert result == expected

    def test_decode_boolean(self):
        """Test decoding a boolean."""
        json_str = 'true'
        result = decode(json_str)
        expected = True
        assert result == expected

    def test_decode_null(self):
        """Test decoding null."""
        json_str = 'null'
        result = decode(json_str)
        expected = None
        assert result == expected

    def test_decode_nested_structure(self):
        """Test decoding a nested structure."""
        json_str = '{"users": [{"id": 1, "name": "Alice", "active": true}, {"id": 2, "name": "Bob", "active": false}], "meta": {"total": 2, "page": 1}}'
        result = decode(json_str)
        expected = {
            "users": [
                {"id": 1, "name": "Alice", "active": True},
                {"id": 2, "name": "Bob", "active": False}
            ],
            "meta": {"total": 2, "page": 1}
        }
        assert result == expected

    def test_encode_decode_roundtrip(self):
        """Test that encoding then decoding returns original data."""
        original_data = {
            "string": "test",
            "number": 123,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"key": "value"}
        }
        encoded = encode(original_data)
        decoded = decode(encoded)
        assert decoded == original_data

    def test_decode_invalid_json(self):
        """Test decoding invalid JSON raises exception."""
        invalid_json = '{"key": "value"'
        with pytest.raises(json.JSONDecodeError):
            decode(invalid_json)

    def test_decode_empty_string(self):
        """Test decoding empty string raises exception."""
        with pytest.raises(json.JSONDecodeError):
            decode("")

    def test_encode_unicode(self):
        """Test encoding unicode characters."""
        data = {"message": "Héllo wörld! 🌍"}
        result = encode(data)
        assert isinstance(result, str)
        assert decode(result) == data