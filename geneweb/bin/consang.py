#!/usr/bin/env python3
# Copyright (c) 1998-2007 INRIA
# Python rewrite of Geneweb consang application

import sys
import os
import argparse
import signal
from pathlib import Path

# Ajout du chemin pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.db.driver import Database, with_database
from lib.core.consang_all import ConsangAll
from lib.core.consang import TopologicalSortError
from lib.db.gutil import Gutil
from lib.util.lock import Lock, Mutil, Secure

class ConsangApp:
    """Application de calcul de consanguinité"""
    
    def __init__(self):
        self.fname = ""
        self.scratch = False
        self.verbosity = 2
        self.fast = False
        self.save_mem = False
        self.no_lock = False
    
    def setup_args(self) -> argparse.ArgumentParser:
        """Configure les arguments de ligne de commande"""
        parser = argparse.ArgumentParser(
            description="Geneweb consanguinity calculator",
            prog="consang"
        )
        
        parser.add_argument(
            "-q", "--quiet", 
            action="store_const", 
            const=1, 
            dest="verbosity",
            help="quiet mode"
        )
        
        parser.add_argument(
            "-qq", "--very-quiet", 
            action="store_const", 
            const=0, 
            dest="verbosity",
            help="very quiet mode"
        )
        
        parser.add_argument(
            "-fast", "--fast", 
            action="store_true",
            help="faster, but use more memory"
        )
        
        parser.add_argument(
            "-scratch", "--scratch", 
            action="store_true",
            help="from scratch"
        )
        
        parser.add_argument(
            "-mem", "--save-memory", 
            action="store_true",
            help="Save memory, but slower when rewriting database"
        )
        
        parser.add_argument(
            "-nolock", "--no-lock", 
            action="store_true",
            help="do not lock database"
        )
        
        parser.add_argument(
            "database", 
            help="database file name"
        )
        
        return parser
    
    def run(self):
        """Exécute l'application"""
        parser = self.setup_args()
        args = parser.parse_args()
        
        # Configuration
        self.fname = args.database
        self.scratch = args.scratch
        self.verbosity = getattr(args, 'verbosity', 2)
        self.fast = args.fast
        self.save_mem = args.save_memory
        self.no_lock = args.no_lock
        
        if not self.fname:
            print("Missing file name", file=sys.stderr)
            print("Use option --help for usage", file=sys.stderr)
            sys.exit(2)
        
        if self.verbosity == 0:
            Mutil.verbose = False
        
        # Configuration de sécurité
        Secure.set_base_dir(os.path.dirname(self.fname))
        
        # Configuration du verrou
        Lock.no_lock_flag = self.no_lock
        
        # Gestion du verrou
        lock_file = Mutil.lock_file(self.fname)
        
        def on_exception(exn, bt):
            print(f"Error: {exn}", file=sys.stderr)
            if bt:
                print(f"Backtrace: {bt}", file=sys.stderr)
            sys.exit(2)
        
        # Contrôle avec verrou
        with Lock.control(on_exn=on_exception, wait=True, lock_file=lock_file):
            self._process_database()
    
    def _process_database(self):
        """Traite la base de données"""
        with with_database(self.fname) as base:
            if self.fast:
                # Chargement rapide en mémoire
                base.load_persons_array()
                base.load_families_array()
                base.load_ascends_array()
                base.load_unions_array()
                base.load_couples_array()
                base.load_descends_array()
                base.load_strings_array()
            
            try:
                # Activation de l'interruption par Ctrl+C
                signal.signal(signal.SIGINT, signal.default_int_handler)
                
                # Calcul de la consanguinité
                if ConsangAll.compute(base, self.scratch, verbosity=self.verbosity):
                    base.sync()
                    
            except TopologicalSortError as e:
                person = e.person
                designation = Gutil.designation(base, person)
                print(f"\nError: loop in database, {designation} is his/her own ancestor.")
                sys.stdout.flush()
                sys.exit(2)
            except KeyboardInterrupt:
                print("\nInterrupted by user", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"\nUnexpected error: {e}", file=sys.stderr)
                sys.exit(2)

def main():
    """Point d'entrée principal"""
    app = ConsangApp()
    app.run()

if __name__ == "__main__":
    main()
