# Copyright (c) 1998-2007 INRIA
# Python rewrite of ConsangAll module

from typing import Optional, Callable, Tuple, List
import sys
from ..db.driver import Database, Collection, Marker
from ..definitions import Person
from ..adef import Fix, NO_CONSANG, fix_of_float
from .consang import Consang, RelationshipInfo
from ..util.progress_bar import ProgrBar
from ..db.gutil import Gutil

class ConsangAll:
    """Calcul de consanguinité pour toute la base"""
    
    @staticmethod
    def relationship(base: Database, tab: RelationshipInfo, ip1: int, ip2: int) -> float:
        """Calcule la relation entre deux personnes"""
        result = Consang.relationship_and_links(base, tab, False, ip1, ip2)
        return result[0]
    
    @staticmethod
    def trace(verbosity: int, cnt: int, max_cnt: int):
        """Affiche le progrès du calcul"""
        if verbosity >= 2:
            print(f"\r{cnt:7d}", end="", file=sys.stderr)
            sys.stderr.flush()
        elif verbosity >= 1:
            ProgrBar.run(max_cnt - cnt, max_cnt)
    
    @staticmethod
    def consang_array(base: Database) -> Tuple[Callable, Callable, Callable, List[bool]]:
        """Crée les fonctions d'accès pour la consanguinité"""
        patched = [False]
        
        def fget(i: int) -> Optional[int]:
            """Obtient les parents d'une personne"""
            person = base.poi(i)
            return base.get_parents(person)
        
        def cget(i: int) -> Fix:
            """Obtient la consanguinité d'une personne"""
            person = base.poi(i)
            return base.get_consang(person)
        
        def cset(i: int, v: Fix):
            """Définit la consanguinité d'une personne"""
            patched[0] = True
            person = base.poi(i)
            ascend = base.gen_ascend_of_person(person)
            ascend.consang = v
            base.patch_ascend(i, ascend)
        
        return fget, cget, cset, patched
    
    @staticmethod
    def compute(base: Database, from_scratch: bool, verbosity: int = 2) -> bool:
        """Calcule la consanguinité pour toutes les personnes de la base"""
        # Chargement des données nécessaires
        base.load_ascends_array()
        base.load_couples_array()
        
        fget, cget, cset, patched = ConsangAll.consang_array(base)
        
        try:
            # Tri topologique et création de la table de relations
            ts = Consang.topological_sort(base, lambda b, i: b.poi(i))
            tab = Consang.make_relationship_info(base, ts)
            
            persons = base.ipers()
            families = base.ifams()
            consang_tab = base.ifam_marker(families, NO_CONSANG)
            
            cnt = [0]
            
            # Initialisation
            for i in persons:
                if from_scratch:
                    cset(i, NO_CONSANG)
                    cnt[0] += 1
                else:
                    cg = cget(i)
                    ifam = fget(i)
                    if ifam is not None:
                        consang_tab.set(ifam, cg)
                    if cg == NO_CONSANG:
                        cnt[0] += 1
            
            max_cnt = cnt[0]
            most = [None]
            
            if verbosity >= 1:
                print(f"To do: {max_cnt} persons", file=sys.stderr)
            
            if max_cnt != 0:
                if verbosity >= 2:
                    print("Computing consanguinity...", end="", file=sys.stderr)
                    sys.stderr.flush()
                elif verbosity >= 1:
                    ProgrBar.start()
            
            # Boucle principale de calcul
            running = True
            while running:
                running = False
                
                for i in persons:
                    if cget(i) == NO_CONSANG:
                        ifam = fget(i)
                        
                        if ifam is not None:
                            pconsang = consang_tab.get(ifam)
                            
                            if pconsang == NO_CONSANG:
                                family = base.foi(ifam)
                                ifath = base.get_father(family)
                                imoth = base.get_mother(family)
                                
                                if (cget(ifath) != NO_CONSANG and 
                                    cget(imoth) != NO_CONSANG):
                                    
                                    consang = ConsangAll.relationship(base, tab, ifath, imoth)
                                    ConsangAll.trace(verbosity, cnt[0], max_cnt)
                                    cnt[0] -= 1
                                    
                                    cg = fix_of_float(consang)
                                    cset(i, cg)
                                    consang_tab.set(ifam, cg)
                                    
                                    if verbosity >= 2:
                                        if (most[0] is None or cg > cget(most[0])):
                                            person = base.poi(i)
                                            designation = Gutil.designation(base, person)
                                            print(f"\nMax consanguinity {consang:.6f} for {designation}... ", 
                                                  end="", file=sys.stderr)
                                            sys.stderr.flush()
                                            most[0] = i
                                else:
                                    running = True
                            else:
                                ConsangAll.trace(verbosity, cnt[0], max_cnt)
                                cnt[0] -= 1
                                cset(i, pconsang)
                        else:
                            ConsangAll.trace(verbosity, cnt[0], max_cnt)
                            cnt[0] -= 1
                            cset(i, fix_of_float(0.0))
            
            if max_cnt != 0:
                if verbosity >= 2:
                    print(" done   ", file=sys.stderr)
                    sys.stderr.flush()
                elif verbosity >= 1:
                    ProgrBar.finish()
                    
        except KeyboardInterrupt:
            if verbosity > 0:
                print("", file=sys.stderr)
                sys.stderr.flush()
        
        if patched[0]:
            base.commit_patches()
        
        return patched[0]
