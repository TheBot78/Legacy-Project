# Copyright (c) 1998-2007 INRIA
# Python rewrite of Geneweb calendar module

from typing import Tuple, Optional
from ..definitions import Calendar, Dmy
from .date import leap_year, nb_days_in_month

def julian_of_gregorian(dmy: Dmy) -> Dmy:
    """Convert Gregorian date to Julian"""
    # Simplified conversion
    day, month, year = dmy.day, dmy.month, dmy.year
    
    # Julian calendar is 13 days behind Gregorian after 1900
    if year >= 1900:
        day -= 13
    elif year >= 1800:
        day -= 12
    elif year >= 1700:
        day -= 11
    else:
        day -= 10
    
    if day <= 0:
        month -= 1
        if month <= 0:
            month = 12
            year -= 1
        day += nb_days_in_month(month, year)
    
    return Dmy(day=day, month=month, year=year, prec=dmy.prec, delta=dmy.delta)

def gregorian_of_julian(dmy: Dmy) -> Dmy:
    """Convert Julian date to Gregorian"""
    # Simplified conversion
    day, month, year = dmy.day, dmy.month, dmy.year
    
    # Add the difference
    if year >= 1900:
        day += 13
    elif year >= 1800:
        day += 12
    elif year >= 1700:
        day += 11
    else:
        day += 10
    
    max_days = nb_days_in_month(month, year)
    if day > max_days:
        day -= max_days
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    return Dmy(day=day, month=month, year=year, prec=dmy.prec, delta=dmy.delta)

def french_of_gregorian(dmy: Dmy) -> Optional[Dmy]:
    """Convert Gregorian to French Revolutionary calendar"""
    # French calendar was used from 1792 to 1805
    if dmy.year < 1792 or dmy.year > 1805:
        return None
    
    # Simplified implementation
    year = dmy.year - 1792
    return Dmy(day=dmy.day, month=dmy.month, year=year, prec=dmy.prec, delta=dmy.delta)

def gregorian_of_french(dmy: Dmy) -> Dmy:
    """Convert French Revolutionary to Gregorian calendar"""
    year = dmy.year + 1792
    return Dmy(day=dmy.day, month=dmy.month, year=year, prec=dmy.prec, delta=dmy.delta)

def hebrew_of_gregorian(dmy: Dmy) -> Dmy:
    """Convert Gregorian to Hebrew calendar"""
    # Simplified implementation - Hebrew year starts around September
    year = dmy.year + 3760
    if dmy.month >= 9:  # Tishrei starts around September
        year += 1
    return Dmy(day=dmy.day, month=dmy.month, year=year, prec=dmy.prec, delta=dmy.delta)

def gregorian_of_hebrew(dmy: Dmy) -> Dmy:
    """Convert Hebrew to Gregorian calendar"""
    year = dmy.year - 3760
    if dmy.month < 7:  # Before Tishrei
        year -= 1
    return Dmy(day=dmy.day, month=dmy.month, year=year, prec=dmy.prec, delta=dmy.delta)
