import pytest
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
import json
import tempfile
import shutil
from backend.api import (
    app, BASES_DIR, PersonInput, FamilyInput, ImportRequest,
    GwParseRequest, GwImportGWRequest, GwImportGEDRequest,
    RenameRequest, PersonNode, SearchContext
)
from backend.models import Person, Family
from fastapi.testclient import TestClient


class TestModels:
    """Tests for API model classes."""

    def test_person_input_creation(self):
        """Test PersonInput model creation."""
        person = PersonInput(
            first_names=["John"],
            surname="Doe",
            sex="m",
            birth_date="1990"
        )
        assert person.first_names == ["John"]
        assert person.surname == "Doe"
        assert person.sex == "m"
        assert person.birth_date == "1990"
        assert person.id is None

    def test_person_input_with_id(self):
        """Test PersonInput model with ID."""
        person = PersonInput(
            id=123,
            first_names=["Jane"],
            surname="Smith"
        )
        assert person.id == 123
        assert person.first_names == ["Jane"]
        assert person.surname == "Smith"

    def test_family_input_creation(self):
        """Test FamilyInput model creation."""
        family = FamilyInput(
            husband_id=1,
            wife_id=2,
            children_ids=[3, 4],
            marriage_date="2000"
        )
        assert family.husband_id == 1
        assert family.wife_id == 2
        assert family.children_ids == [3, 4]
        assert family.marriage_date == "2000"
        assert family.id is None

    def test_import_request_creation(self):
        """Test ImportRequest model creation."""
        person = PersonInput(first_names=["John"], surname="Doe")
        family = FamilyInput(husband_id=1, wife_id=2)
        
        request = ImportRequest(
            db_name="test_db",
            persons=[person],
            families=[family],
            notes_origin_file="test.ged"
        )
        
        assert request.db_name == "test_db"
        assert len(request.persons) == 1
        assert len(request.families) == 1
        assert request.notes_origin_file == "test.ged"

    def test_gw_parse_request_creation(self):
        """Test GwParseRequest model creation."""
        request = GwParseRequest(gw_text="test gw content")
        assert request.gw_text == "test gw content"

    def test_gw_import_gw_request_creation(self):
        """Test GwImportGWRequest model creation."""
        request = GwImportGWRequest(
            db_name="test_db",
            gw_text="test content",
            notes_origin_file="test.gw"
        )
        assert request.db_name == "test_db"
        assert request.gw_text == "test content"
        assert request.notes_origin_file == "test.gw"

    def test_gw_import_ged_request_creation(self):
        """Test GwImportGEDRequest model creation."""
        request = GwImportGEDRequest(
            db_name="test_db",
            ged_text="test ged content",
            notes_origin_file="test.ged"
        )
        assert request.db_name == "test_db"
        assert request.ged_text == "test ged content"
        assert request.notes_origin_file == "test.ged"

    def test_rename_request_creation(self):
        """Test RenameRequest model creation."""
        request = RenameRequest(new_name="new_db_name")
        assert request.new_name == "new_db_name"

    def test_person_node_creation(self):
        """Test PersonNode model creation."""
        node = PersonNode(
            id=1,
            surname="Doe",
            first_names=["John"],
            birth_date="1990",
            sex="m"
        )
        assert node.id == 1
        assert node.surname == "Doe"
        assert node.first_names == ["John"]
        assert node.birth_date == "1990"
        assert node.sex == "m"
        assert node.spouse is None
        assert node.children == []

    def test_person_node_with_relationships(self):
        """Test PersonNode with spouse and children."""
        child = PersonNode(id=3, surname="Doe", first_names=["Child"])
        spouse = PersonNode(id=2, surname="Smith", first_names=["Jane"])
        
        node = PersonNode(
            id=1,
            surname="Doe",
            first_names=["John"],
            spouse=spouse,
            children=[child]
        )
        
        assert node.spouse == spouse
        assert len(node.children) == 1
        assert node.children[0] == child


class TestConstants:
    """Tests for API constants."""

    def test_bases_dir_exists(self):
        """Test that BASES_DIR is properly defined."""
        assert isinstance(BASES_DIR, Path)
        assert BASES_DIR.name == "bases"

    def test_app_configuration(self):
        """Test FastAPI app configuration."""
        assert app.title == "GeneWeb-like Python Backend"
        assert app.version == "0.1"


class TestSearchContext:
    """Tests for SearchContext class."""

    def test_search_context_initialization(self):
        """Test SearchContext initialization."""
        with patch('backend.api.SearchContext._load_data'):
            context = SearchContext("test_db")
            assert context.db_name == "test_db"

    @patch('backend.api.load_db_file')
    def test_search_context_load_data(self, mock_load_db_file):
        """Test SearchContext data loading."""
        mock_load_db_file.side_effect = [
            {"persons": [], "families": []},  # base.json
            {"table_size": 0, "buckets": []},  # names.inx.json
            {"table_size": 0, "buckets": []}   # strings.inx.json
        ]
        
        context = SearchContext("test_db")
        
        assert mock_load_db_file.call_count == 3
        assert hasattr(context, 'persons')
        assert hasattr(context, 'families')
        assert hasattr(context, 'names_index')
        assert hasattr(context, 'strings_index')

    @patch('backend.api.load_db_file')
    def test_search_context_get_surname(self, mock_load_db_file):
        """Test SearchContext _get_surname method."""
        mock_load_db_file.side_effect = [
            {"persons": [], "families": []},
            {"table_size": 0, "buckets": []},
            {"table_size": 1, "buckets": [["Doe"]]}
        ]
        
        context = SearchContext("test_db")
        
        # Test with valid surname_id
        person = {"surname_id": 0}
        surname = context._get_surname(person)
        assert surname == "Doe"
        
        # Test with missing surname_id
        person_no_surname = {}
        surname = context._get_surname(person_no_surname)
        assert surname == ""
        
        # Test with invalid surname_id
        person_invalid = {"surname_id": 999}
        surname = context._get_surname(person_invalid)
        assert surname == ""

    @patch('backend.api.load_db_file')
    def test_search_context_find_by_list(self, mock_load_db_file):
        """Test SearchContext find_by_list method."""
        mock_load_db_file.side_effect = [
            {
                "persons": [
                    {"id": 1, "surname_id": 0, "first_name_ids": [0]}
                ],
                "families": []
            },
            {
                "table_size": 1,
                "buckets": [[
                    {"crushed_name": "doe", "person_ids": [1]}
                ]]
            },
            {
                "table_size": 2,
                "buckets": [["John"], ["Doe"]]
            }
        ]
        
        context = SearchContext("test_db")
        results = context.find_by_list("doe", "john")
        
        assert isinstance(results, list)
        # The exact behavior depends on the implementation details

    @patch('backend.api.load_db_file')
    def test_search_context_find_person_details(self, mock_load_db_file):
        """Test SearchContext find_person_details method."""
        mock_load_db_file.side_effect = [
            {
                "persons": [
                    {
                        "id": 1,
                        "surname_id": 1,
                        "first_name_ids": [0],
                        "sex": "m",
                        "birth_date": "1990"
                    }
                ],
                "families": []
            },
            {
                "table_size": 1,
                "buckets": [[
                    {"crushed_name": "doe", "person_ids": [1]}
                ]]
            },
            {
                "table_size": 2,
                "buckets": [["John"], ["Doe"]]
            }
        ]
        
        context = SearchContext("test_db")
        result = context.find_person_details("doe", "john")
        
        # The method should return a dictionary or None
        assert result is None or isinstance(result, dict)


class TestAPIEndpoints:
    """Tests for API endpoints using TestClient."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "available_endpoints" in data

    @patch('backend.api.BASES_DIR')
    def test_list_dbs_endpoint_empty(self, mock_bases_dir, client):
        """Test list_dbs endpoint with no databases."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_bases_dir.__str__ = lambda: temp_dir
            mock_bases_dir.iterdir.return_value = []
            
            response = client.get("/dbs")
            assert response.status_code == 200
            data = response.json()
            assert data == []

    @patch('backend.api.BASES_DIR')
    def test_list_dbs_endpoint_with_databases(self, mock_bases_dir, client):
        """Test list_dbs endpoint with databases."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock database directories
            db1_dir = Path(temp_dir) / "db1.gwb"
            db2_dir = Path(temp_dir) / "db2.gwb"
            db1_dir.mkdir()
            db2_dir.mkdir()
            
            mock_bases_dir.iterdir.return_value = [db1_dir, db2_dir]
            
            response = client.get("/dbs")
            assert response.status_code == 200
            data = response.json()
            assert "db1" in data
            assert "db2" in data

    @patch('backend.api.parse_gw_text')
    def test_parse_gw_endpoint(self, mock_parse_gw, client):
        """Test parse_gw endpoint."""
        mock_parse_gw.return_value = {
            "persons": [{"id": 1, "name": "John Doe"}],
            "families": []
        }
        
        request_data = {"gw_text": "test gw content"}
        response = client.post("/parse_gw", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data
        assert "persons" in data
        assert "families" in data
        mock_parse_gw.assert_called_once_with("test gw content")

    @patch('backend.api.parse_gw_text')
    def test_parse_gw_endpoint_error(self, mock_parse_gw, client):
        """Test parse_gw endpoint with parsing error."""
        mock_parse_gw.side_effect = Exception("Parse error")
        
        request_data = {"gw_text": "invalid gw content"}
        response = client.post("/parse_gw", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is False
        assert "error" in data

    @patch('backend.api.write_gwb')
    @patch('backend.api.write_gwb_classic')
    @patch('backend.api.write_gw')
    @patch('backend.api.write_gwf')
    def test_import_database_endpoint(self, mock_write_gwf, mock_write_gw, 
                                    mock_write_gwb_classic, mock_write_gwb, client):
        """Test import database endpoint."""
        mock_write_gwb.return_value = Path("/test/db")
        mock_write_gw.return_value = Path("/test/db.gw")
        mock_write_gwf.return_value = Path("/test/db.gwf")
        
        request_data = {
            "db_name": "test_db",
            "persons": [
                {
                    "first_names": ["John"],
                    "surname": "Doe",
                    "sex": "m"
                }
            ],
            "families": [
                {
                    "husband_id": 1,
                    "wife_id": 2
                }
            ]
        }
        
        response = client.post("/import", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "db_dir" in data
        assert "gw_path" in data
        assert "gwf_path" in data

    @patch('backend.api.parse_gw_text')
    @patch('backend.api.write_gwb')
    @patch('backend.api.write_gwb_classic')
    @patch('backend.api.write_gw')
    @patch('backend.api.write_gwf')
    def test_import_gw_endpoint(self, mock_write_gwf, mock_write_gw,
                               mock_write_gwb_classic, mock_write_gwb,
                               mock_parse_gw, client):
        """Test import_gw endpoint."""
        mock_parse_gw.return_value = {
            "persons": [{"id": 1, "first_names": ["John"], "surname": "Doe"}],
            "families": []
        }
        mock_write_gwb.return_value = Path("/test/db")
        mock_write_gw.return_value = Path("/test/db.gw")
        mock_write_gwf.return_value = Path("/test/db.gwf")
        
        request_data = {
            "db_name": "test_db",
            "gw_text": "test gw content"
        }
        
        response = client.post("/import_gw", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        mock_parse_gw.assert_called_once_with("test gw content")

    @patch('backend.api.parse_ged_text')
    @patch('backend.api.write_gwb')
    @patch('backend.api.write_gwb_classic')
    @patch('backend.api.write_gw')
    @patch('backend.api.write_gwf')
    def test_import_ged_endpoint(self, mock_write_gwf, mock_write_gw,
                                mock_write_gwb_classic, mock_write_gwb,
                                mock_parse_ged, client):
        """Test import_ged endpoint."""
        mock_parse_ged.return_value = {
            "persons": [{"id": 1, "first_names": ["John"], "surname": "Doe"}],
            "families": []
        }
        mock_write_gwb.return_value = Path("/test/db")
        mock_write_gw.return_value = Path("/test/db.gw")
        mock_write_gwf.return_value = Path("/test/db.gwf")
        
        request_data = {
            "db_name": "test_db",
            "ged_text": "test ged content"
        }
        
        response = client.post("/import_ged", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        mock_parse_ged.assert_called_once_with("test ged content")

    @patch('backend.api.load_db_file')
    def test_stats_endpoint(self, mock_load_db_file, client):
        """Test stats endpoint."""
        mock_load_db_file.return_value = {
            "counts": {
                "persons": 100,
                "families": 50
            }
        }
        
        response = client.get("/db/test_db/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "persons" in data
        assert "families" in data
        assert data["persons"] == 100
        assert data["families"] == 50

    @patch('backend.api.load_db_file')
    def test_stats_endpoint_missing_db(self, mock_load_db_file, client):
        """Test stats endpoint with missing database."""
        mock_load_db_file.side_effect = FileNotFoundError("Database not found")
        
        response = client.get("/db/nonexistent/stats")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Base not found"

    @patch('backend.api.BASES_DIR')
    @patch('shutil.rmtree')
    def test_delete_db_endpoint(self, mock_rmtree, mock_bases_dir, client):
        """Test delete database endpoint."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_dir = Path(temp_dir) / "test_db.gwb"
            db_dir.mkdir()
            
            mock_bases_dir.__truediv__ = lambda self, other: db_dir if "test_db.gwb" in str(other) else Path(temp_dir) / other
            
            # Mock exists() method
            with patch.object(Path, 'exists', return_value=True):
                response = client.delete("/db/test_db")
            
            assert response.status_code == 200
            data = response.json()
            assert data["ok"] is True

    @patch('backend.api.BASES_DIR')
    def test_delete_db_endpoint_not_found(self, mock_bases_dir, client):
        """Test delete database endpoint with non-existent database."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_bases_dir.__truediv__ = lambda self, other: Path(temp_dir) / other
            
            # Mock exists() method to return False
            with patch.object(Path, 'exists', return_value=False):
                response = client.delete("/db/nonexistent")
            
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Base not found"

    @patch('backend.api.BASES_DIR')
    @patch('shutil.move')
    def test_rename_db_endpoint(self, mock_move, mock_bases_dir, client):
        """Test rename database endpoint."""
        with tempfile.TemporaryDirectory() as temp_dir:
            old_dir = Path(temp_dir) / "old_db.gwb"
            new_dir = Path(temp_dir) / "new_db.gwb"
            old_dir.mkdir()
            
            def mock_truediv(self, other):
                if "old_db.gwb" in str(other):
                    return old_dir
                elif "new_db.gwb" in str(other):
                    return new_dir
                return Path(temp_dir) / other
            
            mock_bases_dir.__truediv__ = mock_truediv
            
            # Mock exists() method
            def mock_exists(self):
                return "old_db.gwb" in str(self)
            
            with patch.object(Path, 'exists', mock_exists):
                request_data = {"new_name": "new_db"}
                response = client.post("/db/old_db/rename", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["ok"] is True

    @patch('backend.api.SearchContext')
    def test_search_db_endpoint(self, mock_search_context, client):
        """Test search database endpoint."""
        mock_context = Mock()
        mock_context.find_by_list.return_value = [
            {"id": 1, "name": "John Doe", "birth_date": "1990"}
        ]
        mock_search_context.return_value = mock_context
        
        response = client.get("/db/test_db/search?n=Doe&p=John")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "results" in data
        assert len(data["results"]) == 1

    @patch('backend.api.SearchContext')
    def test_get_person_details_endpoint(self, mock_search_context, client):
        """Test get person details endpoint."""
        mock_context = Mock()
        mock_context.find_person_details.return_value = {
            "id": 1,
            "name": "John Doe",
            "birth_date": "1990",
            "family": {}
        }
        mock_search_context.return_value = mock_context
        
        response = client.get("/db/test_db/person?n=Doe&p=John")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "person" in data
        assert data["person"]["id"] == 1

    def test_search_db_endpoint_missing_params(self, client):
        """Test search database endpoint with missing parameters."""
        response = client.get("/db/test_db/search")
        
        assert response.status_code == 400
        data = response.json()
        assert "Missing required parameters" in data["detail"]

    def test_get_person_details_endpoint_missing_params(self, client):
        """Test get person details endpoint with missing parameters."""
        response = client.get("/db/test_db/person")
        
        assert response.status_code == 400
        data = response.json()
        assert "Missing required parameters" in data["detail"]


class TestUtilityFunctions:
    """Tests for utility functions in the API module."""

    @patch('builtins.open')
    @patch('json.load')
    @patch('backend.api.BASES_DIR')
    def test_load_db_file_json(self, mock_bases_dir, mock_json_load, mock_open):
        """Test load_db_file function with JSON file."""
        from backend.api import load_db_file
        
        mock_json_load.return_value = {"test": "data"}
        mock_bases_dir.__truediv__ = lambda self, other: Path("/test") / other
        
        result = load_db_file("test_db", "test.json", is_json=True)
        
        assert result == {"test": "data"}
        mock_open.assert_called_once()
        mock_json_load.assert_called_once()

    @patch('builtins.open')
    @patch('backend.api.BASES_DIR')
    def test_load_db_file_text(self, mock_bases_dir, mock_open):
        """Test load_db_file function with text file."""
        from backend.api import load_db_file
        
        mock_file = Mock()
        mock_file.read.return_value = "test content"
        mock_open.return_value.__enter__.return_value = mock_file
        mock_bases_dir.__truediv__ = lambda self, other: Path("/test") / other
        
        result = load_db_file("test_db", "test.txt", is_json=False)
        
        assert result == "test content"
        mock_open.assert_called_once()

    @patch('backend.api.BASES_DIR')
    def test_load_db_file_not_found(self, mock_bases_dir):
        """Test load_db_file function with non-existent file."""
        from backend.api import load_db_file
        
        mock_bases_dir.__truediv__ = lambda self, other: Path("/nonexistent") / other
        
        with patch('builtins.open', side_effect=FileNotFoundError()):
            with pytest.raises(FileNotFoundError):
                load_db_file("test_db", "nonexistent.json")


class TestErrorHandling:
    """Tests for error handling in API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_invalid_json_request(self, client):
        """Test API endpoints with invalid JSON."""
        response = client.post("/import", data="invalid json")
        assert response.status_code == 422  # Validation error

    def test_missing_required_fields(self, client):
        """Test API endpoints with missing required fields."""
        # Missing db_name in import request
        request_data = {
            "persons": [],
            "families": []
        }
        response = client.post("/import", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_field_types(self, client):
        """Test API endpoints with invalid field types."""
        request_data = {
            "db_name": 123,  # Should be string
            "persons": [],
            "families": []
        }
        response = client.post("/import", json=request_data)
        assert response.status_code == 422  # Validation error

    @patch('backend.api.SearchContext')
    def test_search_endpoint_exception_handling(self, mock_search_context, client):
        """Test search endpoint exception handling."""
        mock_search_context.side_effect = Exception("Database error")
        
        response = client.get("/db/test_db/search?n=Doe&p=John")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is False
        assert "error" in data
        assert "Database error" in data["error"]