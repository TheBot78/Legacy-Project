import pytest
import requests
import json
from fastapi.testclient import TestClient
from backend.api import app


class TestBackendAPILocal:
    """Test the backend API using local TestClient."""
    
    def test_root_endpoint(self, test_client):
        """Test the root endpoint."""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_list_dbs_empty(self, test_client, temp_bases_dir):
        """Test listing databases when none exist."""
        response = test_client.get("/dbs")
        assert response.status_code == 200
        data = response.json()
        assert "databases" in data
        assert data["databases"] == []
    
    def test_import_database_basic(self, test_client, temp_bases_dir, sample_import_request):
        """Test importing a basic database."""
        response = test_client.post("/import", json=sample_import_request)
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "db_name" in data
        assert data["db_name"] == sample_import_request["db_name"]
    
    def test_import_database_creates_files(self, test_client, temp_bases_dir, sample_import_request):
        """Test that importing creates the expected files."""
        response = test_client.post("/import", json=sample_import_request)
        assert response.status_code == 200
        
        # Check that database directory was created
        db_path = temp_bases_dir / f"{sample_import_request['db_name']}.gwb"
        assert db_path.exists()
        assert db_path.is_dir()
        
        # Check that required files exist
        assert (db_path / "base.json").exists()
        assert (db_path / "strings.inx.json").exists()
        assert (db_path / "names.inx.json").exists()
        assert (db_path / "base.acc.json").exists()
    
    def test_list_dbs_after_import(self, test_client, temp_bases_dir, sample_import_request):
        """Test listing databases after importing one."""
        # Import a database
        test_client.post("/import", json=sample_import_request)
        
        # List databases
        response = test_client.get("/dbs")
        assert response.status_code == 200
        data = response.json()
        assert len(data["databases"]) == 1
        assert data["databases"][0]["name"] == sample_import_request["db_name"]
    
    def test_stats_existing_db(self, test_client, temp_bases_dir, sample_import_request):
        """Test getting stats for an existing database."""
        # Import a database
        test_client.post("/import", json=sample_import_request)
        
        # Get stats
        response = test_client.get(f"/db/{sample_import_request['db_name']}/stats")
        assert response.status_code == 200
        data = response.json()
        assert "persons_count" in data
        assert "families_count" in data
        assert data["persons_count"] == len(sample_import_request["persons"])
        assert data["families_count"] == len(sample_import_request["families"])
    
    def test_stats_nonexistent_db(self, test_client):
        """Test getting stats for a non-existent database."""
        response = test_client.get("/db/nonexistent/stats")
        assert response.status_code == 404
        assert response.json() == {"detail": "Base not found"}
    
    def test_delete_db(self, test_client, temp_bases_dir, sample_import_request):
        """Test deleting a database."""
        # Import a database
        test_client.post("/import", json=sample_import_request)
        
        # Verify it exists
        response = test_client.get("/dbs")
        assert len(response.json()["databases"]) == 1
        
        # Delete it
        response = test_client.delete(f"/db/{sample_import_request['db_name']}")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        # Verify it's gone
        response = test_client.get("/dbs")
        assert len(response.json()["databases"]) == 0
    
    def test_delete_nonexistent_db(self, test_client):
        """Test deleting a non-existent database."""
        response = test_client.delete("/db/nonexistent")
        assert response.status_code == 404
        assert response.json() == {"detail": "Base not found"}
    
    def test_rename_db(self, test_client, temp_bases_dir, sample_import_request):
        """Test renaming a database."""
        # Import a database
        test_client.post("/import", json=sample_import_request)
        
        # Rename it
        new_name = "renamed_db"
        response = test_client.post(
            f"/db/{sample_import_request['db_name']}/rename",
            json={"new_name": new_name}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        # Verify old name is gone and new name exists
        response = test_client.get("/dbs")
        db_names = [db["name"] for db in response.json()["databases"]]
        assert sample_import_request["db_name"] not in db_names
        assert new_name in db_names
    
    def test_parse_gw(self, test_client, sample_gw_text):
        """Test parsing GW text."""
        response = test_client.post("/parse_gw", json={"gw_text": sample_gw_text})
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "persons" in data
        assert "families" in data
        assert len(data["persons"]) > 0
        assert len(data["families"]) > 0
    
    def test_import_gw(self, test_client, temp_bases_dir, sample_gw_text):
        """Test importing from GW text."""
        request_data = {
            "db_name": "gw_test_db",
            "gw_text": sample_gw_text,
            "notes_origin_file": "test.gw"
        }
        
        response = test_client.post("/import_gw", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["db_name"] == "gw_test_db"
        
        # Verify database was created
        db_path = temp_bases_dir / "gw_test_db.gwb"
        assert db_path.exists()
    
    def test_import_ged(self, test_client, temp_bases_dir, sample_ged_text):
        """Test importing from GEDCOM text."""
        request_data = {
            "db_name": "ged_test_db",
            "ged_text": sample_ged_text,
            "notes_origin_file": "test.ged"
        }
        
        response = test_client.post("/import_ged", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["db_name"] == "ged_test_db"
        
        # Verify database was created
        db_path = temp_bases_dir / "ged_test_db.gwb"
        assert db_path.exists()
    
    def test_search_db_by_surname(self, test_client, temp_bases_dir, sample_import_request):
        """Test searching database by surname."""
        # Import a database
        test_client.post("/import", json=sample_import_request)
        
        # Search by surname
        response = test_client.get(
            f"/db/{sample_import_request['db_name']}/search",
            params={"n": "Doe"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "results" in data
        assert len(data["results"]) > 0
    
    def test_search_db_by_first_name(self, test_client, temp_bases_dir, sample_import_request):
        """Test searching database by first name."""
        # Import a database
        test_client.post("/import", json=sample_import_request)
        
        # Search by first name
        response = test_client.get(
            f"/db/{sample_import_request['db_name']}/search",
            params={"p": "John"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "results" in data
    
    def test_search_db_by_both_names(self, test_client, temp_bases_dir, sample_import_request):
        """Test searching database by both names."""
        # Import a database
        test_client.post("/import", json=sample_import_request)
        
        # Search by both names
        response = test_client.get(
            f"/db/{sample_import_request['db_name']}/search",
            params={"n": "Doe", "p": "John"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "results" in data
    
    def test_get_person_details(self, test_client, temp_bases_dir, sample_import_request):
        """Test getting person details."""
        # Import a database
        test_client.post("/import", json=sample_import_request)
        
        # Get person details
        response = test_client.get(
            f"/db/{sample_import_request['db_name']}/person",
            params={"n": "Doe", "p": "John"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "person" in data
    
    def test_search_nonexistent_db(self, test_client):
        """Test searching a non-existent database."""
        response = test_client.get("/db/nonexistent/search", params={"n": "Doe"})
        assert response.status_code == 404
        assert response.json() == {"detail": "Base not found"}
    
    def test_import_invalid_data(self, test_client):
        """Test importing with invalid data."""
        invalid_request = {
            "db_name": "invalid_db",
            "persons": [
                {
                    # Missing required fields
                    "id": 1
                }
            ],
            "families": []
        }
        
        response = test_client.post("/import", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    def test_import_duplicate_db_name(self, test_client, temp_bases_dir, sample_import_request):
        """Test importing with duplicate database name."""
        # Import first database
        response1 = test_client.post("/import", json=sample_import_request)
        assert response1.status_code == 200
        
        # Try to import with same name
        response2 = test_client.post("/import", json=sample_import_request)
        # Should either succeed (overwrite) or return an error
        # The exact behavior depends on implementation
        assert response2.status_code in [200, 400, 409]


@pytest.mark.docker
class TestBackendAPIDocker:
    """Test the backend API running in Docker."""
    
    def test_docker_root_endpoint(self, docker_test_client):
        """Test the root endpoint via Docker."""
        response = docker_test_client.get("http://localhost:8000/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_docker_list_dbs(self, docker_test_client):
        """Test listing databases via Docker."""
        response = docker_test_client.get("http://localhost:8000/dbs")
        assert response.status_code == 200
        data = response.json()
        assert "databases" in data
    
    def test_docker_import_and_search(self, docker_test_client, sample_import_request, cleanup_test_dbs):
        """Test importing and searching via Docker."""
        # Register for cleanup
        cleanup_test_dbs(sample_import_request["db_name"])
        
        # Import database
        response = docker_test_client.post(
            "http://localhost:8000/import",
            json=sample_import_request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        # Search the database
        response = docker_test_client.get(
            f"http://localhost:8000/db/{sample_import_request['db_name']}/search",
            params={"n": "Doe"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "results" in data
    
    def test_docker_stats(self, docker_test_client, sample_import_request, cleanup_test_dbs):
        """Test getting stats via Docker."""
        # Register for cleanup
        cleanup_test_dbs(sample_import_request["db_name"])
        
        # Import database
        docker_test_client.post(
            "http://localhost:8000/import",
            json=sample_import_request
        )
        
        # Get stats
        response = docker_test_client.get(
            f"http://localhost:8000/db/{sample_import_request['db_name']}/stats"
        )
        assert response.status_code == 200
        data = response.json()
        assert "persons_count" in data
        assert "families_count" in data
    
    def test_docker_parse_gw(self, docker_test_client, sample_gw_text):
        """Test parsing GW text via Docker."""
        response = docker_test_client.post(
            "http://localhost:8000/parse_gw",
            json={"gw_text": sample_gw_text}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "persons" in data
        assert "families" in data
    
    def test_docker_import_gw(self, docker_test_client, sample_gw_text, cleanup_test_dbs):
        """Test importing GW via Docker."""
        db_name = "docker_gw_test"
        cleanup_test_dbs(db_name)
        
        request_data = {
            "db_name": db_name,
            "gw_text": sample_gw_text,
            "notes_origin_file": "test.gw"
        }
        
        response = docker_test_client.post(
            "http://localhost:8000/import_gw",
            json=request_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["db_name"] == db_name
    
    def test_docker_import_ged(self, docker_test_client, sample_ged_text, cleanup_test_dbs):
        """Test importing GEDCOM via Docker."""
        db_name = "docker_ged_test"
        cleanup_test_dbs(db_name)
        
        request_data = {
            "db_name": db_name,
            "ged_text": sample_ged_text,
            "notes_origin_file": "test.ged"
        }
        
        response = docker_test_client.post(
            "http://localhost:8000/import_ged",
            json=request_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["db_name"] == db_name
    
    def test_docker_database_persistence(self, docker_test_client, sample_import_request, cleanup_test_dbs):
        """Test that databases persist in Docker."""
        # Register for cleanup
        cleanup_test_dbs(sample_import_request["db_name"])
        
        # Import database
        docker_test_client.post(
            "http://localhost:8000/import",
            json=sample_import_request
        )
        
        # Verify it appears in database list
        response = docker_test_client.get("http://localhost:8000/dbs")
        assert response.status_code == 200
        data = response.json()
        
        db_names = [db["name"] for db in data["databases"]]
        assert sample_import_request["db_name"] in db_names
        
        # Verify we can still access it
        response = docker_test_client.get(
            f"http://localhost:8000/db/{sample_import_request['db_name']}/stats"
        )
        assert response.status_code == 200
