import pytest
from pydantic import ValidationError
from rpc.json_rpc import RPCRequest, RPCResponse


class TestRPCRequest:
    """Tests for RPCRequest model."""

    def test_create_request_with_required_fields(self):
        """Test creating request with only required fields."""
        request = RPCRequest(method="test_method", params={"key": "value"})
        assert request.method == "test_method"
        assert request.params == {"key": "value"}
        assert request.id is None

    def test_create_request_with_all_fields(self):
        """Test creating request with all fields."""
        request = RPCRequest(
            method="test_method",
            params={"key": "value", "number": 42},
            id=123
        )
        assert request.method == "test_method"
        assert request.params == {"key": "value", "number": 42}
        assert request.id == 123

    def test_create_request_with_empty_params(self):
        """Test creating request with empty params."""
        request = RPCRequest(method="test_method", params={})
        assert request.method == "test_method"
        assert request.params == {}
        assert request.id is None

    def test_create_request_with_complex_params(self):
        """Test creating request with complex params."""
        params = {
            "string": "test",
            "number": 42,
            "boolean": True,
            "list": [1, 2, 3],
            "nested": {"key": "value"}
        }
        request = RPCRequest(method="complex_method", params=params)
        assert request.method == "complex_method"
        assert request.params == params

    def test_create_request_missing_method(self):
        """Test creating request without method raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            RPCRequest(params={"key": "value"})
        assert "method" in str(exc_info.value)

    def test_create_request_missing_params(self):
        """Test creating request without params raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            RPCRequest(method="test_method")
        assert "params" in str(exc_info.value)

    def test_create_request_invalid_method_type(self):
        """Test creating request with invalid method type."""
        with pytest.raises(ValidationError):
            RPCRequest(method=123, params={"key": "value"})

    def test_create_request_invalid_params_type(self):
        """Test creating request with invalid params type."""
        with pytest.raises(ValidationError):
            RPCRequest(method="test_method", params="invalid")

    def test_create_request_invalid_id_type(self):
        """Test creating request with invalid id type."""
        with pytest.raises(ValidationError):
            RPCRequest(method="test_method", params={}, id="invalid")

    def test_request_serialization(self):
        """Test request can be serialized to dict."""
        request = RPCRequest(
            method="test_method",
            params={"key": "value"},
            id=123
        )
        data = request.model_dump()
        expected = {
            "method": "test_method",
            "params": {"key": "value"},
            "id": 123
        }
        assert data == expected

    def test_request_from_dict(self):
        """Test creating request from dictionary."""
        data = {
            "method": "test_method",
            "params": {"key": "value"},
            "id": 123
        }
        request = RPCRequest(**data)
        assert request.method == "test_method"
        assert request.params == {"key": "value"}
        assert request.id == 123


class TestRPCResponse:
    """Tests for RPCResponse model."""

    def test_create_response_with_required_fields(self):
        """Test creating response with only required fields."""
        response = RPCResponse(result="success")
        assert response.result == "success"
        assert response.id is None

    def test_create_response_with_all_fields(self):
        """Test creating response with all fields."""
        response = RPCResponse(result={"status": "ok", "data": [1, 2, 3]}, id=123)
        assert response.result == {"status": "ok", "data": [1, 2, 3]}
        assert response.id == 123

    def test_create_response_with_string_result(self):
        """Test creating response with string result."""
        response = RPCResponse(result="Hello World")
        assert response.result == "Hello World"

    def test_create_response_with_number_result(self):
        """Test creating response with number result."""
        response = RPCResponse(result=42)
        assert response.result == 42

    def test_create_response_with_boolean_result(self):
        """Test creating response with boolean result."""
        response = RPCResponse(result=True)
        assert response.result is True

    def test_create_response_with_none_result(self):
        """Test creating response with None result."""
        response = RPCResponse(result=None)
        assert response.result is None

    def test_create_response_with_list_result(self):
        """Test creating response with list result."""
        result = [1, 2, 3, "test"]
        response = RPCResponse(result=result)
        assert response.result == result

    def test_create_response_with_dict_result(self):
        """Test creating response with dict result."""
        result = {"users": [{"id": 1, "name": "Alice"}], "total": 1}
        response = RPCResponse(result=result)
        assert response.result == result

    def test_create_response_missing_result(self):
        """Test creating response without result raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            RPCResponse()
        assert "result" in str(exc_info.value)

    def test_create_response_invalid_id_type(self):
        """Test creating response with invalid id type."""
        with pytest.raises(ValidationError):
            RPCResponse(result="success", id="invalid")

    def test_response_serialization(self):
        """Test response can be serialized to dict."""
        response = RPCResponse(
            result={"status": "ok", "count": 5},
            id=456
        )
        data = response.model_dump()
        expected = {
            "result": {"status": "ok", "count": 5},
            "id": 456
        }
        assert data == expected

    def test_response_from_dict(self):
        """Test creating response from dictionary."""
        data = {
            "result": {"message": "Operation completed"},
            "id": 789
        }
        response = RPCResponse(**data)
        assert response.result == {"message": "Operation completed"}
        assert response.id == 789

    def test_response_with_error_result(self):
        """Test creating response with error as result."""
        error_result = {"error": "Something went wrong", "code": 500}
        response = RPCResponse(result=error_result)
        assert response.result == error_result