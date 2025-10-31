import pytest
import tempfile
import json
from pathlib import Path
from backend.storage import (
    StringsMap, write_gwb, write_gw, write_gwf, 
    write_gwb_classic, write_json_base, _encode_persons, _encode_families
)
from backend.models import Person, Family


class TestStringsMap:
    """Test the StringsMap class."""
    
    def test_strings_map_initialization(self):
        """Test StringsMap initialization."""
        sm = StringsMap()
        assert sm.strings == []
        assert sm.index_by_string == {}
    
    def test_get_id_none_returns_none(self):
        """Test get_id with None input."""
        sm = StringsMap()
        assert sm.get_id(None) is None
    
    def test_get_id_empty_string_returns_none(self):
        """Test get_id with empty string."""
        sm = StringsMap()
        assert sm.get_id("") is None
        assert sm.get_id("   ") is None
    
    def test_get_id_new_string_adds_to_map(self):
        """Test get_id with new string."""
        sm = StringsMap()
        id1 = sm.get_id("test")
        assert id1 == 0
        assert sm.strings == ["test"]
        assert sm.index_by_string == {"test": 0}
    
    def test_get_id_existing_string_returns_same_id(self):
        """Test get_id with existing string."""
        sm = StringsMap()
        id1 = sm.get_id("test")
        id2 = sm.get_id("test")
        assert id1 == id2 == 0
        assert len(sm.strings) == 1
    
    def test_get_id_multiple_strings(self):
        """Test get_id with multiple different strings."""
        sm = StringsMap()
        id1 = sm.get_id("first")
        id2 = sm.get_id("second")
        id3 = sm.get_id("first")  # Should return same as id1
        
        assert id1 == 0
        assert id2 == 1
        assert id3 == 0
        assert sm.strings == ["first", "second"]
    
    def test_get_id_strips_whitespace(self):
        """Test that get_id strips whitespace."""
        sm = StringsMap()
        id1 = sm.get_id("  test  ")
        id2 = sm.get_id("test")
        assert id1 == id2 == 0
        assert sm.strings == ["test"]


class TestEncodeFunctions:
    """Test the encoding functions."""
    
    def test_encode_persons_empty_list(self):
        """Test encoding empty persons list."""
        sm = StringsMap()
        result = _encode_persons([], sm)
        assert result == []
    
    def test_encode_persons_single_person(self):
        """Test encoding single person."""
        sm = StringsMap()
        person = Person(
            id=1,
            first_names=["John"],
            surname="Doe",
            sex="m",
            birth_date="1980",
            birth_place="New York"
        )
        result = _encode_persons([person], sm)
        
        assert len(result) == 1
        encoded = result[0]
        assert encoded["id"] == 1
        assert encoded["sex"] == "m"
        assert encoded["first_name_ids"] == [0]  # "John" gets id 0
        assert encoded["surname_id"] == 1  # "Doe" gets id 1
        assert encoded["birth_date_id"] == 2  # "1980" gets id 2
        assert encoded["birth_place_id"] == 3  # "New York" gets id 3
    
    def test_encode_families_empty_list(self):
        """Test encoding empty families list."""
        sm = StringsMap()
        result = _encode_families([], sm)
        assert result == []
    
    def test_encode_families_single_family(self):
        """Test encoding single family."""
        sm = StringsMap()
        family = Family(
            id=1,
            husband_id=2,
            wife_id=3,
            children_ids=[4, 5],
            marriage_date="2000",
            marriage_place="Paris"
        )
        result = _encode_families([family], sm)
        
        assert len(result) == 1
        encoded = result[0]
        assert encoded["id"] == 1
        assert encoded["husband_id"] == 2
        assert encoded["wife_id"] == 3
        assert encoded["children_ids"] == [4, 5]
        assert encoded["marriage_date_id"] == 0  # "2000" gets id 0
        assert encoded["marriage_place_id"] == 1  # "Paris" gets id 1


class TestWriteFunctions:
    """Test the write functions."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def sample_data(self):
        """Sample persons and families for testing."""
        persons = [
            Person(
                id=1,
                first_names=["John"],
                surname="Doe",
                sex="m",
                birth_date="1980",
                birth_place="New York"
            ),
            Person(
                id=2,
                first_names=["Jane"],
                surname="Smith",
                sex="f",
                birth_date="1985",
                birth_place="Boston"
            )
        ]
        families = [
            Family(
                id=1,
                husband_id=1,
                wife_id=2,
                children_ids=[],
                marriage_date="2005",
                marriage_place="Chicago"
            )
        ]
        return persons, families
    
    def test_write_gwb_creates_directory_and_files(self, temp_dir, sample_data):
        """Test that write_gwb creates the expected directory structure."""
        persons, families = sample_data
        db_name = "test_db"
        
        result_path = write_gwb(temp_dir, db_name, persons, families)
        
        assert result_path.exists()
        assert result_path.is_dir()
        assert result_path.name == f"{db_name}.gwb"
        
        # Check that required files are created
        assert (result_path / "base.json").exists()
        assert (result_path / "strings.inx.json").exists()
        assert (result_path / "names.inx.json").exists()
        assert (result_path / "base.acc.json").exists()
    
    def test_write_gwb_base_json_content(self, temp_dir, sample_data):
        """Test the content of base.json file."""
        persons, families = sample_data
        db_name = "test_db"
        
        result_path = write_gwb(temp_dir, db_name, persons, families)
        
        with open(result_path / "base.json", 'r', encoding='utf-8') as f:
            base_data = json.load(f)
        
        assert "persons" in base_data
        assert "families" in base_data
        assert len(base_data["persons"]) == 2
        assert len(base_data["families"]) == 1
        
        # Check person encoding
        person1 = base_data["persons"][0]
        assert person1["id"] == 1
        assert person1["sex"] == "m"
    
    def test_write_gwb_strings_index_content(self, temp_dir, sample_data):
        """Test the content of strings.inx.json file."""
        persons, families = sample_data
        db_name = "test_db"
        
        result_path = write_gwb(temp_dir, db_name, persons, families)
        
        # Check strings index structure
        with open(result_path / "strings.inx.json", 'r', encoding='utf-8') as f:
            strings_index = json.load(f)
        
        assert "buckets" in strings_index
        assert "table_size" in strings_index
        
        # Check that strings are in base.json
        with open(result_path / "base.json", 'r', encoding='utf-8') as f:
            base_data = json.load(f)
        
        assert "strings" in base_data
        strings_list = base_data["strings"]
        
        # Check that all strings from persons and families are included
        assert "John" in strings_list
        assert "Doe" in strings_list
        assert "Jane" in strings_list
        assert "Smith" in strings_list
        assert "1980" in strings_list
        assert "New York" in strings_list
        assert "2005" in strings_list
        assert "Chicago" in strings_list
    
    def test_write_gw_creates_file(self, temp_dir, sample_data):
        """Test that write_gw creates a .gw file."""
        persons, families = sample_data
        db_name = "test_db"
        
        result_path = write_gw(temp_dir, db_name, persons, families)
        
        assert result_path.exists()
        assert result_path.is_file()
        assert result_path.suffix == ".gw"
        assert result_path.name == f"{db_name}.gw"
    
    def test_write_gw_content_format(self, temp_dir, sample_data):
        """Test the content format of .gw file."""
        persons, families = sample_data
        db_name = "test_db"
        
        result_path = write_gw(temp_dir, db_name, persons, families)
        
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that content contains expected GW format elements
        assert "encoding: utf-8" in content
        assert "pevt Doe John" in content
        assert "pevt Smith Jane" in content
        assert "fam Doe John" in content
    
    def test_write_gwf_creates_file(self, temp_dir):
        """Test that write_gwf creates a .gwf file."""
        db_name = "test_db"
        
        result_path = write_gwf(temp_dir, db_name)
        
        assert result_path.exists()
        assert result_path.is_file()
        assert result_path.suffix == ".gwf"
        assert result_path.name == f"{db_name}.gwf"
    
    def test_write_json_base_creates_file(self, temp_dir, sample_data):
        """Test that write_json_base creates a JSON file."""
        persons, families = sample_data
        db_name = "test_db"
        
        result_path = write_json_base(temp_dir, db_name, persons, families)
        
        assert result_path.exists()
        assert result_path.is_dir()
        assert result_path.name == db_name
        assert (result_path / "base.json").exists()
        assert (result_path / "base.json").is_file()
    
    def test_write_json_base_content(self, temp_dir, sample_data):
        """Test the content of JSON base file."""
        persons, families = sample_data
        db_name = "test_db"
        
        result_path = write_json_base(temp_dir, db_name, persons, families)
        
        with open(result_path / "base.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "persons" in data
        assert "families" in data
        assert len(data["persons"]) == 2
        assert len(data["families"]) == 1
        
        # Check person data
        person1 = data["persons"][0]
        assert "first_name_ids" in person1
        assert "surname_id" in person1
        assert person1["sex"] == "m"
    
    def test_write_gwb_classic_creates_directory(self, temp_dir, sample_data):
        """Test that write_gwb_classic creates the expected directory structure."""
        persons, families = sample_data
        db_name = "test_db"
        
        result_path = write_gwb_classic(temp_dir, db_name, persons, families)
        
        assert result_path.exists()
        assert result_path.is_dir()
        assert result_path.name == f"{db_name}.gwb"
    
    def test_write_functions_with_notes_origin_file(self, temp_dir, sample_data):
        """Test write functions with notes_origin_file parameter."""
        persons, families = sample_data
        db_name = "test_db"
        notes_file = "source.ged"
        
        # Test write_gwb with notes
        result_path = write_gwb(temp_dir, db_name, persons, families, notes_file)
        assert result_path.exists()
        
        # Test write_json_base with notes
        json_path = write_json_base(temp_dir, f"{db_name}_json", persons, families, notes_file)
        assert json_path.exists()
        
        with open(json_path / "base.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert "notes_origin_file" in data
        assert data["notes_origin_file"] == notes_file
    
    def test_write_functions_with_empty_data(self, temp_dir):
        """Test write functions with empty persons and families lists."""
        db_name = "empty_db"
        
        # Test all write functions with empty data
        gwb_path = write_gwb(temp_dir, db_name, [], [])
        assert gwb_path.exists()
        
        gw_path = write_gw(temp_dir, f"{db_name}_gw", [], [])
        assert gw_path.exists()
        
        json_path = write_json_base(temp_dir, f"{db_name}_json", [], [])
        assert json_path.exists()
        
        # Check that files contain empty data structures
        with open(json_path / "base.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data["persons"] == []
        assert data["families"] == []