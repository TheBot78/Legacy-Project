import pytest
from calendar_mod import (
    gregorian_of_sdn, sdn_of_gregorian,
    julian_of_sdn, sdn_of_julian,
    french_of_sdn, sdn_of_french,
    hebrew_of_sdn, sdn_of_hebrew,
    gregorian_of_julian, julian_of_gregorian,
    gregorian_of_french, french_of_gregorian,
    gregorian_of_hebrew, hebrew_of_gregorian,
    Date, Sure, OrYear
)

# Données de test équivalentes à data_sure et data_oryear
data_sure = [
    Date(day=1, month=1, year=1900, delta=0, prec=Sure()),
    Date(day=0, month=1, year=1900, delta=0, prec=Sure()),
    Date(day=0, month=0, year=1900, delta=0, prec=Sure()),
]

data_oryear = [
    Date(day=1, month=1, year=1900, delta=0, prec=OrYear(day2=1, month2=1, year2=1901, delta2=0)),
    Date(day=0, month=1, year=1900, delta=0, prec=OrYear(day2=0, month2=1, year2=1901, delta2=0)),
    Date(day=0, month=0, year=1900, delta=0, prec=OrYear(day2=0, month2=0, year2=1901, delta2=0)),
]

def round_trip(of_, to_, data):
    for d in data:
        assert d == of_(to_(d))

@pytest.mark.parametrize("of_, to_", [
    (gregorian_of_sdn, sdn_of_gregorian),
    (julian_of_sdn, sdn_of_julian),
    (french_of_sdn, sdn_of_french),
    (hebrew_of_sdn, sdn_of_hebrew),
])
@pytest.mark.parametrize("d", data_sure)
def test_calendar_sdn_failures(of_, to_, d):
    # Ces tests doivent échouer car les dates incomplètes ne sont pas supportées
    with pytest.raises(Exception):
        assert d == of_(to_(d))

@pytest.mark.parametrize("of_, to_", [
    (gregorian_of_julian, julian_of_gregorian),
    (gregorian_of_french, french_of_gregorian),
    (gregorian_of_hebrew, hebrew_of_gregorian),
])
@pytest.mark.parametrize("d", data_sure + data_oryear)
def test_calendar_gregorian_round_trip(of_, to_, d):
    assert d == of_(to_(d))