import pytest
from fastapi.testclient import TestClient
from rpc.server.main import app
from rpc.service import services, register_service


class TestRPCAPI:
    """Integration tests for RPC API."""

    def setup_method(self):
        """Clear services and set up test services before each test."""
        services.clear()
        
        # Register test services
        @register_service("ping")
        def ping():
            return "pong"

        @register_service("add")
        def add(x: int, y: int):
            return x + y

        @register_service("greet")
        def greet(name: str, greeting: str = "Hello"):
            return f"{greeting}, {name}!"

        @register_service("get_user")
        def get_user(user_id: int):
            return {
                "id": user_id,
                "name": f"User{user_id}",
                "email": f"user{user_id}@example.com"
            }

        @register_service("divide")
        def divide(x: float, y: float):
            if y == 0:
                raise ValueError("Division by zero")
            return x / y

    def test_rpc_endpoint_ping(self):
        """Test RPC endpoint with ping service."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "method": "ping",
            "params": {},
            "id": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "pong"
        assert data["id"] == 1

    def test_rpc_endpoint_add(self):
        """Test RPC endpoint with add service."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "method": "add",
            "params": {"x": 5, "y": 3},
            "id": 2
        })
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 8
        assert data["id"] == 2

    def test_rpc_endpoint_greet_with_default(self):
        """Test RPC endpoint with greet service using default parameter."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "method": "greet",
            "params": {"name": "Alice"},
            "id": 3
        })
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "Hello, Alice!"
        assert data["id"] == 3

    def test_rpc_endpoint_greet_with_custom_greeting(self):
        """Test RPC endpoint with greet service using custom greeting."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "method": "greet",
            "params": {"name": "Bob", "greeting": "Hi"},
            "id": 4
        })
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "Hi, Bob!"
        assert data["id"] == 4

    def test_rpc_endpoint_get_user(self):
        """Test RPC endpoint with get_user service returning complex data."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "method": "get_user",
            "params": {"user_id": 123},
            "id": 5
        })
        assert response.status_code == 200
        data = response.json()
        expected_result = {
            "id": 123,
            "name": "User123",
            "email": "user123@example.com"
        }
        assert data["result"] == expected_result
        assert data["id"] == 5

    def test_rpc_endpoint_without_id(self):
        """Test RPC endpoint without id parameter."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "method": "ping",
            "params": {}
        })
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "pong"
        assert data["id"] is None

    def test_rpc_endpoint_unknown_method(self):
        """Test RPC endpoint with unknown method."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "method": "unknown_method",
            "params": {},
            "id": 6
        })
        assert response.status_code == 200
        data = response.json()
        assert "Error: Unknown method: unknown_method" in data["result"]
        assert data["id"] == 6

    def test_rpc_endpoint_missing_params(self):
        """Test RPC endpoint with missing required parameters."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "method": "add",
            "params": {"x": 5},  # Missing 'y' parameter
            "id": 7
        })
        assert response.status_code == 200
        data = response.json()
        assert "Error:" in data["result"]
        assert data["id"] == 7

    def test_rpc_endpoint_service_exception(self):
        """Test RPC endpoint when service raises an exception."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "method": "divide",
            "params": {"x": 10, "y": 0},
            "id": 8
        })
        assert response.status_code == 200
        data = response.json()
        assert "Error: Division by zero" in data["result"]
        assert data["id"] == 8

    def test_rpc_endpoint_invalid_json(self):
        """Test RPC endpoint with invalid JSON."""
        client = TestClient(app)
        response = client.post("/rpc", 
            data="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Unprocessable Entity

    def test_rpc_endpoint_missing_method(self):
        """Test RPC endpoint with missing method field."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "params": {},
            "id": 9
        })
        assert response.status_code == 422  # Validation error

    def test_rpc_endpoint_missing_params(self):
        """Test RPC endpoint with missing params field."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "method": "ping",
            "id": 10
        })
        assert response.status_code == 422  # Validation error

    def test_rpc_endpoint_invalid_method_type(self):
        """Test RPC endpoint with invalid method type."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "method": 123,  # Should be string
            "params": {},
            "id": 11
        })
        assert response.status_code == 422  # Validation error

    def test_rpc_endpoint_invalid_params_type(self):
        """Test RPC endpoint with invalid params type."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "method": "ping",
            "params": "invalid",  # Should be dict
            "id": 12
        })
        assert response.status_code == 422  # Validation error

    def test_rpc_endpoint_invalid_id_type(self):
        """Test RPC endpoint with invalid id type."""
        client = TestClient(app)
        response = client.post("/rpc", json={
            "method": "ping",
            "params": {},
            "id": "invalid"  # Should be int or None
        })
        assert response.status_code == 422  # Validation error

    def test_custom_404_handler(self):
        """Test custom 404 handler."""
        client = TestClient(app)
        response = client.get("/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "Not Found"
        assert data["detail"] == "Endpoint not found"
        assert data["path"] == "/nonexistent"

    def test_rpc_endpoint_get_method_not_allowed(self):
        """Test that GET method is not allowed on RPC endpoint."""
        client = TestClient(app)
        response = client.get("/rpc")
        assert response.status_code == 405  # Method Not Allowed

    def test_rpc_endpoint_multiple_requests(self):
        """Test multiple RPC requests in sequence."""
        client = TestClient(app)
        
        # First request
        response1 = client.post("/rpc", json={
            "method": "add",
            "params": {"x": 1, "y": 2},
            "id": 1
        })
        assert response1.status_code == 200
        assert response1.json()["result"] == 3
        
        # Second request
        response2 = client.post("/rpc", json={
            "method": "greet",
            "params": {"name": "Test"},
            "id": 2
        })
        assert response2.status_code == 200
        assert response2.json()["result"] == "Hello, Test!"
        
        # Third request
        response3 = client.post("/rpc", json={
            "method": "ping",
            "params": {},
            "id": 3
        })
        assert response3.status_code == 200
        assert response3.json()["result"] == "pong"

    def test_rpc_endpoint_large_params(self):
        """Test RPC endpoint with large parameter values."""
        client = TestClient(app)
        large_number = 999999999
        response = client.post("/rpc", json={
            "method": "add",
            "params": {"x": large_number, "y": 1},
            "id": 13
        })
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == large_number + 1
        assert data["id"] == 13