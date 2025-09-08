# Copyright (c) 1998-2007 INRIA
# Python rewrite of Geneweb mutil module

import re
from typing import Set, List, Dict, Optional, Any
from collections import defaultdict

class StrSet:
    """String set implementation"""
    def __init__(self):
        self._set = set()
    
    def add(self, s: str):
        self._set.add(s)
    
    def remove(self, s: str):
        self._set.discard(s)
    
    def contains(self, s: str) -> bool:
        return s in self._set
    
    def to_list(self) -> List[str]:
        return list(self._set)
    
    def is_empty(self) -> bool:
        return len(self._set) == 0

class StrMap:
    """String map implementation"""
    def __init__(self):
        self._map = {}
    
    def add(self, key: str, value: Any):
        self._map[key] = value
    
    def find(self, key: str) -> Optional[Any]:
        return self._map.get(key)
    
    def remove(self, key: str):
        self._map.pop(key, None)

def start_with(prefix: str, s: str) -> bool:
    """Check if string starts with prefix"""
    return s.startswith(prefix)

def contains(substring: str, s: str) -> bool:
    """Check if string contains substring"""
    return substring in s

def strip_spaces(s: str) -> str:
    """Strip leading and trailing spaces"""
    return s.strip()

def normalize(s: str) -> str:
    """Normalize string for comparison"""
    return s.lower().strip()

def split_on_char(char: str, s: str) -> List[str]:
    """Split string on character"""
    return s.split(char)

def list_iter_first(fn, lst: List[Any]) -> bool:
    """Apply function to first element that satisfies condition"""
    for item in lst:
        if fn(item):
            return True
    return False

def array_to_list_map(fn, arr: List[Any]) -> List[Any]:
    """Map function over array and convert to list"""
    return [fn(x) for x in arr]

def verbose(level: int, msg: str):
    """Print verbose message"""
    if level > 0:
        print(f"[VERBOSE {level}] {msg}")
