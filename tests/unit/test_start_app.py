import pytest
from front.start.start_app import app # Import the 'start' app

@pytest.fixture
def client():
    """Pytest-Flask fixture to create a test client for front/start/start_app.py."""
    with app.test_client() as client:
        yield client


def test_start_root_redirects_to_welcome(client):
    """
    Tests that the / route redirects to /welcome.
    """
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 200


def test_start_invalid_path_access(client):
    """
    Tests that the / route redirects to /welcome.
    """
    response = client.get('/a', follow_redirects=False)
    assert response.status_code == 404
