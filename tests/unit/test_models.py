import pytest
from pydantic import ValidationError
from backend.models import Person, Family, in_memory_strings


def test_person_model_minimal_creation_succeeds():
    p = Person(id=1, first_names=["John"], surname="Doe")
    assert p.surname == "Doe"
    assert p.first_names == ["John"]
    assert p.id is 1
    assert p.sex is None


def test_person_model_full_creation_succeeds():
    p = Person(
        id=1,
        first_names=["John", "Fitzgerald"],
        surname="Doe",
        sex="m",
        father_id=2,
        mother_id=3,
        birth_date="1990",
        birth_place="New York"
    )
    assert p.id == 1
    assert p.sex == "m"
    assert p.birth_place == "New York"
    assert p.father_id == 2

def test_person_model_missing_surname_raises_validation_error():
    with pytest.raises(TypeError):
        Person(first_names=["John"]) # surname is required

def test_person_model_missing_firstname_raises_validation_error():
     with pytest.raises(TypeError):
        Person(surname="Doe") # first_names is required


