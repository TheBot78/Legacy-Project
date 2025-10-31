import pytest
from backend.gw_parser import parse_gw_text
from backend.models import Person, Family


def test_parse_gw_text_empty_string_returns_empty_lists():
    """Test parsing empty GW text."""
    result = parse_gw_text("")
    persons, families = result["persons"], result["families"]
    assert persons == []
    assert families == []


def test_parse_gw_text_encoding_line_only():
    """Test parsing GW text with only encoding line."""
    gw_text = "encoding: utf-8"
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    assert persons == []
    assert families == []


def test_parse_gw_text_single_person_basic():
    """Test parsing single person with basic information."""
    gw_text = """encoding: utf-8
per 1 John /Doe/ m"""
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(persons) == 1
    assert len(families) == 0
    
    person = persons[0]
    assert person.id == 1
    assert person.first_names == ["John"]
    assert person.surname == "Doe"
    assert person.sex == "m"


def test_parse_gw_text_person_with_birth_info():
    """Test parsing person with birth information."""
    gw_text = """encoding: utf-8
per 1 Jane /Smith/ f 1980 in New York"""
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(persons) == 1
    person = persons[0]
    assert person.first_names == ["Jane"]
    assert person.surname == "Smith"
    assert person.sex == "f"
    assert person.birth_date == "1980"
    assert person.birth_place == "New York"


def test_parse_gw_text_person_with_death_info():
    """Test parsing person with death information."""
    gw_text = """encoding: utf-8
per 1 John /Doe/ m 1950 in London +2020 in Paris"""
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(persons) == 1
    person = persons[0]
    assert person.birth_date == "1950"
    assert person.birth_place == "London"
    assert person.death_date == "2020"
    assert person.death_place == "Paris"


def test_parse_gw_text_person_with_parents():
    """Test parsing person with parent references."""
    gw_text = """encoding: utf-8
per 1 Bob /Smith/ m 2010 fath 2 moth 3"""
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(persons) == 1
    person = persons[0]
    assert person.first_names == ["Bob"]
    assert person.surname == "Smith"
    assert person.father_id == 2
    assert person.mother_id == 3
    assert person.birth_date == "2010"


def test_parse_gw_text_multiple_first_names():
    """Test parsing person with multiple first names."""
    gw_text = """encoding: utf-8
per 1 Jean Pierre /Dupont/ m"""
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(persons) == 1
    person = persons[0]
    assert person.first_names == ["Jean", "Pierre"]
    assert person.surname == "Dupont"


def test_parse_gw_text_family_basic():
    """Test parsing basic family structure."""
    gw_text = """encoding: utf-8
fam 1 husb 2 wife 3"""
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(persons) == 0
    assert len(families) == 1
    
    family = families[0]
    assert family.id == 1
    assert family.husband_id == 2
    assert family.wife_id == 3
    assert family.children_ids == []


def test_parse_gw_text_family_with_children():
    """Test parsing family with children."""
    gw_text = """encoding: utf-8
fam 1 husb 2 wife 3 chil 4 chil 5"""
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(families) == 1
    family = families[0]
    assert family.husband_id == 2
    assert family.wife_id == 3
    assert set(family.children_ids) == {4, 5}


def test_parse_gw_text_family_with_marriage_info():
    """Test parsing family with marriage information."""
    gw_text = """encoding: utf-8
fam 1 husb 2 wife 3 marr 2000 in Paris"""
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(families) == 1
    family = families[0]
    assert family.marriage_date == "2000"
    assert family.marriage_place == "Paris"


def test_parse_gw_text_mixed_persons_and_families():
    """Test parsing mixed persons and families."""
    gw_text = """encoding: utf-8
per 1 John /Doe/ m 1950
per 2 Jane /Smith/ f 1955
fam 1 husb 1 wife 2 marr 1975
per 3 Bob /Doe/ m 1980 fath 1 moth 2"""
    
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(persons) == 3
    assert len(families) == 1
    
    # Check persons
    john = next(p for p in persons if p.first_names == ["John"])
    jane = next(p for p in persons if p.first_names == ["Jane"])
    bob = next(p for p in persons if p.first_names == ["Bob"])
    
    assert john.birth_date == "1950"
    assert jane.birth_date == "1955"
    assert bob.birth_date == "1980"
    assert bob.father_id == 1
    assert bob.mother_id == 2
    
    # Check family
    family = families[0]
    assert family.husband_id == 1
    assert family.wife_id == 2
    assert family.marriage_date == "1975"


def test_parse_gw_text_person_without_sex():
    """Test parsing person without sex specification."""
    gw_text = """encoding: utf-8
per 1 Alex /Taylor/"""
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(persons) == 1
    person = persons[0]
    assert person.first_names == ["Alex"]
    assert person.surname == "Taylor"
    assert person.sex is None


def test_parse_gw_text_family_without_spouse():
    """Test parsing family with missing spouse information."""
    gw_text = """encoding: utf-8
fam 1 husb 1 chil 2"""
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(families) == 1
    family = families[0]
    assert family.husband_id == 1
    assert family.wife_id is None
    assert family.children_ids == [2]


def test_parse_gw_text_ignore_invalid_lines():
    """Test that invalid lines are ignored gracefully."""
    gw_text = """encoding: utf-8
invalid line here
per 1 John /Doe/ m
another invalid line
fam 1 husb 1"""
    
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(persons) == 1
    assert len(families) == 1
    assert persons[0].first_names == ["John"]
    assert families[0].husband_id == 1


def test_parse_gw_text_complex_genealogy():
    """Test parsing a complex genealogy structure."""
    gw_text = """encoding: utf-8
per 1 John /Doe/ m 1950 in London
per 2 Mary /Johnson/ f 1955 in Manchester
per 3 Robert /Doe/ m 1980 in Liverpool fath 1 moth 2
per 4 Sarah /Doe/ f 1982 in Birmingham fath 1 moth 2
fam 1 husb 1 wife 2 chil 3 chil 4 marr 1975 in London
per 5 Emma /Smith/ f 1985
fam 2 husb 3 wife 5 marr 2005 in Manchester
per 6 James /Doe/ m 2010 fath 3 moth 5"""
    
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(persons) == 6
    assert len(families) == 2
    
    # Check first generation
    john = next(p for p in persons if p.first_names == ["John"])
    mary = next(p for p in persons if p.first_names == ["Mary"])
    assert john.birth_place == "London"
    assert mary.birth_place == "Manchester"
    
    # Check second generation
    robert = next(p for p in persons if p.first_names == ["Robert"])
    sarah = next(p for p in persons if p.first_names == ["Sarah"])
    assert robert.father_id == john.id
    assert robert.mother_id == mary.id
    assert sarah.father_id == john.id
    assert sarah.mother_id == mary.id
    
    # Check third generation
    james = next(p for p in persons if p.first_names == ["James"])
    emma = next(p for p in persons if p.first_names == ["Emma"])
    assert james.father_id == robert.id
    assert james.mother_id == emma.id
    
    # Check families
    family1 = next(f for f in families if f.husband_id == john.id)
    family2 = next(f for f in families if f.husband_id == robert.id)
    
    assert family1.wife_id == mary.id
    assert set(family1.children_ids) == {robert.id, sarah.id}
    assert family1.marriage_place == "London"
    
    assert family2.wife_id == emma.id
    assert family2.marriage_place == "Manchester"


def test_parse_gw_text_whitespace_handling():
    """Test that extra whitespace is handled correctly."""
    gw_text = """encoding: utf-8
   per   1   John   /Doe/   m   1950   
   fam   1   husb   1   """
    
    result = parse_gw_text(gw_text)
    persons, families = result["persons"], result["families"]
    
    assert len(persons) == 1
    assert len(families) == 1
    assert persons[0].first_names == ["John"]
    assert persons[0].surname == "Doe"
    assert families[0].husband_id == 1