import pytest
from unittest.mock import patch, Mock
from backend.ged_parser import (
    GedRecord, _tokenize, parse_ged_text, GED_TAG_LEVEL
)
from backend.models import Person, Family


class TestConstants:
    """Tests for module constants."""

    def test_ged_tag_level_constants(self):
        """Test GED_TAG_LEVEL constants."""
        assert GED_TAG_LEVEL["INDI"] == 0
        assert GED_TAG_LEVEL["FAM"] == 0
        assert len(GED_TAG_LEVEL) == 2


class TestGedRecord:
    """Tests for GedRecord class."""

    def test_ged_record_initialization(self):
        """Test GedRecord initialization."""
        record = GedRecord("INDI")
        assert record.tag == "INDI"
        assert record.xref is None
        assert record.lines == []

    def test_ged_record_initialization_with_xref(self):
        """Test GedRecord initialization with xref."""
        record = GedRecord("INDI", "@I1@")
        assert record.tag == "INDI"
        assert record.xref == "@I1@"
        assert record.lines == []

    def test_ged_record_add_line(self):
        """Test adding lines to GedRecord."""
        record = GedRecord("INDI")
        record.add(1, "NAME", "John /Doe/")
        
        assert len(record.lines) == 1
        assert record.lines[0] == (1, "NAME", "John /Doe/")

    def test_ged_record_add_multiple_lines(self):
        """Test adding multiple lines to GedRecord."""
        record = GedRecord("INDI")
        record.add(1, "NAME", "John /Doe/")
        record.add(1, "SEX", "M")
        record.add(1, "BIRT", None)
        record.add(2, "DATE", "1990")
        
        assert len(record.lines) == 4
        assert record.lines[0] == (1, "NAME", "John /Doe/")
        assert record.lines[1] == (1, "SEX", "M")
        assert record.lines[2] == (1, "BIRT", None)
        assert record.lines[3] == (2, "DATE", "1990")

    def test_ged_record_add_line_with_none_data(self):
        """Test adding line with None data."""
        record = GedRecord("INDI")
        record.add(1, "BIRT", None)
        
        assert len(record.lines) == 1
        assert record.lines[0] == (1, "BIRT", None)


class TestTokenize:
    """Tests for _tokenize function."""

    def test_tokenize_empty_string(self):
        """Test tokenizing empty string."""
        result = _tokenize("")
        assert result == []

    def test_tokenize_whitespace_only(self):
        """Test tokenizing whitespace-only string."""
        result = _tokenize("   \n\t  \n  ")
        assert result == []

    def test_tokenize_simple_line(self):
        """Test tokenizing simple GEDCOM line."""
        result = _tokenize("0 HEAD")
        assert len(result) == 1
        assert result[0] == (0, None, "HEAD", None)

    def test_tokenize_line_with_data(self):
        """Test tokenizing line with data."""
        result = _tokenize("1 NAME John /Doe/")
        assert len(result) == 1
        assert result[0] == (1, None, "NAME", "John /Doe/")

    def test_tokenize_line_with_xref(self):
        """Test tokenizing line with xref."""
        result = _tokenize("0 @I1@ INDI")
        assert len(result) == 1
        assert result[0] == (0, "@I1@", "INDI", None)

    def test_tokenize_line_with_xref_and_data(self):
        """Test tokenizing line with xref and data."""
        result = _tokenize("0 @F1@ FAM")
        assert len(result) == 1
        assert result[0] == (0, "@F1@", "FAM", None)

    def test_tokenize_multiple_lines(self):
        """Test tokenizing multiple lines."""
        ged_text = """0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
2 DATE 1990"""
        
        result = _tokenize(ged_text)
        assert len(result) == 4
        assert result[0] == (0, "@I1@", "INDI", None)
        assert result[1] == (1, None, "NAME", "John /Doe/")
        assert result[2] == (1, None, "SEX", "M")
        assert result[3] == (2, None, "DATE", "1990")

    def test_tokenize_with_empty_lines(self):
        """Test tokenizing with empty lines."""
        ged_text = """0 @I1@ INDI

1 NAME John /Doe/

1 SEX M"""
        
        result = _tokenize(ged_text)
        assert len(result) == 3
        assert result[0] == (0, "@I1@", "INDI", None)
        assert result[1] == (1, None, "NAME", "John /Doe/")
        assert result[2] == (1, None, "SEX", "M")

    def test_tokenize_with_trailing_whitespace(self):
        """Test tokenizing with trailing whitespace."""
        ged_text = "0 @I1@ INDI   \n1 NAME John /Doe/  \t"
        
        result = _tokenize(ged_text)
        assert len(result) == 2
        assert result[0] == (0, "@I1@", "INDI", None)
        assert result[1] == (1, None, "NAME", "John /Doe/")

    def test_tokenize_invalid_level(self):
        """Test tokenizing with invalid level."""
        ged_text = """0 @I1@ INDI
INVALID NAME John
1 SEX M"""
        
        result = _tokenize(ged_text)
        assert len(result) == 2
        assert result[0] == (0, "@I1@", "INDI", None)
        assert result[1] == (1, None, "SEX", "M")

    def test_tokenize_no_tag(self):
        """Test tokenizing line with no tag."""
        ged_text = """0 @I1@ INDI
1
1 SEX M"""
        
        result = _tokenize(ged_text)
        assert len(result) == 2
        assert result[0] == (0, "@I1@", "INDI", None)
        assert result[1] == (1, None, "SEX", "M")

    def test_tokenize_complex_data(self):
        """Test tokenizing with complex data containing spaces."""
        result = _tokenize("2 PLAC New York, NY, USA")
        assert len(result) == 1
        assert result[0] == (2, None, "PLAC", "New York, NY, USA")

    def test_tokenize_xref_without_at_symbols(self):
        """Test tokenizing with invalid xref format."""
        result = _tokenize("0 I1 INDI")
        assert len(result) == 1
        assert result[0] == (0, None, "I1", "INDI")

    def test_tokenize_partial_xref(self):
        """Test tokenizing with partial xref format."""
        result = _tokenize("0 @I1 INDI")
        assert len(result) == 1
        assert result[0] == (0, None, "@I1", "INDI")


class TestParseGedText:
    """Tests for parse_ged_text function."""

    def test_parse_empty_ged(self):
        """Test parsing empty GEDCOM text."""
        result = parse_ged_text("")
        assert "persons" in result
        assert "families" in result
        assert "notes" in result
        assert result["persons"] == []
        assert result["families"] == []
        assert result["notes"] == {}

    def test_parse_simple_person(self):
        """Test parsing simple person record."""
        ged_text = """0 @I1@ INDI
1 NAME John /Doe/
1 SEX M"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 1
        assert len(result["families"]) == 0
        
        person = result["persons"][0]
        assert person.first_names == ["John"]
        assert person.surname == "Doe"
        assert person.sex == "M"
        assert person.id == 1

    def test_parse_person_with_birth_info(self):
        """Test parsing person with birth information."""
        ged_text = """0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 BIRT
2 DATE 1990
2 PLAC New York"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 1
        person = result["persons"][0]
        assert person.birth_date == "1990"
        assert person.birth_place == "New York"

    def test_parse_person_with_death_info(self):
        """Test parsing person with death information."""
        ged_text = """0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 DEAT
2 DATE 2020
2 PLAC Boston"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 1
        person = result["persons"][0]
        assert person.death_date == "2020"
        assert person.death_place == "Boston"

    def test_parse_person_with_multiple_first_names(self):
        """Test parsing person with multiple first names."""
        ged_text = """0 @I1@ INDI
1 NAME John William /Doe/
1 SEX M"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 1
        person = result["persons"][0]
        assert person.first_names == ["John", "William"]
        assert person.surname == "Doe"

    def test_parse_person_name_without_surname(self):
        """Test parsing person name without surname."""
        ged_text = """0 @I1@ INDI
1 NAME John
1 SEX M"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 1
        person = result["persons"][0]
        assert person.first_names == ["John"]
        assert person.surname == ""

    def test_parse_person_with_female_sex(self):
        """Test parsing person with female sex."""
        ged_text = """0 @I1@ INDI
1 NAME Jane /Doe/
1 SEX F"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 1
        person = result["persons"][0]
        assert person.sex == "F"

    def test_parse_person_with_unknown_sex(self):
        """Test parsing person with unknown sex."""
        ged_text = """0 @I1@ INDI
1 NAME Unknown /Person/
1 SEX U"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 1
        person = result["persons"][0]
        assert person.sex == "U"

    def test_parse_person_with_invalid_sex(self):
        """Test parsing person with invalid sex value."""
        ged_text = """0 @I1@ INDI
1 NAME Test /Person/
1 SEX X"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 1
        person = result["persons"][0]
        assert person.sex is None

    def test_parse_simple_family(self):
        """Test parsing simple family record."""
        ged_text = """0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 2
        assert len(result["families"]) == 1
        
        family = result["families"][0]
        assert family.husband_id == 1
        assert family.wife_id == 2
        assert family.children_ids == []

    def test_parse_family_with_children(self):
        """Test parsing family with children."""
        ged_text = """0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
0 @I3@ INDI
1 NAME Child1 /Doe/
1 SEX M
0 @I4@ INDI
1 NAME Child2 /Doe/
1 SEX F
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
1 CHIL @I4@"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 4
        assert len(result["families"]) == 1
        
        family = result["families"][0]
        assert family.husband_id == 1
        assert family.wife_id == 2
        assert len(family.children_ids) == 2
        assert 3 in family.children_ids
        assert 4 in family.children_ids

    def test_parse_family_with_marriage_info(self):
        """Test parsing family with marriage information."""
        ged_text = """0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 MARR
2 DATE 2000
2 PLAC Church"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["families"]) == 1
        family = result["families"][0]
        assert family.marriage_date == "2000"
        assert family.marriage_place == "Church"

    def test_parse_family_relationships(self):
        """Test parsing family relationships (FAMC)."""
        ged_text = """0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
0 @I3@ INDI
1 NAME Child /Doe/
1 SEX M
1 FAMC @F1@
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 3
        assert len(result["families"]) == 1
        
        # Find the child
        child = next(p for p in result["persons"] if p.first_names == ["Child"])
        assert child.father_id == 1  # John's ID
        assert child.mother_id == 2  # Jane's ID

    def test_parse_multiple_families(self):
        """Test parsing multiple families."""
        ged_text = """0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
0 @I3@ INDI
1 NAME Bob /Johnson/
1 SEX M
0 @I4@ INDI
1 NAME Alice /Brown/
1 SEX F
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
0 @F2@ FAM
1 HUSB @I3@
1 WIFE @I4@"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 4
        assert len(result["families"]) == 2
        
        family1 = result["families"][0]
        family2 = result["families"][1]
        
        assert family1.husband_id == 1
        assert family1.wife_id == 2
        assert family2.husband_id == 3
        assert family2.wife_id == 4

    def test_parse_incomplete_family(self):
        """Test parsing family with missing spouse."""
        ged_text = """0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 @F1@ FAM
1 HUSB @I1@"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 1
        assert len(result["families"]) == 1
        
        family = result["families"][0]
        assert family.husband_id == 1
        assert family.wife_id is None

    def test_parse_family_with_nonexistent_person(self):
        """Test parsing family referencing non-existent person."""
        ged_text = """0 @F1@ FAM
1 HUSB @I999@
1 WIFE @I888@
1 CHIL @I777@"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 0
        assert len(result["families"]) == 1
        
        family = result["families"][0]
        assert family.husband_id is None
        assert family.wife_id is None
        assert family.children_ids == []

    def test_parse_person_without_xref(self):
        """Test parsing person record without xref."""
        ged_text = """0 INDI
1 NAME John /Doe/
1 SEX M"""
        
        result = parse_ged_text(ged_text)
        
        # Should be ignored since no xref
        assert len(result["persons"]) == 0
        assert len(result["families"]) == 0

    def test_parse_mixed_valid_invalid_records(self):
        """Test parsing mix of valid and invalid records."""
        ged_text = """0 HEAD
1 SOUR Test
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 TRLR"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 1
        assert len(result["families"]) == 0
        
        person = result["persons"][0]
        assert person.first_names == ["John"]
        assert person.surname == "Doe"

    def test_parse_complex_nested_structure(self):
        """Test parsing complex nested GEDCOM structure."""
        ged_text = """0 @I1@ INDI
1 NAME John William /Doe Jr./
1 SEX M
1 BIRT
2 DATE 15 JAN 1990
2 PLAC New York, NY, USA
3 NOTE Birth certificate available
1 DEAT
2 DATE 20 DEC 2020
2 PLAC Boston, MA, USA
1 FAMC @F1@
0 @I2@ INDI
1 NAME Jane Marie /Smith/
1 SEX F
0 @F1@ FAM
1 HUSB @I2@
1 WIFE @I1@
1 MARR
2 DATE 1989
2 PLAC Las Vegas
1 CHIL @I1@"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 2
        assert len(result["families"]) == 1
        
        # Find John
        john = next(p for p in result["persons"] if "John" in p.first_names)
        assert john.first_names == ["John", "William"]
        assert john.surname == "Doe Jr."
        assert john.birth_date == "15 JAN 1990"
        assert john.birth_place == "New York, NY, USA"
        assert john.death_date == "20 DEC 2020"
        assert john.death_place == "Boston, MA, USA"
        
        # Check family
        family = result["families"][0]
        assert family.marriage_date == "1989"
        assert family.marriage_place == "Las Vegas"

    def test_parse_whitespace_handling(self):
        """Test parsing with various whitespace scenarios."""
        ged_text = """0 @I1@ INDI
1 NAME   John   /Doe/  
1 SEX   M   
1 BIRT
2 DATE   1990   
2 PLAC   New York   """
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 1
        person = result["persons"][0]
        assert person.first_names == ["John"]
        assert person.surname == "Doe"
        assert person.birth_date == "1990"
        assert person.birth_place == "New York"

    def test_parse_case_sensitivity(self):
        """Test parsing with different case for sex values."""
        ged_text = """0 @I1@ INDI
1 NAME John /Doe/
1 SEX m
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX f
0 @I3@ INDI
1 NAME Unknown /Person/
1 SEX u"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 3
        assert result["persons"][0].sex == "M"
        assert result["persons"][1].sex == "F"
        assert result["persons"][2].sex == "U"

    @patch('backend.ged_parser.IdAllocator')
    def test_parse_with_mocked_id_allocator(self, mock_id_allocator):
        """Test parsing with mocked ID allocator."""
        mock_pid_alloc = Mock()
        mock_fid_alloc = Mock()
        mock_pid_alloc.alloc.side_effect = [100, 101]
        mock_fid_alloc.alloc.side_effect = [200]
        
        mock_id_allocator.side_effect = [mock_pid_alloc, mock_fid_alloc]
        
        ged_text = """0 @I1@ INDI
1 NAME John /Doe/
0 @I2@ INDI
1 NAME Jane /Smith/
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 2
        assert len(result["families"]) == 1
        assert result["persons"][0].id == 100
        assert result["persons"][1].id == 101
        assert result["families"][0].id == 200

    def test_parse_edge_cases(self):
        """Test parsing edge cases and malformed data."""
        ged_text = """0 @I1@ INDI
1 NAME //
1 SEX
1 BIRT
2 DATE
2 PLAC
1 DEAT
2 DATE
2 PLAC"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 1
        person = result["persons"][0]
        assert person.first_names == []
        assert person.surname == ""
        assert person.sex is None
        assert person.birth_date is None
        assert person.birth_place is None
        assert person.death_date is None
        assert person.death_place is None

    def test_parse_result_structure(self):
        """Test that parse result has correct structure."""
        result = parse_ged_text("")
        
        assert isinstance(result, dict)
        assert "persons" in result
        assert "families" in result
        assert "notes" in result
        assert isinstance(result["persons"], list)
        assert isinstance(result["families"], list)
        assert isinstance(result["notes"], dict)

    def test_parse_returns_person_objects(self):
        """Test that parse returns proper Person objects."""
        ged_text = """0 @I1@ INDI
1 NAME John /Doe/
1 SEX M"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["persons"]) == 1
        person = result["persons"][0]
        assert isinstance(person, Person)
        assert hasattr(person, 'id')
        assert hasattr(person, 'first_names')
        assert hasattr(person, 'surname')
        assert hasattr(person, 'sex')
        assert hasattr(person, 'birth_date')
        assert hasattr(person, 'birth_place')
        assert hasattr(person, 'death_date')
        assert hasattr(person, 'death_place')
        assert hasattr(person, 'father_id')
        assert hasattr(person, 'mother_id')

    def test_parse_returns_family_objects(self):
        """Test that parse returns proper Family objects."""
        ged_text = """0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@"""
        
        result = parse_ged_text(ged_text)
        
        assert len(result["families"]) == 1
        family = result["families"][0]
        assert isinstance(family, Family)
        assert hasattr(family, 'id')
        assert hasattr(family, 'husband_id')
        assert hasattr(family, 'wife_id')
        assert hasattr(family, 'children_ids')
        assert hasattr(family, 'marriage_date')
        assert hasattr(family, 'marriage_place')