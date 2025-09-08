# Copyright (c) 1998-2007 INRIA
# Python rewrite of Adef module

from typing import Union, Optional
import math

class Fix:
    """Fixed point arithmetic for consanguinity"""
    
    def __init__(self, value: Union[int, float]):
        if isinstance(value, float):
            self._value = int((value * 1000000.0) + 0.5)
        else:
            self._value = value
    
    @classmethod
    def from_float(cls, x: float) -> 'Fix':
        return cls(x)
    
    @classmethod
    def from_int(cls, x: int) -> 'Fix':
        return cls.__new__(cls)
        instance = cls.__new__(cls)
        instance._value = x
        return instance
    
    def to_float(self) -> float:
        return float(self._value) / 1000000.0
    
    def to_int(self) -> int:
        return self._value
    
    def __eq__(self, other):
        if isinstance(other, Fix):
            return self._value == other._value
        return False
    
    def __lt__(self, other):
        if isinstance(other, Fix):
            return self._value < other._value
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, Fix):
            return self._value > other._value
        return NotImplemented
    
    def __repr__(self):
        return f"Fix({self.to_float()})"

# Constante pour "pas de consanguinité calculée"
NO_CONSANG = Fix.from_int(-1)

def fix_of_float(x: float) -> Fix:
    """Convertit un float en Fix"""
    return Fix.from_float(x)

def float_of_fix(x: Fix) -> float:
    """Convertit un Fix en float"""
    return x.to_float()
