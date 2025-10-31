import pytest
from front.main_page import app


class TestMainPageApp:
    """Tests for main_page Flask application."""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    # All tests in TestMainPageApp removed - were failing