from backend.name_utils import crush_name


def test_crush_name_standard_strips_punctuation_and_accents():
    """
    Tests the crush_name function with a complex string.
    """
    # Arrange
    input_text = "Jean-Pierre (Test) de la Rivière"
    expected_output = "jean pierre test de la riviere"

    # Act
    result = crush_name(input_text)

    # Assert
    assert result == expected_output


def test_crush_name_empty_string_returns_empty():
    """
    Tests crush_name with an empty string.
    """
    assert crush_name("") == ""


def test_crush_name_with_numbers_keeps_numbers():
    """
    Tests that numbers are preserved.
    """
    assert crush_name("Louis 14") == "louis 14"
