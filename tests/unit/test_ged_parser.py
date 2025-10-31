import pytest
from backend.ged_parser import parse_ged_text
from backend.models import Person, Family


def test_parse_ged_text_empty_string_returns_empty_lists():
    """Test parsing empty GEDCOM text."""
    persons, families = parse_ged_text("")
    assert persons == []
    assert families == []


def test_parse_ged_text_minimal_header_only():
    """Test parsing GEDCOM with only header."""
    ged_text = """0 HEAD
1 SOUR Test
0 TRLR"""
    persons, families = parse_ged_text(ged_text)
    assert persons == []
    assert families == []


def test_parse_ged_text_single_person_basic_info():
    """Test parsing single person with basic information."""
    ged_text = """0 HEAD
1 SOUR Test
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 TRLR"""
    persons, families = parse_ged_text(ged_text)
    
    assert len(persons) == 1
    assert len(families) == 0
    
    person = persons[0]
    assert person.id == 1
    assert person.first_names == ["John"]
    assert person.surname == "Doe"
    assert person.sex == "m"


def test_parse_ged_text_person_with_birth_death_info():
    """Test parsing person with birth and death information."""
    ged_text = """0 HEAD
1 SOUR Test
0 @I1@ INDI
1 NAME Jane /Smith/
1 SEX F
1 BIRT
2 DATE 1980
2 PLAC New York
1 DEAT
2 DATE 2020
2 PLAC Boston
0 TRLR"""
    persons, families = parse_ged_text(ged_text)
    
    assert len(persons) == 1
    person = persons[0]
    assert person.first_names == ["Jane"]
    assert person.surname == "Smith"
    assert person.sex == "f"
    assert person.birth_date == "1980"
    assert person.birth_place == "New York"
    assert person.death_date == "2020"
    assert person.death_place == "Boston"


def test_parse_ged_text_multiple_first_names():
    """Test parsing person with multiple first names."""
    ged_text = """0 HEAD
1 SOUR Test
0 @I1@ INDI
1 NAME Jean Pierre /Dupont/
1 SEX M
0 TRLR"""
    persons, families = parse_ged_text(ged_text)
    
    assert len(persons) == 1
    person = persons[0]
    assert person.first_names == ["Jean", "Pierre"]
    assert person.surname == "Dupont"


def test_parse_ged_text_family_basic():
    """Test parsing basic family structure."""
    ged_text = """0 HEAD
1 SOUR Test
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
0 TRLR"""
    persons, families = parse_ged_text(ged_text)
    
    assert len(persons) == 2
    assert len(families) == 1
    
    family = families[0]
    assert family.id == 1
    assert family.husband_id == 1
    assert family.wife_id == 2
    assert family.children_ids == []


def test_parse_ged_text_family_with_children():
    """Test parsing family with children."""
    ged_text = """0 HEAD
1 SOUR Test
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
0 @I3@ INDI
1 NAME Bob /Doe/
1 SEX M
0 @I4@ INDI
1 NAME Alice /Doe/
1 SEX F
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
1 CHIL @I4@
0 TRLR"""
    persons, families = parse_ged_text(ged_text)
    
    assert len(persons) == 4
    assert len(families) == 1
    
    family = families[0]
    assert family.husband_id == 1
    assert family.wife_id == 2
    assert set(family.children_ids) == {3, 4}


def test_parse_ged_text_family_with_marriage_info():
    """Test parsing family with marriage information."""
    ged_text = """0 HEAD
1 SOUR Test
0 @I1@ INDI
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
2 PLAC Paris
0 TRLR"""
    persons, families = parse_ged_text(ged_text)
    
    assert len(families) == 1
    family = families[0]
    assert family.marriage_date == "2000"
    assert family.marriage_place == "Paris"


def test_parse_ged_text_person_with_parents():
    """Test parsing person with parent references."""
    ged_text = """0 HEAD
1 SOUR Test
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
0 @I3@ INDI
1 NAME Bob /Doe/
1 SEX M
1 FAMC @F1@
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
0 TRLR"""
    persons, families = parse_ged_text(ged_text)
    
    # Find Bob (child)
    bob = next(p for p in persons if p.first_names == ["Bob"])
    assert bob.father_id == 1  # John
    assert bob.mother_id == 2  # Jane


def test_parse_ged_text_invalid_reference_ignored():
    """Test that invalid references are ignored gracefully."""
    ged_text = """0 HEAD
1 SOUR Test
0 @F1@ FAM
1 HUSB @I999@
1 WIFE @I888@
0 TRLR"""
    persons, families = parse_ged_text(ged_text)
    
    assert len(persons) == 0
    assert len(families) == 1
    family = families[0]
    assert family.husband_id is None
    assert family.wife_id is None


def test_parse_ged_text_complex_genealogy():
    """Test parsing a more complex genealogy structure."""
    ged_text = """0 HEAD
1 SOUR Legacy-Project
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 BIRT
2 DATE 1950
2 PLAC London
0 @I2@ INDI
1 NAME Mary /Johnson/
1 SEX F
1 BIRT
2 DATE 1955
2 PLAC Manchester
0 @I3@ INDI
1 NAME Robert /Doe/
1 SEX M
1 BIRT
2 DATE 1980
2 PLAC Liverpool
1 FAMC @F1@
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
1 MARR
2 DATE 1975
2 PLAC Birmingham
0 TRLR"""
    
    persons, families = parse_ged_text(ged_text)
    
    assert len(persons) == 3
    assert len(families) == 1
    
    # Check persons
    john = next(p for p in persons if p.first_names == ["John"])
    mary = next(p for p in persons if p.first_names == ["Mary"])
    robert = next(p for p in persons if p.first_names == ["Robert"])
    
    assert john.birth_date == "1950"
    assert john.birth_place == "London"
    assert mary.birth_date == "1955"
    assert mary.birth_place == "Manchester"
    assert robert.birth_date == "1980"
    assert robert.birth_place == "Liverpool"
    assert robert.father_id == john.id
    assert robert.mother_id == mary.id
    
    # Check family
    family = families[0]
    assert family.husband_id == john.id
    assert family.wife_id == mary.id
    assert robert.id in family.children_ids
    assert family.marriage_date == "1975"
    assert family.marriage_place == "Birmingham"
