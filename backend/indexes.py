from typing import Dict, List, Tuple
import hashlib
from .name_utils import crush_name, ngrams


def _stable_hash(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).digest()
    # take first 8 bytes for a 64-bit int
    return int.from_bytes(h[:8], "big")


def next_prime(n: int) -> int:
    def is_prime(x: int) -> bool:
        if x < 2:
            return False
        if x % 2 == 0:
            return x == 2
        i = 3
        while i * i <= x:
            if x % i == 0:
                return False
            i += 2
        return True
    p = max(3, n)
    while not is_prime(p):
        p += 1
    return p


def build_strings_index(strings: List[str]) -> Dict:
    """Build a hash-table like index mapping crushed string hash buckets to string ids.
    Structure similar in spirit to strings.inx.
    """
    if not strings:
        return {"table_size": 0, "buckets": []}
    size = next_prime(max(11, len(strings) * 10))
    buckets: List[List[int]] = [[] for _ in range(size)]
    for sid, s in enumerate(strings):
        key = crush_name(s)
        slot = _stable_hash(key) % size
        buckets[slot].append(sid)
    return {"table_size": size, "buckets": buckets}


def build_names_index(persons: List[Dict], strings: List[str]) -> Dict:
    """Build indexes akin to names.inx:
    - name_to_person: bucketed by crushed full name -> person ids
    - surname_ngrams: bucketed by surname n-grams -> surname string ids
    - firstname_ngrams: bucketed by first name n-grams -> first name string ids
    persons: list of dicts with keys referencing string ids: surname_id, first_name_ids
    """
    # Full name index
    if not persons:
        return {
            "name_to_person": {"table_size": 0, "buckets": []},
            "surname_ngrams": {"table_size": 0, "buckets": []},
            "firstname_ngrams": {"table_size": 0, "buckets": []},
        }

    full_keys: List[Tuple[int, str]] = []  # (person_id, crushed_full_name)
    surname_tokens: Dict[int, List[str]] = {}
    firstname_tokens: Dict[int, List[str]] = {}

    for p in persons:
        pid = p["id"]
        sname = strings[p["surname_id"]] if p.get("surname_id") is not None else ""
        fnames = [strings[i] for i in p.get("first_name_ids", [])]
        full = crush_name(" ".join([*fnames, sname]).strip())
        full_keys.append((pid, full))
        surname_tokens[pid] = ngrams(sname, 3)
        fn_ngrams: List[str] = []
        for fn in fnames:
            fn_ngrams.extend(ngrams(fn, 3))
        firstname_tokens[pid] = fn_ngrams

    # Build bucket tables
    # name_to_person
    name_size = next_prime(max(11, len(full_keys) * 10))
    name_buckets: List[List[int]] = [[] for _ in range(name_size)]
    for pid, key in full_keys:
        slot = _stable_hash(key) % name_size
        name_buckets[slot].append(pid)

    # surname_ngrams -> surname string ids (we store string ids, but we choose to store unique ids)
    # Build mapping substring -> set of string ids
    surname_set_map: Dict[str, set] = {}
    for p in persons:
        sid = p.get("surname_id")
        if sid is None:
            continue
        for tok in ngrams(strings[sid], 3):
            surname_set_map.setdefault(tok, set()).add(sid)
    s_keys = list(surname_set_map.keys())
    s_size = next_prime(max(11, len(s_keys) * 10))
    s_buckets: List[List[int]] = [[] for _ in range(s_size)]
    for tok, idset in surname_set_map.items():
        slot = _stable_hash(tok) % s_size
        # store unique ids under this slot (flattened)
        s_buckets[slot].extend(sorted(idset))

    # firstname_ngrams -> first name string ids
    fname_set_map: Dict[str, set] = {}
    for p in persons:
        for fid in p.get("first_name_ids", []):
            for tok in ngrams(strings[fid], 3):
                fname_set_map.setdefault(tok, set()).add(fid)
    f_keys = list(fname_set_map.keys())
    f_size = next_prime(max(11, len(f_keys) * 10))
    f_buckets: List[List[int]] = [[] for _ in range(f_size)]
    for tok, idset in fname_set_map.items():
        slot = _stable_hash(tok) % f_size
        f_buckets[slot].extend(sorted(idset))

    return {
        "name_to_person": {"table_size": name_size, "buckets": name_buckets},
        "surname_ngrams": {"table_size": s_size, "buckets": s_buckets},
        "firstname_ngrams": {"table_size": f_size, "buckets": f_buckets},
    }