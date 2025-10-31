import pytest
from rpc.service import register_service, call_service, services


class TestRPCService:
    """Tests for RPC service module."""

    def setup_method(self):
        """Clear services before each test."""
        services.clear()

    def test_register_service_basic(self):
        """Test basic service registration."""
        @register_service("test_service")
        def test_func():
            return "test_result"

        assert "test_service" in services
        assert services["test_service"] == test_func

    def test_register_service_with_params(self):
        """Test registering service with parameters."""
        @register_service("add_service")
        def add(x, y):
            return x + y

        assert "add_service" in services
        assert services["add_service"] == add

    def test_register_multiple_services(self):
        """Test registering multiple services."""
        @register_service("service1")
        def func1():
            return "result1"

        @register_service("service2")
        def func2():
            return "result2"

        assert "service1" in services
        assert "service2" in services
        assert len(services) == 2

    def test_register_service_overwrites_existing(self):
        """Test that registering a service with existing name overwrites it."""
        @register_service("test_service")
        def original_func():
            return "original"

        @register_service("test_service")
        def new_func():
            return "new"

        assert services["test_service"] == new_func
        assert len(services) == 1

    def test_register_service_returns_function(self):
        """Test that register_service decorator returns the original function."""
        def original_func():
            return "test"

        decorated_func = register_service("test_service")(original_func)
        assert decorated_func == original_func

    def test_call_service_no_params(self):
        """Test calling service without parameters."""
        @register_service("ping")
        def ping():
            return "pong"

        result = call_service("ping", {})
        assert result == "pong"

    def test_call_service_with_params(self):
        """Test calling service with parameters."""
        @register_service("add")
        def add(x, y):
            return x + y

        result = call_service("add", {"x": 5, "y": 3})
        assert result == 8

    def test_call_service_with_keyword_params(self):
        """Test calling service with keyword parameters."""
        @register_service("greet")
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = call_service("greet", {"name": "Alice", "greeting": "Hi"})
        assert result == "Hi, Alice!"

    def test_call_service_with_default_params(self):
        """Test calling service using default parameters."""
        @register_service("greet")
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = call_service("greet", {"name": "Bob"})
        assert result == "Hello, Bob!"

    def test_call_service_unknown_method(self):
        """Test calling unknown service raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            call_service("unknown_service", {})
        assert "Unknown method: unknown_service" in str(exc_info.value)

    def test_call_service_missing_required_param(self):
        """Test calling service with missing required parameter raises TypeError."""
        @register_service("multiply")
        def multiply(x, y):
            return x * y

        with pytest.raises(TypeError):
            call_service("multiply", {"x": 5})  # Missing 'y' parameter

    def test_call_service_extra_params(self):
        """Test calling service with extra parameters raises TypeError."""
        @register_service("simple")
        def simple():
            return "result"

        with pytest.raises(TypeError):
            call_service("simple", {"extra": "param"})

    def test_call_service_complex_return(self):
        """Test calling service that returns complex data."""
        @register_service("get_user")
        def get_user(user_id):
            return {
                "id": user_id,
                "name": "Alice",
                "email": "alice@example.com",
                "active": True
            }

        result = call_service("get_user", {"user_id": 123})
        expected = {
            "id": 123,
            "name": "Alice",
            "email": "alice@example.com",
            "active": True
        }
        assert result == expected

    def test_call_service_with_exception(self):
        """Test calling service that raises an exception."""
        @register_service("divide")
        def divide(x, y):
            if y == 0:
                raise ValueError("Division by zero")
            return x / y

        # Normal case
        result = call_service("divide", {"x": 10, "y": 2})
        assert result == 5.0

        # Exception case
        with pytest.raises(ValueError) as exc_info:
            call_service("divide", {"x": 10, "y": 0})
        assert "Division by zero" in str(exc_info.value)

    def test_services_global_state(self):
        """Test that services dictionary maintains global state."""
        # Initially empty (after setup_method)
        assert len(services) == 0

        @register_service("test1")
        def func1():
            return "result1"

        assert len(services) == 1

        @register_service("test2")
        def func2():
            return "result2"

        assert len(services) == 2
        assert "test1" in services
        assert "test2" in services

    def test_call_service_with_none_params(self):
        """Test calling service with None as parameter value."""
        @register_service("process")
        def process(data):
            return f"Processing: {data}"

        result = call_service("process", {"data": None})
        assert result == "Processing: None"

    def test_call_service_with_list_params(self):
        """Test calling service with list parameters."""
        @register_service("sum_list")
        def sum_list(numbers):
            return sum(numbers)

        result = call_service("sum_list", {"numbers": [1, 2, 3, 4, 5]})
        assert result == 15

    def test_call_service_with_dict_params(self):
        """Test calling service with dictionary parameters."""
        @register_service("process_user")
        def process_user(user_data):
            return f"User {user_data['name']} has email {user_data['email']}"

        user_data = {"name": "Alice", "email": "alice@example.com"}
        result = call_service("process_user", {"user_data": user_data})
        assert result == "User Alice has email alice@example.com"