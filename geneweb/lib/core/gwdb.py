# Copyright (c) 1998-2007 INRIA
# Python rewrite of Geneweb gwdb module

from typing import Optional, List, Dict, Any, Union
from ..definitions import Person, Family, Sex, Access, CDate
from ..db.dbdisk import Base

class Database:
    """Main database interface"""
    
    def __init__(self, base: Base):
        self.base = base
    
    # Person access
    def get_person(self, ip: int) -> Optional[Person]:
        """Get person by index"""
        return self.base.data.persons.get(ip)
    
    def set_person(self, ip: int, person: Person):
        """Set person at index"""
        self.base.data.persons.set(ip, person)
    
    def nb_of_persons(self) -> int:
        """Number of persons"""
        return self.base.data.persons.len
    
    # Family access
    def get_family(self, ifam: int) -> Optional[Family]:
        """Get family by index"""
        return self.base.data.families.get(ifam)
    
    def set_family(self, ifam: int, family: Family):
        """Set family at index"""
        self.base.data.families.set(ifam, family)
    
    def nb_of_families(self) -> int:
        """Number of families"""
        return self.base.data.families.len
    
    # String access
    def get_string(self, istr: int) -> str:
        """Get string by index"""
        return self.base.data.strings.get(istr) or ""
    
    def set_string(self, istr: int, s: str):
        """Set string at index"""
        self.base.data.strings.set(istr, s)
    
    # Person search
    def person_of_key(self, first_name: str, surname: str, occ: int) -> Optional[int]:
        """Find person by key"""
        return self.base.func.person_of_key(first_name, surname, occ)
    
    def persons_of_name(self, name: str) -> List[int]:
        """Find persons by name"""
        return self.base.func.persons_of_name(name)
    
    # Utility functions
    def get_first_name(self, person: Person) -> str:
        """Get person's first name"""
        return person.first_name
    
    def get_surname(self, person: Person) -> str:
        """Get person's surname"""
        return person.surname
    
    def get_occ(self, person: Person) -> int:
        """Get person's occurrence number"""
        return person.occ
    
    def get_sex(self, person: Person) -> Sex:
        """Get person's sex"""
        return person.sex
    
    def get_access(self, person: Person) -> Access:
        """Get person's access level"""
        return person.access
    
    def get_birth(self, person: Person) -> Optional[CDate]:
        """Get person's birth date"""
        return person.birth
    
    def get_death(self, person: Person):
        """Get person's death info"""
        return person.death
    
    def get_parents(self, ip: int) -> Optional[int]:
        """Get person's parents family"""
        ascend = self.base.data.ascends.get(ip)
        return ascend.parents if ascend else None
    
    def get_family_list(self, ip: int) -> List[int]:
        """Get person's family list"""
        union = self.base.data.unions.get(ip)
        return union.families if union else []
    
    def get_father(self, ifam: int) -> Optional[int]:
        """Get family's father"""
        couple = self.base.data.couples.get(ifam)
        return couple.father if couple else None
    
    def get_mother(self, ifam: int) -> Optional[int]:
        """Get family's mother"""
        couple = self.base.data.couples.get(ifam)
        return couple.mother if couple else None
    
    def get_children(self, ifam: int) -> List[int]:
        """Get family's children"""
        descend = self.base.data.descends.get(ifam)
        return descend.children if descend else []
    
    def commit_patches(self):
        """Commit all changes"""
        self.base.func.commit_patches()
    
    def close(self):
        """Close database"""
        self.base.close_base()

# Utility functions
def open_database(bdir: str) -> Database:
    """Open database"""
    from ..db.dbdisk import open_base, Perm
    base = open_base(bdir, Perm.RDRW)
    return Database(base)

def poi(db: Database, ip: int) -> Optional[Person]:
    """Person of index"""
    return db.get_person(ip)

def foi(db: Database, ifam: int) -> Optional[Family]:
    """Family of index"""
    return db.get_family(ifam)

def sou(db: Database, istr: int) -> str:
    """String of index"""
    return db.get_string(istr)
