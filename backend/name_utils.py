import unicodedata
import re
from typing import List


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def crush_name(text: str) -> str:
    """Approximate the "crushed" name as described by GeneWeb: lowercased,
    accents removed, punctuation stripped, spaces collapsed.
    """
    t = strip_accents(text).lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def ngrams(s: str, n: int = 3) -> List[str]:
    s = crush_name(s)
    if len(s) < n:
        return [s]
    return [s[i:i+n] for i in range(len(s) - n + 1)]
