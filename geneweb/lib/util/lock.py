# Copyright (c) 1998-2007 INRIA
# File locking utilities

import os
import time
import platform
from contextlib import contextmanager
from typing import Callable, Optional

# Import platform-specific modules
try:
    import fcntl  # Unix/Linux
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False
    try:
        import msvcrt  # Windows
        HAS_MSVCRT = True
    except ImportError:
        HAS_MSVCRT = False

class Lock:
    """Gestion des verrous de fichiers"""
    
    no_lock_flag = False
    
    @staticmethod
    @contextmanager
    def control(on_exn: Callable = None, wait: bool = True, lock_file: str = None):
        """Contrôle avec verrou de fichier"""
        if Lock.no_lock_flag or lock_file is None:
            yield
            return
        
        lock_fd = None
        try:
            lock_fd = os.open(lock_file, os.O_CREAT | os.O_WRONLY, 0o644)
            
            if HAS_FCNTL:  # Unix/Linux
                if wait:
                    fcntl.flock(lock_fd, fcntl.LOCK_EX)
                else:
                    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            elif HAS_MSVCRT:  # Windows
                if wait:
                    while True:
                        try:
                            msvcrt.locking(lock_fd, msvcrt.LK_NBLCK, 1)
                            break
                        except OSError:
                            time.sleep(0.1)
                else:
                    msvcrt.locking(lock_fd, msvcrt.LK_NBLCK, 1)
            # Si aucun module de verrouillage n'est disponible, on continue sans verrou
            
            yield
            
        except Exception as e:
            if on_exn:
                on_exn(e)
            else:
                raise
        finally:
            if lock_fd is not None:
                try:
                    if HAS_FCNTL:
                        fcntl.flock(lock_fd, fcntl.LOCK_UN)
                    elif HAS_MSVCRT:
                        msvcrt.locking(lock_fd, msvcrt.LK_UNLCK, 1)
                    os.close(lock_fd)
                except:
                    pass
    
    @staticmethod
    def pp_exception(exn_info):
        """Formate une exception pour l'affichage"""
        exn, bt = exn_info
        return f"Exception: {exn}\nBacktrace: {bt}"

class FileLock:
    """Classe de verrouillage de fichier compatible avec l'interface attendue"""
    
    def __init__(self, lock_file: str, wait: bool = True):
        self.lock_file = lock_file
        self.wait = wait
        self.lock_fd = None
        self.locked = False
    
    def acquire(self):
        """Acquiert le verrou"""
        if self.locked:
            return
        
        try:
            self.lock_fd = os.open(self.lock_file, os.O_CREAT | os.O_WRONLY, 0o644)
            
            if HAS_FCNTL:  # Unix/Linux
                if self.wait:
                    fcntl.flock(self.lock_fd, fcntl.LOCK_EX)
                else:
                    fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            elif HAS_MSVCRT:  # Windows
                if self.wait:
                    while True:
                        try:
                            msvcrt.locking(self.lock_fd, msvcrt.LK_NBLCK, 1)
                            break
                        except OSError:
                            time.sleep(0.1)
                else:
                    msvcrt.locking(self.lock_fd, msvcrt.LK_NBLCK, 1)
            
            self.locked = True
            
        except Exception:
            if self.lock_fd is not None:
                try:
                    os.close(self.lock_fd)
                except:
                    pass
                self.lock_fd = None
            raise
    
    def release(self):
        """Libère le verrou"""
        if not self.locked or self.lock_fd is None:
            return
        
        try:
            if HAS_FCNTL:
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
            elif HAS_MSVCRT:
                msvcrt.locking(self.lock_fd, msvcrt.LK_UNLCK, 1)
        except:
            pass
        finally:
            try:
                os.close(self.lock_fd)
            except:
                pass
            self.lock_fd = None
            self.locked = False
    
    def __enter__(self):
        """Support pour l'instruction 'with'"""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support pour l'instruction 'with'"""
        self.release()

class Mutil:
    """Utilitaires divers"""
    
    verbose = True
    
    @staticmethod
    def lock_file(filename: str) -> str:
        """Génère le nom du fichier de verrou"""
        return filename + ".lock"

class Secure:
    """Utilitaires de sécurité"""
    
    _base_dir = None
    
    @staticmethod
    def set_base_dir(directory: str):
        """Définit le répertoire de base sécurisé"""
        Secure._base_dir = os.path.abspath(directory)
    
    @staticmethod
    def get_base_dir() -> Optional[str]:
        """Obtient le répertoire de base sécurisé"""
        return Secure._base_dir
