# Copyright (c) 1998-2007 INRIA
# Progress bar utility

import sys
import time

class ProgrBar:
    """Barre de progression"""
    
    _start_time = None
    _last_update = None
    
    @classmethod
    def start(cls):
        """Démarre la barre de progression"""
        cls._start_time = time.time()
        cls._last_update = cls._start_time
        print("[" + " " * 50 + "]", end="", file=sys.stderr)
        print("\r[", end="", file=sys.stderr)
        sys.stderr.flush()
    
    @classmethod
    def run(cls, current: int, total: int):
        """Met à jour la barre de progression"""
        if cls._start_time is None:
            return
        
        now = time.time()
        if now - cls._last_update < 0.1:  # Limite les mises à jour
            return
        
        cls._last_update = now
        progress = min(50, int(50 * current / total)) if total > 0 else 0
        
        print("\r[" + "=" * progress + " " * (50 - progress) + "]", end="", file=sys.stderr)
        sys.stderr.flush()
    
    @classmethod
    def finish(cls):
        """Termine la barre de progression"""
        print("\r[" + "=" * 50 + "] Done\n", file=sys.stderr)
        sys.stderr.flush()
        cls._start_time = None
