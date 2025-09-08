# Copyright (c) 1998-2007 INRIA
# Python rewrite of Geneweb date module

from datetime import datetime, date
from typing import Optional, Tuple
from enum import Enum
from ..definitions import Calendar, Precision, Dmy, Date, CDate

class DateError(Exception):
    pass

def leap_year(year: int) -> bool:
    """Check if year is leap year"""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def nb_days_in_month(month: int, year: int) -> int:
    """Number of days in month"""
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == 2 and leap_year(year):
        return 29
    return days_in_month[month - 1] if 1 <= month <= 12 else 0

def valid_date(dmy: Dmy) -> bool:
    """Check if date is valid"""
    if dmy.year <= 0:
        return False
    if not (1 <= dmy.month <= 12):
        return False
    if not (1 <= dmy.day <= nb_days_in_month(dmy.month, dmy.year)):
        return False
    return True

def compare_date(d1: Date, d2: Date) -> int:
    """Compare two dates (-1, 0, 1)"""
    if d1.dmy is None and d2.dmy is None:
        return 0
    if d1.dmy is None:
        return -1
    if d2.dmy is None:
        return 1
    
    dmy1, dmy2 = d1.dmy, d2.dmy
    if dmy1.year != dmy2.year:
        return -1 if dmy1.year < dmy2.year else 1
    if dmy1.month != dmy2.month:
        return -1 if dmy1.month < dmy2.month else 1
    if dmy1.day != dmy2.day:
        return -1 if dmy1.day < dmy2.day else 1
    return 0

def time_elapsed(d1: Date, d2: Date) -> Tuple[int, int, int]:
    """Calculate time elapsed between dates (years, months, days)"""
    if d1.dmy is None or d2.dmy is None:
        return 0, 0, 0
    
    dmy1, dmy2 = d1.dmy, d2.dmy
    years = dmy2.year - dmy1.year
    months = dmy2.month - dmy1.month
    days = dmy2.day - dmy1.day
    
    if days < 0:
        months -= 1
        days += nb_days_in_month(dmy1.month, dmy1.year)
    
    if months < 0:
        years -= 1
        months += 12
    
    return years, months, days

def date_of_string(s: str) -> Optional[Date]:
    """Parse date from string"""
    try:
        # Simple parsing - can be extended
        parts = s.split('/')
        if len(parts) == 3:
            day, month, year = map(int, parts)
            dmy = Dmy(day=day, month=month, year=year, prec=Precision.SURE, delta=0)
            return Date(dmy=dmy)
        return None
    except ValueError:
        return None

def string_of_date(d: Date) -> str:
    """Convert date to string"""
    if d.text:
        return d.text
    if d.dmy:
        return f"{d.dmy.day:02d}/{d.dmy.month:02d}/{d.dmy.year}"
    return ""

def code_french_year(year: int) -> str:
    """Convert year to French revolutionary calendar"""
    # Simplified implementation
    return str(year - 1792)

def decode_french_year(s: str) -> int:
    """Convert French revolutionary year to Gregorian"""
    try:
        return int(s) + 1792
    except ValueError:
        return 0
