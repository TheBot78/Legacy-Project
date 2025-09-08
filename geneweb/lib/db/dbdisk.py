# Copyright (c) 2006-2007 INRIA
# Python rewrite of Geneweb dbdisk module

from typing import Optional, List, Dict, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum
import os
import pickle
from ..definitions import Person, Family, CDate

class Perm(Enum):
    RDONLY = "readonly"
    RDRW = "readwrite"

@dataclass
class RecordAccess:
    """Generic record access for database arrays"""
    def __init__(self, filename: str, perm: Perm):
        self.filename = filename
        self.perm = perm
        self._array = None
        self._patches = {}
        self._pending_patches = {}
        self.len = 0
    
    def load_array(self):
        """Load array into memory"""
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                self._array = pickle.load(f)
                self.len = len(self._array)
    
    def get(self, index: int) -> Any:
        """Get element at index"""
        # Check pending patches first
        if index in self._pending_patches:
            return self._pending_patches[index]
        
        # Check committed patches
        if index in self._patches:
            return self._patches[index]
        
        # Check loaded array
        if self._array and 0 <= index < len(self._array):
            return self._array[index]
        
        return None
    
    def get_nopending(self, index: int) -> Any:
        """Get element without considering pending patches"""
        if index in self._patches:
            return self._patches[index]
        
        if self._array and 0 <= index < len(self._array):
            return self._array[index]
        
        return None
    
    def set(self, index: int, value: Any):
        """Set element (pending patch)"""
        self._pending_patches[index] = value
    
    def commit_patches(self):
        """Commit pending patches"""
        self._patches.update(self._pending_patches)
        self._pending_patches.clear()
    
    def output_array(self, output_file: str):
        """Save array to file"""
        if self._array:
            # Apply patches
            final_array = self._array.copy()
            for index, value in self._patches.items():
                if index < len(final_array):
                    final_array[index] = value
            
            with open(output_file, 'wb') as f:
                pickle.dump(final_array, f)
    
    def clear_array(self):
        """Clear array from memory"""
        self._array = None

@dataclass
class StringPersonIndex:
    """Index for person names"""
    def __init__(self):
        self._index: Dict[str, List[int]] = {}
    
    def find(self, name_id: int) -> List[int]:
        """Find person IDs with given name ID"""
        return self._index.get(str(name_id), [])
    
    def cursor(self, name: str) -> int:
        """Get name ID or next alphabetical"""
        # Simplified implementation
        return hash(name.lower()) % 10000
    
    def next(self, name_id: int) -> int:
        """Get next name ID"""
        return name_id + 1

@dataclass
class VisibleRecordAccess:
    """Access control for visible records"""
    def __init__(self):
        self._visible = {}
    
    def v_write(self):
        """Write visibility data"""
        pass
    
    def v_get(self, person_filter: Callable, index: int) -> bool:
        """Check if record is visible"""
        return self._visible.get(index, True)

@dataclass
class BaseData:
    """Database data structure"""
    def __init__(self, bdir: str, perm: Perm = Perm.RDONLY):
        self.bdir = bdir
        self.perm = perm
        
        # Initialize record access objects
        self.persons = RecordAccess(os.path.join(bdir, "persons.dat"), perm)
        self.ascends = RecordAccess(os.path.join(bdir, "ascends.dat"), perm)
        self.unions = RecordAccess(os.path.join(bdir, "unions.dat"), perm)
        self.families = RecordAccess(os.path.join(bdir, "families.dat"), perm)
        self.couples = RecordAccess(os.path.join(bdir, "couples.dat"), perm)
        self.descends = RecordAccess(os.path.join(bdir, "descends.dat"), perm)
        self.strings = RecordAccess(os.path.join(bdir, "strings.dat"), perm)
        
        self.visible = VisibleRecordAccess()
        self.particles_txt = []
        self.bnotes = {}
        
        # Load data
        self._load_base()
    
    def _load_base(self):
        """Load base data"""
        for record in [self.persons, self.ascends, self.unions, self.families, 
                      self.couples, self.descends, self.strings]:
            record.load_array()

@dataclass
class BaseFunc:
    """Database functions"""
    def __init__(self, data: BaseData):
        self.data = data
        self._person_index = {}
        self._name_index = StringPersonIndex()
    
    def person_of_key(self, first_name: str, surname: str, occ: int) -> Optional[int]:
        """Find person by key"""
        key = f"{first_name.lower()}#{surname.lower()}#{occ}"
        return self._person_index.get(key)
    
    def persons_of_name(self, name: str) -> List[int]:
        """Find persons by name"""
        name_id = self._name_index.cursor(name)
        return self._name_index.find(name_id)
    
    def strings_of_fsname(self, name: str) -> List[int]:
        """Find string IDs of first/surname"""
        # Simplified implementation
        return [hash(name.lower()) % 1000]
    
    def spi_find(self, name_id: int) -> List[int]:
        """String person index find"""
        return self._name_index.find(name_id)
    
    def spi_first(self, name: str) -> int:
        """First occurrence in string person index"""
        return self._name_index.cursor(name)
    
    def spi_next(self, name_id: int, after_name_id: int) -> int:
        """Next occurrence in string person index"""
        return self._name_index.next(after_name_id)
    
    def commit_patches(self):
        """Commit all pending patches"""
        self.data.persons.commit_patches()
        self.data.families.commit_patches()
        self.data.ascends.commit_patches()
        self.data.unions.commit_patches()
        self.data.couples.commit_patches()
        self.data.descends.commit_patches()
        self.data.strings.commit_patches()
    
    def cleanup(self):
        """Cleanup database"""
        for record in [self.data.persons, self.data.ascends, self.data.unions,
                      self.data.families, self.data.couples, self.data.descends, 
                      self.data.strings]:
            record.clear_array()

@dataclass
class Base:
    """Main database class"""
    def __init__(self, bdir: str, perm: Perm = Perm.RDONLY):
        self.data = BaseData(bdir, perm)
        self.func = BaseFunc(self.data)
    
    def close_base(self):
        """Close database"""
        self.func.cleanup()
    
    def sync(self):
        """Synchronize database"""
        self.func.commit_patches()

# Utility functions
def open_base(bdir: str, perm: Perm = Perm.RDONLY) -> Base:
    """Open database"""
    return Base(bdir, perm)

def close_base(base: Base):
    """Close database"""
    base.close_base()

def sync_base(base: Base):
    """Sync database"""
    base.sync()
