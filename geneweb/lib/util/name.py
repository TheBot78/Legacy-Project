# Copyright (c) 1998-2007 INRIA
# Python rewrite of Geneweb name module

import re
import unicodedata
from typing import List, Tuple

# Forbidden characters in names
FORBIDDEN_CHARS = [':', '@', '#', '=', '$']

def unaccent_utf_8(lower: bool, s: str, i: int = 0) -> Tuple[str, int]:
    """Remove accents from UTF-8 string"""
    normalized = unicodedata.normalize('NFD', s[i:])
    unaccented = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    if lower:
        unaccented = unaccented.lower()
    return unaccented, len(unaccented)

def lower(s: str) -> str:
    """Convert string to lowercase with accent removal"""
    result, _ = unaccent_utf_8(True, s)
    return result

def abbrev(s: str) -> str:
    """Create abbreviation of name"""
    if not s:
        return ""
    words = s.split()
    if len(words) == 1:
        return s[:1].upper() + "."
    return "".join(word[:1].upper() + "." for word in words)

def strip_c(s: str, c: str) -> str:
    """Strip character from both ends"""
    return s.strip(c)

def purge(s: str) -> str:
    """Remove forbidden characters"""
    result = s
    for char in FORBIDDEN_CHARS:
        result = result.replace(char, "")
    return result

def crush_ml(s: str) -> str:
    """Crush multiple spaces and normalize"""
    return re.sub(r'\s+', ' ', s.strip())

def next_chars_if_equiv(s1: str, s2: str, i1: int, i2: int) -> Tuple[int, int]:
    """Find next equivalent characters"""
    while i1 < len(s1) and i2 < len(s2):
        if s1[i1].lower() == s2[i2].lower():
            return i1 + 1, i2 + 1
        i1 += 1
        i2 += 1
    return i1, i2

def name_equiv(s1: str, s2: str) -> bool:
    """Check if two names are equivalent"""
    n1 = lower(s1)
    n2 = lower(s2)
    return n1 == n2

def firstname_equiv(s1: str, s2: str) -> bool:
    """Check if two first names are equivalent"""
    return name_equiv(s1, s2)

def surname_equiv(s1: str, s2: str) -> bool:
    """Check if two surnames are equivalent"""
    return name_equiv(s1, s2)
