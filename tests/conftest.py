import pytest
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from backend.api import app, BASES_DIR
import os
import json
from typing import Dict, List


@pytest.fixture(scope="module")
def test_client():
    """
    Pytest fixture to create a TestClient for your FastAPI app.
    """
    client = TestClient(app)
    yield client


@pytest.fixture(scope="function")
def temp_bases_dir():
    """
    Create a temporary directory for test databases.
    This isolates tests from the real data directory.
    """
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    # Backup original BASES_DIR
    original_bases_dir = BASES_DIR
    
    # Monkey patch the BASES_DIR in the api module
    import backend.api
    backend.api.BASES_DIR = temp_path
    
    yield temp_path
    
    # Cleanup: restore original and remove temp directory
    backend.api.BASES_DIR = original_bases_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_persons_data():
    """
    Sample persons data for testing.
    """
    return [
        {
            "id": 1,
            "first_names": ["John"],
            "surname": "Doe",
            "sex": "m",
            "birth_date": "1980",
            "birth_place": "New York"
        },
        {
            "id": 2,
            "first_names": ["Jane"],
            "surname": "Doe",
            "sex": "f",
            "birth_date": "1985",
            "birth_place": "Boston"
        },
        {
            "id": 3,
            "first_names": ["Bob"],
            "surname": "Smith",
            "sex": "m",
            "father_id": 1,
            "mother_id": 2,
            "birth_date": "2010"
        }
    ]


@pytest.fixture
def sample_families_data():
    """
    Sample families data for testing.
    """
    return [
        {
            "id": 1,
            "husband_id": 1,
            "wife_id": 2,
            "children_ids": [3],
            "marriage_date": "2005",
            "marriage_place": "Chicago"
        }
    ]


@pytest.fixture
def sample_import_request(sample_persons_data, sample_families_data):
    """
    Complete import request for testing.
    """
    return {
        "db_name": "test_db",
        "persons": sample_persons_data,
        "families": sample_families_data,
        "notes_origin_file": "test_import.ged"
    }


@pytest.fixture
def sample_gw_text():
    """
    Sample GW format text for testing parsers.
    """
    return """encoding: utf-8
fam 1 husb 1 wife 2 chil 3 marr 2005 in Chicago
per 1 John /Doe/ m 1980 in New York
per 2 Jane /Doe/ f 1985 in Boston
per 3 Bob /Smith/ m 2010 fath 1 moth 2"""


@pytest.fixture
def sample_ged_text():
    """
    Sample GEDCOM format text for testing parsers.
    """
    return """0 HEAD
1 SOUR Legacy-Project
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 BIRT
2 DATE 1980
2 PLAC New York
0 @I2@ INDI
1 NAME Jane /Doe/
1 SEX F
1 BIRT
2 DATE 1985
2 PLAC Boston
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 MARR
2 DATE 2005
2 PLAC Chicago
0 TRLR"""


@pytest.fixture
def docker_test_client():
    """
    Test client that can work with Docker backend.
    This fixture assumes the backend is running in Docker.
    """
    import requests
    
    # Check if Docker backend is available
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            # Return a requests session configured for Docker
            session = requests.Session()
            session.base_url = "http://localhost:8000"
            yield session
        else:
            pytest.skip("Docker backend not available")
    except requests.exceptions.RequestException:
        pytest.skip("Docker backend not available")


@pytest.fixture
def cleanup_test_dbs():
    """
    Cleanup fixture to remove test databases after tests.
    """
    test_dbs = []
    
    def register_db(db_name: str):
        test_dbs.append(db_name)
    
    yield register_db
    
    # Cleanup
    client = TestClient(app)
    for db_name in test_dbs:
        try:
            client.delete(f"/db/{db_name}")
        except:
            pass  # Ignore cleanup errors
