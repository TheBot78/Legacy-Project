from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Person:
    id: int
    first_names: List[str]
    surname: str
    sex: Optional[str] = None  # 'M' | 'F' | None
    father_id: Optional[int] = None
    mother_id: Optional[int] = None
    birth_date: Optional[str] = None
    birth_place: Optional[str] = None
    death_date: Optional[str] = None
    death_place: Optional[str] = None


@dataclass
class Family:
    id: int
    husband_id: Optional[int] = None
    wife_id: Optional[int] = None
    children_ids: List[int] = field(default_factory=list)
    marriage_date: Optional[str] = None
    marriage_place: Optional[str] = None


@dataclass
class Database:
    persons: List[Person]
    families: List[Family]


# Simple helpers to build ids consecutively
class IdAllocator:
    def __init__(self, start: int = 0):
        self.next_id = start

    def alloc(self) -> int:
        nid = self.next_id
        self.next_id += 1
        return nid


def in_memory_strings(persons: List[Person],
                      families: List[Family]) -> Dict[str, int]:
    """Collect and deduplicate all strings referenced by persons/families.
    Returns a mapping string -> string_id.
    """
    strings: Dict[str, int] = {}

    def add(s: Optional[str]):
        if s is None:
            return
        if s not in strings:
            strings[s] = len(strings)

    for p in persons:
        add(p.surname)
        for fn in p.first_names:
            add(fn)
        add(p.birth_place)
        add(p.death_place)
        add(p.birth_date)
        add(p.death_date)
        add(p.sex)
    for f in families:
        add(f.marriage_place)
        add(f.marriage_date)
    return strings
