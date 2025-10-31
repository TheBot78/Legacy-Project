import pytest
from front.geneweb.app import app # Import the 'geneweb' app

@pytest.fixture
def client():
    """Pytest-Flask fixture for front/geneweb/app.py."""
    with app.test_client() as client:
        yield client


def test_geneweb_root_renders_hello(client):
    """
    Tests that the root / returns 'Choose a genealogy!'
    """
    response = client.get('/choose_genealogy')
    assert response.status_code == 200
    assert b"Choose a genealogy" in response.data
