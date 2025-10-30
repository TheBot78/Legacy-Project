from fastapi.testclient import TestClient


def test_integration_stats_missing_db_returns_404(test_client: TestClient):
    """
    Tests the /stats endpoint for a database that does not exist.
    Follows convention: test_integration_<workflow>_<scenario>
    """
    # Arrange
    db_name = "non_existent_db"

    # Act
    response = test_client.get(f"/db/{db_name}/stats")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Base not found"}


# Note: To test a 200 OK, you would first need to import a database.
# This test example only checks the 404 error path for simplicity.
