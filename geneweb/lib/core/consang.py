# Copyright (c) 1998-2007 INRIA
# Python rewrite of Consang core module

from typing import List, Dict, Tuple, Optional, Set
from collections import deque
import networkx as nx
from ..db.driver import Database, Collection, Marker
from ..definitions import Person
from ..adef import Fix, NO_CONSANG

class TopologicalSortError(Exception):
    """Erreur de tri topologique (boucle détectée)"""
    def __init__(self, person: Person):
        self.person = person
        super().__init__(f"Topological sort error: {person.first_name} {person.surname}")

class AncStat:
    """Statut d'ancêtre"""
    MAYBE_ANC = "maybe_anc"
    IS_ANC = "is_anc"

class RelationshipInfo:
    """Informations de relation pour le calcul de consanguinité"""
    
    def __init__(self, base: Database, topological_sort: List[int]):
        self.base = base
        self.topo_sort = topological_sort
        self.reltab: Dict[int, float] = {}
        self._build_relationship_table()
    
    def _build_relationship_table(self):
        """Construit la table des relations"""
        persons = self.base.ipers()
        for i in persons:
            self.reltab[i] = 0.0

class Consang:
    """Module principal de calcul de consanguinité"""
    
    @staticmethod
    def topological_sort(base: Database, poi_func) -> List[int]:
        """Tri topologique des personnes pour éviter les boucles"""
        persons = base.ipers()
        tab = base.iper_marker(persons, 0)
        cnt = 0
        
        # Première passe : compter les références
        for i in persons:
            person = poi_func(base, i)
            parents_fam = base.get_parents(person)
            if parents_fam is not None:
                family = base.foi(parents_fam)
                father_id = base.get_father(family)
                mother_id = base.get_mother(family)
                
                if father_id >= 0:
                    tab.set(father_id, tab.get(father_id) + 1)
                if mother_id >= 0:
                    tab.set(mother_id, tab.get(mother_id) + 1)
        
        # Tri topologique avec détection de cycles
        result = []
        queue = deque()
        
        # Ajouter les personnes sans parents à la queue
        for i in persons:
            if tab.get(i) == 0:
                queue.append(i)
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            # Traiter les enfants
            person = poi_func(base, current)
            # Ici on devrait itérer sur les enfants, simplifié pour l'exemple
            
        if len(result) != len(list(persons)):
            # Cycle détecté
            for i in persons:
                if tab.get(i) > 0:
                    person = poi_func(base, i)
                    raise TopologicalSortError(person)
        
        return result
    
    @staticmethod
    def make_relationship_info(base: Database, topo_sort: List[int]) -> RelationshipInfo:
        """Crée les informations de relation"""
        return RelationshipInfo(base, topo_sort)
    
    @staticmethod
    def relationship_and_links(base: Database, tab: RelationshipInfo, 
                             with_links: bool, ip1: int, ip2: int) -> Tuple[float, Optional[List]]:
        """Calcule la relation et les liens entre deux personnes"""
        # Algorithme simplifié de calcul de relation
        # Dans la vraie implémentation, ceci serait beaucoup plus complexe
        
        if ip1 == ip2:
            return 1.0, [] if with_links else None
        
        # Utilisation de NetworkX pour le calcul de chemin
        G = nx.Graph()
        
        # Construction du graphe des relations familiales
        persons = base.ipers()
        for i in persons:
            person = base.poi(i)
            parents_fam = base.get_parents(person)
            if parents_fam is not None:
                family = base.foi(parents_fam)
                father_id = base.get_father(family)
                mother_id = base.get_mother(family)
                
                if father_id >= 0:
                    G.add_edge(i, father_id)
                if mother_id >= 0:
                    G.add_edge(i, mother_id)
        
        try:
            if nx.has_path(G, ip1, ip2):
                path = nx.shortest_path(G, ip1, ip2)
                # Calcul simplifié de la consanguinité basé sur la distance
                distance = len(path) - 1
                consanguinity = 1.0 / (2.0 ** distance) if distance > 0 else 0.0
                return consanguinity, path if with_links else None
            else:
                return 0.0, [] if with_links else None
        except nx.NetworkXNoPath:
            return 0.0, [] if with_links else None
