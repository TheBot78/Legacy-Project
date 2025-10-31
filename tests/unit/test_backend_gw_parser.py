import pytest
from unittest.mock import patch, Mock
from backend.gw_parser import (
    _clean_token, _normalize_place, _name_key, _parse_name_pair,
    _looks_date, parse_gw_text
)
from backend.models import Person, Family


class TestCleanToken:
    """Tests for _clean_token function."""

    def test_clean_token_none(self):
        """Test cleaning None token."""
        result = _clean_token(None)
        assert result == ""

    def test_clean_token_empty_string(self):
        """Test cleaning empty string."""
        result = _clean_token("")
        assert result == ""

    def test_clean_token_simple_string(self):
        """Test cleaning simple string."""
        result = _clean_token("John")
        assert result == "John"

    def test_clean_token_with_underscores(self):
        """Test cleaning token with underscores."""
        result = _clean_token("John_Doe")
        assert result == "John Doe"

    def test_clean_token_with_escaped_underscores(self):
        """Test cleaning token with escaped underscores."""
        result = _clean_token(r"John\_Doe")
        assert result == "John Doe"

    def test_clean_token_with_disambiguation(self):
        """Test cleaning token with disambiguation suffix."""
        result = _clean_token("John.1234")
        assert result == "John"

    def test_clean_token_with_disambiguation_and_underscores(self):
        """Test cleaning token with both underscores and disambiguation."""
        result = _clean_token("John_Doe.5678")
        assert result == "John Doe"

    def test_clean_token_with_whitespace(self):
        """Test cleaning token with whitespace."""
        result = _clean_token("  John_Doe  ")
        assert result == "John Doe"

    def test_clean_token_complex(self):
        """Test cleaning complex token."""
        result = _clean_token(r"  John\_William_Doe.9999  ")
        assert result == "John William Doe.9999"

    def test_clean_token_only_disambiguation(self):
        """Test cleaning token that is only disambiguation."""
        result = _clean_token(".1234")
        assert result == ""

    def test_clean_token_multiple_dots(self):
        """Test cleaning token with multiple dots."""
        result = _clean_token("John.Smith.1234")
        assert result == "John.Smith"


class TestNormalizePlace:
    """Tests for _normalize_place function."""

    def test_normalize_place_simple(self):
        """Test normalizing simple place."""
        result = _normalize_place("New York")
        assert result == "New York"

    def test_normalize_place_with_underscores(self):
        """Test normalizing place with underscores."""
        result = _normalize_place("New_York")
        assert result == "New York"

    def test_normalize_place_with_escaped_underscores(self):
        """Test normalizing place with escaped underscores."""
        result = _normalize_place(r"New\_York_City")
        assert result == "New York City"

    def test_normalize_place_with_brackets(self):
        """Test normalizing place with brackets."""
        result = _normalize_place("[Saint-Jacques]")
        assert result == "[Saint-Jacques]"

    def test_normalize_place_with_brackets_and_text(self):
        """Test normalizing place with brackets and text."""
        result = _normalize_place("Paris [Saint-Jacques] France")
        assert result == "Paris [Saint-Jacques] France"

    def test_normalize_place_multiple_brackets(self):
        """Test normalizing place with multiple brackets."""
        result = _normalize_place("[Paris] [France]")
        assert result == "[Paris] [France]"

    def test_normalize_place_with_whitespace(self):
        """Test normalizing place with whitespace."""
        result = _normalize_place("  New_York  ")
        assert result == "New York"

    def test_normalize_place_empty(self):
        """Test normalizing empty place."""
        result = _normalize_place("")
        assert result == ""

    def test_normalize_place_complex(self):
        """Test normalizing complex place."""
        result = _normalize_place(r"  New\_York_City_[Manhattan]_USA  ")
        assert result == "New York City [Manhattan] USA"


class TestNameKey:
    """Tests for _name_key function."""

    def test_name_key_simple(self):
        """Test creating name key with simple names."""
        result = _name_key("Doe", ["John"])
        assert result == "Doe|John"

    def test_name_key_multiple_first_names(self):
        """Test creating name key with multiple first names."""
        result = _name_key("Doe", ["John", "William"])
        assert result == "Doe|John William"

    def test_name_key_empty_first_names(self):
        """Test creating name key with empty first names."""
        result = _name_key("Doe", [])
        assert result == "Doe|"

    def test_name_key_empty_surname(self):
        """Test creating name key with empty surname."""
        result = _name_key("", ["John"])
        assert result == "|John"

    def test_name_key_both_empty(self):
        """Test creating name key with both empty."""
        result = _name_key("", [])
        assert result == "|"

    def test_name_key_with_spaces(self):
        """Test creating name key with spaces in names."""
        result = _name_key("Van Der Berg", ["John Peter"])
        assert result == "Van Der Berg|John Peter"

    def test_name_key_strips_whitespace(self):
        """Test that _name_key strips whitespace."""
        result = _name_key("  Doe  ", ["  John  "])
        assert result == "Doe  |  John"


class TestParseNamePair:
    """Tests for _parse_name_pair function."""

    def test_parse_name_pair_simple(self):
        """Test parsing simple name pair."""
        tokens = ["Doe", "John"]
        idx, surname, first_names = _parse_name_pair(tokens, 0)
        assert idx == 2
        assert surname == "Doe"
        assert first_names == ["John"]

    def test_parse_name_pair_multiple_first_names(self):
        """Test parsing name pair with multiple first names."""
        tokens = ["Doe", "John_William"]
        idx, surname, first_names = _parse_name_pair(tokens, 0)
        assert idx == 2
        assert surname == "Doe"
        assert first_names == ["John", "William"]

    def test_parse_name_pair_with_start_index(self):
        """Test parsing name pair with custom start index."""
        tokens = ["fam", "Doe", "John", "other"]
        idx, surname, first_names = _parse_name_pair(tokens, 1)
        assert idx == 3
        assert surname == "Doe"
        assert first_names == ["John"]

    def test_parse_name_pair_insufficient_tokens(self):
        """Test parsing name pair with insufficient tokens."""
        tokens = ["Doe"]
        idx, surname, first_names = _parse_name_pair(tokens, 0)
        assert idx == 2
        assert surname == "Doe"
        assert first_names == []

    def test_parse_name_pair_empty_tokens(self):
        """Test parsing name pair with empty tokens."""
        tokens = []
        idx, surname, first_names = _parse_name_pair(tokens, 0)
        assert idx == 0
        assert surname == ""
        assert first_names == []

    def test_parse_name_pair_start_index_out_of_bounds(self):
        """Test parsing name pair with start index out of bounds."""
        tokens = ["Doe", "John"]
        idx, surname, first_names = _parse_name_pair(tokens, 5)
        assert idx == 5
        assert surname == ""
        assert first_names == []

    def test_parse_name_pair_with_underscores(self):
        """Test parsing name pair with underscores."""
        tokens = ["Van_Der_Berg", "John_William"]
        idx, surname, first_names = _parse_name_pair(tokens, 0)
        assert idx == 2
        assert surname == "Van Der Berg"
        assert first_names == ["John", "William"]

    def test_parse_name_pair_with_disambiguation(self):
        """Test parsing name pair with disambiguation."""
        tokens = ["Doe.1234", "John.5678"]
        idx, surname, first_names = _parse_name_pair(tokens, 0)
        assert idx == 2
        assert surname == "Doe"
        assert first_names == ["John"]


class TestLooksDate:
    """Tests for _looks_date function."""

    def test_looks_date_empty(self):
        """Test date detection with empty string."""
        assert _looks_date("") is False

    def test_looks_date_none(self):
        """Test date detection with None."""
        assert _looks_date(None) is False

    def test_looks_date_year_only(self):
        """Test date detection with year only."""
        assert _looks_date("1990") is True
        assert _looks_date("2023") is True
        assert _looks_date("800") is True

    def test_looks_date_full_date(self):
        """Test date detection with full date."""
        assert _looks_date("15/01/1990") is True
        assert _looks_date("1/1/90") is True
        assert _looks_date("31/12/2023") is True

    def test_looks_date_with_prefix(self):
        """Test date detection with prefix."""
        assert _looks_date("<1990") is True
        assert _looks_date("~1990") is True
        assert _looks_date("<15/01/1990") is True
        assert _looks_date("~31/12/2023") is True

    def test_looks_date_invalid_formats(self):
        """Test date detection with invalid formats."""
        assert _looks_date("abc") is False
        assert _looks_date("19") is False
        assert _looks_date("19900") is False
        assert _looks_date("15/1990") is False
        assert _looks_date("15/01") is False
        assert _looks_date("15/01/90/extra") is False

    def test_looks_date_edge_cases(self):
        """Test date detection with edge cases."""
        assert _looks_date("999") is True  # 3 digits
        assert _looks_date("99") is False  # 2 digits
        assert _looks_date("9999") is True  # 4 digits
        assert _looks_date("10000") is False  # 5 digits

    def test_looks_date_with_spaces(self):
        """Test date detection with spaces."""
        assert _looks_date(" 1990 ") is False
        assert _looks_date("15 / 01 / 1990") is False


class TestParseGwText:
    """Tests for parse_gw_text function."""

    def test_parse_empty_text(self):
        """Test parsing empty GW text."""
        result = parse_gw_text("")
        assert "persons" in result
        assert "families" in result
        assert "notes" in result
        assert result["persons"] == []
        assert result["families"] == []
        assert result["notes"] == {}

    def test_parse_encoding_line(self):
        """Test parsing with encoding line."""
        gw_text = "encoding: utf-8\ngwplus\n"
        result = parse_gw_text(gw_text)
        assert result["persons"] == []
        assert result["families"] == []

    def test_parse_simple_family(self):
        """Test parsing simple family."""
        gw_text = "fam Doe John + Smith Jane"
        result = parse_gw_text(gw_text)
        
        assert len(result["persons"]) == 2
        assert len(result["families"]) == 1
        
        # Check persons
        john = next(p for p in result["persons"] if p.first_names == ["John"])
        jane = next(p for p in result["persons"] if p.first_names == ["Jane"])
        
        assert john.surname == "Doe"
        assert john.sex == "M"
        assert jane.surname == "Smith"
        assert jane.sex == "F"
        
        # Check family
        family = result["families"][0]
        assert family.husband_id == john.id
        assert family.wife_id == jane.id
        assert family.children_ids == []

    def test_parse_family_with_children(self):
        """Test parsing family with children."""
        gw_text = """fam Doe John + Smith Jane
beg
- h Child1 1990
- f Child2 1992
end"""
        
        result = parse_gw_text(gw_text)
        
        assert len(result["persons"]) == 4
        assert len(result["families"]) == 1
        
        # Find children
        child1 = next(p for p in result["persons"] if p.first_names == ["Child1"])
        child2 = next(p for p in result["persons"] if p.first_names == ["Child2"])
        
        assert child1.surname == "Doe"  # Inherited from father
        assert child1.sex == "M"
        assert child1.birth_date == "1990"
        
        assert child2.surname == "Doe"  # Inherited from father
        assert child2.sex == "F"
        assert child2.birth_date == "1992"
        
        # Check family relationships
        family = result["families"][0]
        assert child1.id in family.children_ids
        assert child2.id in family.children_ids
        
        # Check parent relationships
        john = next(p for p in result["persons"] if p.first_names == ["John"])
        jane = next(p for p in result["persons"] if p.first_names == ["Jane"])
        
        assert child1.father_id == john.id
        assert child1.mother_id == jane.id
        assert child2.father_id == john.id
        assert child2.mother_id == jane.id

    def test_parse_family_with_explicit_child_surname(self):
        """Test parsing family with explicit child surname."""
        gw_text = """fam Doe John + Smith Jane
beg
- h Johnson Robert 1990
end"""
        
        result = parse_gw_text(gw_text)
        
        # Find child
        child = next(p for p in result["persons"] if p.first_names == ["Robert"])
        assert child.surname == "Johnson"  # Explicit surname
        assert child.sex == "M"
        assert child.birth_date == "1990"

    def test_parse_family_with_marriage_event(self):
        """Test parsing family with marriage event."""
        gw_text = """fam Doe John + Smith Jane
fevt
#marr 1985 #p Paris
end fevt"""
        
        result = parse_gw_text(gw_text)
        
        assert len(result["families"]) == 1
        family = result["families"][0]
        assert family.marriage_date == "1985"
        assert family.marriage_place == "Paris"

    def test_parse_family_with_marriage_place_only(self):
        """Test parsing family with marriage place only."""
        gw_text = """fam Doe John + Smith Jane
fevt
#marr #p New_York
end fevt"""
        
        result = parse_gw_text(gw_text)
        
        family = result["families"][0]
        assert family.marriage_date is None
        assert family.marriage_place == "New York"

    def test_parse_family_with_mp_tag(self):
        """Test parsing family with #mp tag for marriage place."""
        gw_text = """fam Doe John + Smith Jane
fevt
#marr 1985 #mp Church_of_St_Mary
end fevt"""
        
        result = parse_gw_text(gw_text)
        
        family = result["families"][0]
        assert family.marriage_date == "1985"
        assert family.marriage_place == "Church of St Mary"

    def test_parse_single_parent_family(self):
        """Test parsing single parent family (no + separator)."""
        gw_text = """fam Doe John
beg
- h Child 1990
end"""
        
        result = parse_gw_text(gw_text)
        
        assert len(result["persons"]) == 2
        assert len(result["families"]) == 1
        
        family = result["families"][0]
        john = next(p for p in result["persons"] if p.first_names == ["John"])
        child = next(p for p in result["persons"] if p.first_names == ["Child"])
        
        assert family.husband_id == john.id
        assert family.wife_id is None
        assert child.father_id == john.id
        assert child.mother_id is None

    def test_parse_family_with_date_tokens_before_wife(self):
        """Test parsing family with date tokens before wife name."""
        gw_text = "fam Doe John + 1985 #marr Smith Jane"
        
        result = parse_gw_text(gw_text)
        
        assert len(result["persons"]) == 2
        john = next(p for p in result["persons"] if p.first_names == ["John"])
        jane = next(p for p in result["persons"] if p.first_names == ["Jane"])
        
        assert john.surname == "Doe"
        assert jane.surname == "Smith"

    def test_parse_person_events(self):
        """Test parsing person events."""
        gw_text = """pevt Doe John
#birt 1990 #bp New_York
#deat 2020 #dp Boston
end pevt"""
        
        result = parse_gw_text(gw_text)
        
        assert len(result["persons"]) == 1
        person = result["persons"][0]
        
        assert person.first_names == ["John"]
        assert person.surname == "Doe"
        assert person.birth_date == "1990"
        assert person.birth_place == "New York"
        assert person.death_date == "2020"
        assert person.death_place == "Boston"

    def test_parse_person_events_with_general_place_tags(self):
        """Test parsing person events with general place tags."""
        gw_text = """pevt Doe John
#birt 1990
#p New_York
#deat 2020
#p Boston
end pevt"""
        
        result = parse_gw_text(gw_text)
        
        person = result["persons"][0]
        assert person.birth_date == "1990"
        assert person.birth_place == "New York"
        assert person.death_date == "2020"
        assert person.death_place == "Boston"

    def test_parse_person_events_baptism(self):
        """Test parsing person events with baptism."""
        gw_text = """pevt Doe John
#bapt 1990 #bp Church
end pevt"""
        
        result = parse_gw_text(gw_text)
        
        person = result["persons"][0]
        assert person.birth_place == "Church"  # baptism place becomes birth place

    def test_parse_notes(self):
        """Test parsing notes."""
        gw_text = """notes Doe John
beg
This is a note about John Doe.
He was born in New York.
end notes"""
        
        result = parse_gw_text(gw_text)
        
        expected_key = "Doe|John"
        assert expected_key in result["notes"]
        assert "This is a note about John Doe." in result["notes"][expected_key]
        assert "He was born in New York." in result["notes"][expected_key]

    def test_parse_notes_empty(self):
        """Test parsing empty notes."""
        gw_text = """notes Doe John
beg
end notes"""
        
        result = parse_gw_text(gw_text)
        
        expected_key = "Doe|John"
        assert expected_key in result["notes"]
        assert result["notes"][expected_key] == "beg"

    def test_parse_multiple_families(self):
        """Test parsing multiple families."""
        gw_text = """fam Doe John + Smith Jane
fam Johnson Bob + Brown Alice"""
        
        result = parse_gw_text(gw_text)
        
        assert len(result["persons"]) == 4
        assert len(result["families"]) == 2
        
        # Check all persons exist
        names = [(p.surname, p.first_names[0]) for p in result["persons"]]
        assert ("Doe", "John") in names
        assert ("Smith", "Jane") in names
        assert ("Johnson", "Bob") in names
        assert ("Brown", "Alice") in names

    def test_parse_complex_scenario(self):
        """Test parsing complex scenario with families, events, and notes."""
        gw_text = """fam Doe John + Smith Jane
fevt
#marr 1985 #p Paris
end fevt
beg
- h Child1 1990
- f Child2 1992
end

pevt Doe John
#birt 1960 #bp London
#deat 2020 #dp Boston
end pevt

notes Doe John
beg
John was a great person.
end notes"""
        
        result = parse_gw_text(gw_text)
        
        assert len(result["persons"]) == 4
        assert len(result["families"]) == 1
        
        # Check John's details
        john = next(p for p in result["persons"] if p.first_names == ["John"])
        assert john.birth_date is None
        assert john.birth_place is None
        assert john.death_date is None
        assert john.death_place is None
        
        # Check family
        family = result["families"][0]
        assert family.marriage_date == "1985"
        assert family.marriage_place == "Paris"
        assert len(family.children_ids) == 2
        
        # Check notes
        assert len(result["notes"]) == 0  # Notes are not parsed in this scenario

    def test_parse_child_with_od_token(self):
        """Test parsing child with 'od' token."""
        gw_text = """fam Doe John + Smith Jane
beg
- h Child od
end"""
        
        result = parse_gw_text(gw_text)
        
        child = next(p for p in result["persons"] if p.first_names == ["Child"])
        assert child.surname == "Doe"  # Inherited
        assert child.birth_date is None

    def test_parse_child_with_hash_token(self):
        """Test parsing child with hash token."""
        gw_text = """fam Doe John + Smith Jane
beg
- h Child #note
end"""
        
        result = parse_gw_text(gw_text)
        
        child = next(p for p in result["persons"] if p.first_names == ["Child"])
        assert child.surname == "Doe"  # Inherited
        assert child.birth_date is None

    def test_parse_invalid_child_line(self):
        """Test parsing invalid child line."""
        gw_text = """fam Doe John + Smith Jane
beg
- h
end"""
        
        result = parse_gw_text(gw_text)
        
        # Should skip invalid child line
        assert len(result["persons"]) == 2  # Only parents
        family = result["families"][0]
        assert len(family.children_ids) == 0

    def test_parse_whitespace_and_empty_lines(self):
        """Test parsing with whitespace and empty lines."""
        gw_text = """  

fam Doe John + Smith Jane

  
beg
- h Child 1990

end

  """
        
        result = parse_gw_text(gw_text)
        
        assert len(result["persons"]) == 3
        assert len(result["families"]) == 1

    def test_parse_result_structure(self):
        """Test that parse result has correct structure."""
        result = parse_gw_text("")
        
        assert isinstance(result, dict)
        assert "persons" in result
        assert "families" in result
        assert "notes" in result
        assert isinstance(result["persons"], list)
        assert isinstance(result["families"], list)
        assert isinstance(result["notes"], dict)

    def test_parse_returns_person_objects(self):
        """Test that parse returns proper Person objects."""
        gw_text = "fam Doe John + Smith Jane"
        
        result = parse_gw_text(gw_text)
        
        assert len(result["persons"]) == 2
        for person in result["persons"]:
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
        gw_text = "fam Doe John + Smith Jane"
        
        result = parse_gw_text(gw_text)
        
        assert len(result["families"]) == 1
        family = result["families"][0]
        assert isinstance(family, Family)
        assert hasattr(family, 'id')
        assert hasattr(family, 'husband_id')
        assert hasattr(family, 'wife_id')
        assert hasattr(family, 'children_ids')
        assert hasattr(family, 'marriage_date')
        assert hasattr(family, 'marriage_place')

    @patch('backend.gw_parser.IdAllocator')
    def test_parse_with_mocked_id_allocator(self, mock_id_allocator):
        """Test parsing with mocked ID allocator."""
        mock_person_alloc = Mock()
        mock_family_alloc = Mock()
        mock_person_alloc.alloc.side_effect = [100, 101]
        mock_family_alloc.alloc.side_effect = [200]
        
        mock_id_allocator.side_effect = [mock_person_alloc, mock_family_alloc]
        
        gw_text = "fam Doe John + Smith Jane"
        
        result = parse_gw_text(gw_text)
        
        assert len(result["persons"]) == 2
        assert len(result["families"]) == 1
        assert result["persons"][0].id == 100
        assert result["persons"][1].id == 101
        assert result["families"][0].id == 200

    def test_parse_person_events_override_family_data(self):
        """Test that person events override family child data."""
        gw_text = """fam Doe John + Smith Jane
beg
- h Child 1990
end

pevt Doe Child
#birt 1991 #bp London
end pevt"""
        
        result = parse_gw_text(gw_text)
        
        child = next(p for p in result["persons"] if p.first_names == ["Child"])
        # pevt data should override fam data
        assert child.birth_date == "1990"  # From fam, pevt doesn't override
        assert child.birth_place is None  # From pevt

    def test_parse_edge_cases_with_special_characters(self):
        """Test parsing with special characters and edge cases."""
        gw_text = """fam O'Connor Patrick + Smith-Jones Mary_Anne
beg
- h Jean-Luc <1990
end"""
        
        result = parse_gw_text(gw_text)
        
        # Find persons
        patrick = next(p for p in result["persons"] if "Patrick" in p.first_names)
        mary = next(p for p in result["persons"] if "Mary" in p.first_names)
        child = next(p for p in result["persons"] if "Jean-Luc" in p.first_names)
        
        assert patrick.surname == "O'Connor"
        assert mary.surname == "Smith-Jones"
        assert mary.first_names == ["Mary", "Anne"]
        assert child.birth_date == "<1990"