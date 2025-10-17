import re
from typing import Dict, List, Tuple, Optional

from .models import Person, Family, IdAllocator


def _clean_token(tok: str) -> str:
    if tok is None:
        return ""
    # Unescape \_ then replace _ by space
    tok = tok.replace("\\_", "_")
    tok = tok.replace("_", " ")
    # Remove trailing disambiguation like .1234
    tok = re.sub(r"\.\d+$", "", tok)
    return tok.strip()


def _normalize_place(text: str) -> str:
    text = text.replace("\\_", "_")
    text = text.replace("_", " ")
    # Remove bracket wrappers like _[Saint-Jacques]_
    text = re.sub(r"_\[(.*?)\]_", r"\1", text)
    return text.strip()


def _name_key(surname: str, first_names: List[str]) -> str:
    return f"{surname}|{' '.join(first_names)}".strip()


def _parse_name_pair(tokens: List[str], start_idx: int = 0) -> Tuple[int, str, List[str]]:
    # Expect at least two tokens: surname and first-name token (can include hyphens/underscores)
    if start_idx >= len(tokens):
        return start_idx, "", []
    surname = _clean_token(tokens[start_idx])
    first_token = _clean_token(tokens[start_idx + 1]) if start_idx + 1 < len(tokens) else ""
    first_names = [x for x in first_token.split(" ") if x]
    return start_idx + 2, surname, first_names


def _looks_date(tok: str) -> bool:
    return bool(re.match(r"^[<~]?\d{1,2}/\d{1,2}/\d{2,4}$", tok) or re.match(r"^[<~]?\d{3,4}$", tok))


def parse_gw_text(gw_text: str) -> Dict[str, object]:
    """Parse a GW/GWPlus-like text and produce persons, families and notes.
    - Recognizes fam blocks with children (beg/end) and marriage events (fevt)
    - Recognizes pevt blocks for person events (#birt/#deat/#p/#bp/#dp)
    - Recognizes notes blocks for person notes (notes <Name> ... beg ... end notes)
    Returns dict: {persons: List[Person], families: List[Family], notes: Dict[name_key, str]}
    """
    lines = [ln.strip() for ln in gw_text.splitlines()]
    # State
    persons_map: Dict[str, Dict[str, Optional[str]]] = {}
    sex_map: Dict[str, str] = {}
    notes_map: Dict[str, str] = {}

    families_raw: List[Dict] = []  # {husband_key, wife_key, children_keys, marriage_date, marriage_place}

    # Helpers to get or create person
    def ensure_person(surname: str, first_names: List[str]) -> str:
        key = _name_key(surname, first_names)
        if key not in persons_map:
            persons_map[key] = {
                "surname": surname,
                "first_names": first_names,
                "birth_date": None,
                "birth_place": None,
                "death_date": None,
                "death_place": None,
                "father_key": None,
                "mother_key": None,
            }
        return key

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line or line.startswith("encoding:") or line.startswith("gwplus"):
            i += 1
            continue

        # fam line
        if line.startswith("fam "):
            # Tokenize
            tokens = line.split()
            # Parse husband (first two tokens after 'fam') until a control token ('#', '+', numeric marker)
            # We keep heuristic: first two tokens are surname/firstnames
            _, hus_surname, hus_first = _parse_name_pair(tokens, 1)
            husband_key = ensure_person(hus_surname, hus_first)
            sex_map[husband_key] = "M"

            # Try to find wife near the end: last two non-control tokens
            # Control tokens start with '#', or look like dates, or are '+' separators, or lone digits '0'
            # We'll scan from the end to find two candidate name tokens
            wife_surname = None
            wife_first = []
            # Remove any trailing control tokens
            end_idx = len(tokens) - 1
            while end_idx >= 0 and (tokens[end_idx].startswith('#') or tokens[end_idx] in {'+', 'od', '0'} or _looks_date(tokens[end_idx])):
                end_idx -= 1
            if end_idx >= 1:
                wife_surname = _clean_token(tokens[end_idx - 1])
                wife_first_token = _clean_token(tokens[end_idx])
                wife_first = [x for x in wife_first_token.split(' ') if x]
                wife_key = ensure_person(wife_surname, wife_first)
                sex_map[wife_key] = "F"
            else:
                wife_key = None

            # Initialize current family raw record
            fam_rec = {
                "husband_key": husband_key,
                "wife_key": wife_key,
                "children_keys": [],
                "marriage_date": None,
                "marriage_place": None,
            }

            # Advance to next lines to parse fevt/beg blocks that follow this fam
            i += 1
            # Parse following blocks until next fam or end
            while i < len(lines):
                ln = lines[i]
                if not ln:
                    i += 1
                    continue
                if ln.startswith("fam "):
                    break
                if ln.startswith("fevt"):
                    # Read events until 'end fevt'
                    i += 1
                    last_event = None
                    while i < len(lines) and not lines[i].startswith("end fevt"):
                        evt_line = lines[i]
                        evt_toks = evt_line.split()
                        j = 0
                        while j < len(evt_toks):
                            tok = evt_toks[j]
                            if tok == "#marr":
                                last_event = "marr"
                                j += 1
                                if j < len(evt_toks) and not evt_toks[j].startswith('#'):
                                    fam_rec["marriage_date"] = _clean_token(evt_toks[j])
                                    j += 1
                                continue
                            if tok in {"#p", "#mp"}:
                                j += 1
                                place_tokens = []
                                while j < len(evt_toks) and not evt_toks[j].startswith('#'):
                                    place_tokens.append(evt_toks[j])
                                    j += 1
                                place = _normalize_place(" ".join(place_tokens))
                                if last_event == "marr":
                                    fam_rec["marriage_place"] = place
                                continue
                            j += 1
                        i += 1
                    # consume 'end fevt'
                    if i < len(lines) and lines[i].startswith("end fevt"):
                        i += 1
                    continue
                if ln.startswith("beg"):
                    # Children list until 'end'
                    i += 1
                    while i < len(lines) and not lines[i].startswith("end"):
                        child_line = lines[i]
                        child_toks = child_line.split()
                        if len(child_toks) >= 3 and child_toks[0] == '-' and child_toks[1] in {'h', 'f'}:
                            gender = child_toks[1]
                            _, csurname, cfirst = _parse_name_pair(child_toks, 2)
                            ckey = ensure_person(csurname, cfirst)
                            sex_map[ckey] = 'M' if gender == 'h' else 'F'
                            # try to pick a date token following name for birth
                            # scan remaining tokens for a date-like and assign as birth_date
                            for t in child_toks[2+len(cfirst)+1:]:
                                if _looks_date(t):
                                    persons_map[ckey]['birth_date'] = _clean_token(t)
                                    break
                            # set parental links
                            persons_map[ckey]['father_key'] = fam_rec['husband_key']
                            persons_map[ckey]['mother_key'] = fam_rec['wife_key']
                            fam_rec['children_keys'].append(ckey)
                        i += 1
                    if i < len(lines) and lines[i].startswith("end"):
                        i += 1
                    continue
                # Other lines within fam block we ignore
                i += 1
            families_raw.append(fam_rec)
            continue

        # notes block for a person: 'notes <Surname> <First_Names>'
        if line.startswith("notes "):
            ntoks = line.split()
            _, nsurname, nfirst = _parse_name_pair(ntoks, 1)
            nkey = _name_key(nsurname, nfirst)
            # Read until 'end notes'
            i += 1
            buf: List[str] = []
            while i < len(lines) and not lines[i].startswith("end notes"):
                buf.append(lines[i])
                i += 1
            notes_map[nkey] = "\n".join(buf).strip()
            if i < len(lines) and lines[i].startswith("end notes"):
                i += 1
            continue

        # person events 'pevt <Surname> <First_Names>'
        if line.startswith("pevt "):
            ptoks = line.split()
            _, psurname, pfirst = _parse_name_pair(ptoks, 1)
            pkey = ensure_person(psurname, pfirst)
            # Read until 'end pevt'
            i += 1
            last_evt = None
            while i < len(lines) and not lines[i].startswith("end pevt"):
                evt_line = lines[i]
                evt_toks = evt_line.split()
                j = 0
                while j < len(evt_toks):
                    tok = evt_toks[j]
                    if tok in {"#birt", "#bapt", "#deat"}:
                        last_evt = tok
                        j += 1
                        if j < len(evt_toks) and not evt_toks[j].startswith('#'):
                            val = _clean_token(evt_toks[j])
                            if tok == "#birt":
                                persons_map[pkey]["birth_date"] = val
                            elif tok == "#deat":
                                persons_map[pkey]["death_date"] = val
                            j += 1
                        continue
                    if tok in {"#p", "#bp", "#dp"}:
                        j += 1
                        place_tokens = []
                        while j < len(evt_toks) and not evt_toks[j].startswith('#'):
                            place_tokens.append(evt_toks[j])
                            j += 1
                        place = _normalize_place(" ".join(place_tokens))
                        if last_evt in {"#birt", "#bapt"} or tok in {"#bp"}:
                            persons_map[pkey]["birth_place"] = place
                        else:
                            persons_map[pkey]["death_place"] = place
                        continue
                    j += 1
                i += 1
            if i < len(lines) and lines[i].startswith("end pevt"):
                i += 1
            continue

        # skip other lines
        i += 1

    # Assign ids and build Person/Family objects
    alloc = IdAllocator()
    key_to_id: Dict[str, int] = {}
    persons_out: List[Person] = []
    for key, data in persons_map.items():
        pid = alloc.alloc()
        key_to_id[key] = pid
        # Determine sex
        sex = sex_map.get(key)
        persons_out.append(Person(
            id=pid,
            first_names=data["first_names"],
            surname=data["surname"],
            sex=sex,
            father_id=None,  # set after building families
            mother_id=None,
            birth_date=data["birth_date"],
            birth_place=data["birth_place"],
            death_date=data["death_date"],
            death_place=data["death_place"],
        ))

    # Map for quick update of parent ids
    persons_by_key = {pkey: p for pkey, p in zip(key_to_id.keys(), persons_out)}

    families_out: List[Family] = []
    f_alloc = IdAllocator()
    for fr in families_raw:
        hid = key_to_id.get(fr["husband_key"]) if fr["husband_key"] else None
        wid = key_to_id.get(fr["wife_key"]) if fr["wife_key"] else None
        child_ids = [key_to_id[c] for c in fr["children_keys"]]
        fam = Family(
            id=f_alloc.alloc(),
            husband_id=hid,
            wife_id=wid,
            children_ids=child_ids,
            marriage_date=fr["marriage_date"],
            marriage_place=fr["marriage_place"],
        )
        families_out.append(fam)
        # assign parents to children
        for ck in fr["children_keys"]:
            p = persons_by_key.get(ck)
            if p:
                p.father_id = hid
                p.mother_id = wid

    return {"persons": persons_out, "families": families_out, "notes": notes_map}