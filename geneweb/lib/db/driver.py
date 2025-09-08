# Copyright (c) 1998-2007 INRIA
# Python rewrite of Database driver

import os
import pickle
import threading
from typing import Dict, List, Optional, Any, Iterator, Callable
from contextlib import contextmanager
from ..definitions import Person, Family, Fix
from ..adef import NO_CONSANG

class DatabaseError(Exception):
    pass

class Collection:
    """Collection générique pour les données"""
    
    def __init__(self, data: List[Any] = None):
        self._data = data or []
        self._lock = threading.RLock()
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __getitem__(self, index: int) -> Any:
        with self._lock:
            return self._data[index]
    
    def __setitem__(self, index: int, value: Any):
        with self._lock:
            self._data[index] = value
    
    def append(self, item: Any):
        with self._lock:
            self._data.append(item)
    
    def __iter__(self) -> Iterator[int]:
        return iter(range(len(self._data)))
    
    def iter_collection(self) -> Iterator[int]:
        return self.__iter__()

class Marker:
    """Marqueur pour les algorithmes"""
    
    def __init__(self, size: int, default_value: Any = None):
        self._data = [default_value] * size
        self._lock = threading.RLock()
    
    def get(self, index: int) -> Any:
        with self._lock:
            return self._data[index]
    
    def set(self, index: int, value: Any):
        with self._lock:
            self._data[index] = value
    
    @classmethod
    def make(cls, size: int, default_value: Any = None) -> 'Marker':
        return cls(size, default_value)

class Database:
    """Base de données principale"""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.persons: Collection[Person] = Collection()
        self.families: Collection[Family] = Collection()
        self.strings: Dict[str, int] = {}
        self.patches: List[Any] = []
        self._lock = threading.RLock()
        self._loaded_arrays = set()
        
        # Chargement des données
        self._load_base()
    
    def _load_base(self):
        """Charge la base depuis le disque"""
        persons_file = os.path.join(self.base_dir, "persons.pkl")
        families_file = os.path.join(self.base_dir, "families.pkl")
        
        if os.path.exists(persons_file):
            with open(persons_file, 'rb') as f:
                self.persons._data = pickle.load(f)
        
        if os.path.exists(families_file):
            with open(families_file, 'rb') as f:
                self.families._data = pickle.load(f)
    
    def save(self):
        """Sauvegarde la base sur le disque"""
        os.makedirs(self.base_dir, exist_ok=True)
        
        persons_file = os.path.join(self.base_dir, "persons.pkl")
        families_file = os.path.join(self.base_dir, "families.pkl")
        
        with open(persons_file, 'wb') as f:
            pickle.dump(self.persons._data, f)
        
        with open(families_file, 'wb') as f:
            pickle.dump(self.families._data, f)
    
    def ipers(self) -> Collection:
        """Retourne la collection des personnes"""
        return Collection(list(range(len(self.persons))))
    
    def ifams(self) -> Collection:
        """Retourne la collection des familles"""
        return Collection(list(range(len(self.families))))
    
    def poi(self, index: int) -> Person:
        """Person of index"""
        return self.persons[index]
    
    def foi(self, index: int) -> Family:
        """Family of index"""
        return self.families[index]
    
    def get_parents(self, person: Person) -> Optional[int]:
        """Obtient l'index de la famille des parents"""
        # Implémentation simplifiée
        return getattr(person, 'parents_family', None)
    
    def get_consang(self, person: Person) -> Fix:
        """Obtient la consanguinité d'une personne"""
        return getattr(person, 'consang', NO_CONSANG)
    
    def get_father(self, family: Family) -> int:
        """Obtient l'index du père"""
        return getattr(family, 'father_id', -1)
    
    def get_mother(self, family: Family) -> int:
        """Obtient l'index de la mère"""
        return getattr(family, 'mother_id', -1)
    
    def patch_ascend(self, person_id: int, ascend_data: Any):
        """Applique un patch aux données d'ascendance"""
        with self._lock:
            self.patches.append(('ascend', person_id, ascend_data))
    
    def commit_patches(self):
        """Applique tous les patches en attente"""
        with self._lock:
            for patch_type, person_id, data in self.patches:
                if patch_type == 'ascend':
                    person = self.persons[person_id]
                    if hasattr(data, 'consang'):
                        person.consang = data.consang
            self.patches.clear()
            self.save()
    
    def sync(self):
        """Synchronise la base"""
        self.save()
    
    def load_persons_array(self):
        """Charge le tableau des personnes en mémoire"""
        self._loaded_arrays.add('persons')
    
    def load_families_array(self):
        """Charge le tableau des familles en mémoire"""
        self._loaded_arrays.add('families')
    
    def load_ascends_array(self):
        """Charge le tableau des ascendances en mémoire"""
        self._loaded_arrays.add('ascends')
    
    def load_unions_array(self):
        """Charge le tableau des unions en mémoire"""
        self._loaded_arrays.add('unions')
    
    def load_couples_array(self):
        """Charge le tableau des couples en mémoire"""
        self._loaded_arrays.add('couples')
    
    def load_descends_array(self):
        """Charge le tableau des descendants en mémoire"""
        self._loaded_arrays.add('descends')
    
    def load_strings_array(self):
        """Charge le tableau des chaînes en mémoire"""
        self._loaded_arrays.add('strings')
    
    def iper_marker(self, collection: Collection, default_value: Any = None) -> Marker:
        """Crée un marqueur pour les personnes"""
        return Marker(len(collection), default_value)
    
    def ifam_marker(self, collection: Collection, default_value: Any = None) -> Marker:
        """Crée un marqueur pour les familles"""
        return Marker(len(collection), default_value)
    
    def gen_ascend_of_person(self, person: Person) -> Any:
        """Génère les données d'ascendance d'une personne"""
        class AscendData:
            def __init__(self):
                self.consang = getattr(person, 'consang', NO_CONSANG)
        return AscendData()

# Fonctions globales du driver
@contextmanager
def with_database(filename: str):
    """Context manager pour ouvrir une base de données"""
    base_dir = os.path.dirname(filename) or "."
    db = Database(base_dir)
    try:
        yield db
    finally:
        db.save()

# Aliases pour compatibilité
Driver = type('Driver', (), {
    'with_database': staticmethod(with_database),
    'ipers': lambda db: db.ipers(),
    'ifams': lambda db: db.ifams(),
    'poi': lambda db, i: db.poi(i),
    'foi': lambda db, i: db.foi(i),
    'get_parents': lambda db, p: db.get_parents(p),
    'get_consang': lambda db, p: db.get_consang(p),
    'get_father': lambda db, f: db.get_father(f),
    'get_mother': lambda db, f: db.get_mother(f),
    'patch_ascend': lambda db, i, d: db.patch_ascend(i, d),
    'commit_patches': lambda db: db.commit_patches(),
    'sync': lambda db: db.sync(),
    'load_persons_array': lambda db: db.load_persons_array(),
    'load_families_array': lambda db: db.load_families_array(),
    'load_ascends_array': lambda db: db.load_ascends_array(),
    'load_unions_array': lambda db: db.load_unions_array(),
    'load_couples_array': lambda db: db.load_couples_array(),
    'load_descends_array': lambda db: db.load_descends_array(),
    'load_strings_array': lambda db: db.load_strings_array(),
    'iper_marker': lambda db, c, d=None: db.iper_marker(c, d),
    'ifam_marker': lambda db, c, d=None: db.ifam_marker(c, d),
    'gen_ascend_of_person': lambda db, p: db.gen_ascend_of_person(p),
})
