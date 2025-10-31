import pytest
from front.gwsetup.app import app # Import the 'gwsetup' app

@pytest.fixture
def client():
    """Pytest-Flask fixture for front/gwsetup/app.py."""
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_api_calls(mocker):
    """Mocks backend API calls."""
    mocker.patch('requests.get', return_value=mocker.Mock(json=lambda: ["db1", "db2"]))
    mocker.patch('requests.post', return_value=mocker.Mock(json=lambda: {"ok": True, "counts": {"persons": 10}}))
    mocker.patch('requests.delete', return_value=mocker.Mock(json=lambda: {"ok": True}))


def test_gwsetup_root_renders_bases(client):
    """
    Tests that the root / renders the list of bases.
    """
    response = client.get('/welcome')
    assert response.status_code == 200


def test_gwsetup_ged2gwb_get_renders_form(client):
    """
    Tests that GET /ged2gwb renders the upload form.
    """
    response = client.get('/ged2gwb')
    assert response.status_code == 200
    assert b"Import a GEDCOM file" in response.data


def test_gwsetup_delete_get_renders_form(client):
    """
    Tests that GET /delete renders the delete form.
    """
    response = client.get('/delete')
    assert response.status_code == 200


def test_gwsetup_gwc_get_renders_form(client):
    response = client.get('/gwc')
    assert response.status_code == 200
