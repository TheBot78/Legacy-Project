import pytest
from backend.name_utils import strip_accents, crush_name, ngrams

# Tests for strip_accents
def test_strip_accents_simple_returns_unmodified():
    assert strip_accents("Hello") == "Hello"

def test_strip_accents_removes_common_accents():
    assert strip_accents("François-René") == "Francois-Rene"
    
def test_strip_accents_handles_various_diacritics():
    assert strip_accents("åÅçÇéÉèÈêÊ") == "aAcCeEeEeE"

# Tests for crush_name
def test_crush_name_standard_lowercases_and_strips():
    # Arrange
    input_text = "Jean-Pierre (Test) de la Rivière"
    expected = "jean pierre test de la riviere"
    # Act & Assert
    assert crush_name(input_text) == expected
    
def test_crush_name_removes_all_punctuation():
    assert crush_name("Test,./;'[]<>?:{}|!@#$%^&*()_+-=") == "test"

def test_crush_name_collapses_whitespace():
    assert crush_name("  Extra   Spaces  ") == "extra spaces"

def test_crush_name_handles_empty_string_returns_empty():
    assert crush_name("") == ""
    
def test_crush_name_handles_only_punctuation_returns_empty():
    assert crush_name("...()[]-") == ""

def test_ngrams_string_shorter_than_n_returns_string():
    assert ngrams("hi", 3) == ["hi"]
    
def test_ngrams_string_equals_n_returns_string():
    assert ngrams("hey", 3) == ["hey"]

def test_ngrams_string_longer_than_n_returns_correct_ngrams():
    assert ngrams("hello", 3) == ["hel", "ell", "llo"]
