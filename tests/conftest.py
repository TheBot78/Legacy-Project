import pytest
from fastapi.testclient import TestClient
from backend.api import app


@pytest.fixture(scope="module")
def test_client():
    """
    Pytest fixture to create a TestClient for your FastAPI app.
    """
    client = TestClient(app)
    yield client
