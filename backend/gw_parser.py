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
    return bool(
        re.match(r"^[<~]?\d{1,2}/\d{1,2}/\d{2,4}$", tok)
        or re.match(r"^[<~]?\d{3,4}$", tok)
    )


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

    families_raw: List[Dict] = []
    # husband_key, wife_key, children_keys, marriage_date, marriage_place

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
                "per_id": None,  # Store original per ID if available
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
            
            # --- PARSE HUSBAND ---
            # Check if this is a reference format: 'fam <id> husb <person_ref>'
            if len(tokens) >= 4 and tokens[2] == "husb" and tokens[3].isdigit():
                # This is a reference to person with per_id
                per_id = tokens[3]
                # Find the person with this per_id
                husband_key = None
                for key, data in persons_map.items():
                    if data.get("per_id") == per_id:
                        husband_key = key
                        break
                if not husband_key:
                    # Person not found, create a placeholder
                    husband_key = f"per_{per_id}"
                    persons_map[husband_key] = {
                        "surname": "",
                        "first_names": [],
                        "birth_date": None,
                        "birth_place": None,
                        "death_date": None,
                        "death_place": None,
                        "father_key": None,
                        "mother_key": None,
                        "per_id": per_id,
                    }
            else:
                # Parse husband: tokens after 'fam <id>'
                _, hus_surname, hus_first = _parse_name_pair(tokens, 2)
                husband_key = ensure_person(hus_surname, hus_first)
            sex_map[husband_key] = "M"

            # --- PARSE WIFE ---
            wife_key = None
            
            # Look for 'wife' keyword followed by reference
            wife_idx = None
            for idx, token in enumerate(tokens):
                if token == "wife":
                    wife_idx = idx
                    break
            
            if wife_idx is not None and wife_idx + 1 < len(tokens):
                wife_ref = tokens[wife_idx + 1]
                if wife_ref.isdigit():
                     # This is a reference to person with per_id
                     for key, data in persons_map.items():
                         if data.get("per_id") == wife_ref:
                             wife_key = key
                             break
                     
                     # If person doesn't exist, create a placeholder
                     if wife_key is None:
                         wife_key = f"per_{wife_ref}"
                         persons_map[wife_key] = {
                             "surname": "",
                             "first_names": [],
                             "birth_date": None,
                             "birth_place": None,
                             "death_date": None,
                             "death_place": None,
                             "father_key": None,
                             "mother_key": None,
                             "per_id": wife_ref,
                         }
                else:
                    # Parse as name (fallback to old logic)
                    try:
                        plus_index = tokens.index('+')
                        
                        # Scan tokens after '+' to find the start of the wife's name,
                        # skipping control tokens (dates, '0', etc.)
                        wife_start_idx = plus_index + 1
                        while wife_start_idx < len(tokens):
                            tok = tokens[wife_start_idx]
                            if tok.startswith('#') or _looks_date(tok) or tok == '0':
                                wife_start_idx += 1
                            else:
                                # Found the start of the name
                                break
                        
                        # Ensure we have at least two tokens (surname + firstname)
                        if wife_start_idx < len(tokens) - 1:
                            _, wife_surname, wife_first = _parse_name_pair(tokens, wife_start_idx)
                            if wife_surname: # Only create person if a name was found
                                wife_key = ensure_person(wife_surname, wife_first)
                                
                    except ValueError:
                        # No '+' found, so no wife in this fam record (or single parent)
                        pass
            
            if wife_key:
                sex_map[wife_key] = "F" 

            # --- PARSE CHILDREN ---
            children_keys = []
            
            # Look for 'chil' keywords followed by references
            for idx, token in enumerate(tokens):
                if token == "chil" and idx + 1 < len(tokens):
                    child_ref = tokens[idx + 1]
                    if child_ref.isdigit():
                        # This is a reference to person with per_id
                        child_key = None
                        for key, data in persons_map.items():
                            if data.get("per_id") == child_ref:
                                child_key = key
                                break
                        
                        # If person doesn't exist, create a placeholder
                        if child_key is None:
                            child_key = f"per_{child_ref}"
                            persons_map[child_key] = {
                                "surname": "",
                                "first_names": [],
                                "birth_date": None,
                                "birth_place": None,
                                "death_date": None,
                                "death_place": None,
                                "father_key": None,
                                "mother_key": None,
                                "per_id": child_ref,
                            }
                        
                        children_keys.append(child_key)
            
            # Initialize current family raw record
            fam_rec = {
                "husband_key": husband_key,
                "wife_key": wife_key,
                "children_keys": children_keys,
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
                        if (
                            len(child_toks) >= 3
                            and child_toks[0] == '-'
                            and child_toks[1] in {'h', 'f'}
                        ):
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

        # per line: 'per <id> <First_Names> /<Surname>/ <sex> [birth_info] [death_info] [parent_info]'
        if line.startswith("per "):
            ptoks = line.split()
            if len(ptoks) < 4:
                i += 1
                continue
            
            # Extract person ID
            person_id = ptoks[1]
            
            # Find surname in /.../ format
            surname_start = -1
            surname_end = -1
            for idx, tok in enumerate(ptoks):
                if tok.startswith('/') and tok.endswith('/'):
                    surname_start = idx
                    surname_end = idx
                    break
                elif tok.startswith('/'):
                    surname_start = idx
                elif tok.endswith('/') and surname_start != -1:
                    surname_end = idx
                    break
            
            if surname_start == -1:
                i += 1
                continue
            
            # Extract first names (between person_id and surname)
            first_names = []
            for idx in range(2, surname_start):
                if idx < len(ptoks):
                    first_names.append(ptoks[idx])
            
            # Extract surname
            if surname_start == surname_end:
                surname = ptoks[surname_start][1:-1]  # Remove / /
            else:
                surname_parts = []
                for idx in range(surname_start, surname_end + 1):
                    if idx < len(ptoks):
                        part = ptoks[idx]
                        if idx == surname_start:
                            part = part[1:]  # Remove leading /
                        if idx == surname_end:
                            part = part[:-1]  # Remove trailing /
                        surname_parts.append(part)
                surname = " ".join(surname_parts)
            
            # Create person
            pkey = ensure_person(surname, first_names)
            
            # Store the original per ID
            persons_map[pkey]["per_id"] = person_id
            
            # Extract sex (token after surname)
            sex_idx = surname_end + 1
            if sex_idx < len(ptoks):
                sex = ptoks[sex_idx]
                if sex in {'m', 'f', 'M', 'F'}:
                    sex_map[pkey] = sex.upper()
            
            # Parse remaining tokens for birth/death/parent info
            idx = sex_idx + 1
            while idx < len(ptoks):
                tok = ptoks[idx]
                
                # Birth date
                if _looks_date(tok):
                    persons_map[pkey]["birth_date"] = _clean_token(tok)
                    idx += 1
                    # Check for 'in' keyword followed by place
                    if idx < len(ptoks) and ptoks[idx] == "in":
                        idx += 1
                        place_parts = []
                        while idx < len(ptoks) and not ptoks[idx].startswith('+') and ptoks[idx] not in {'fath', 'moth'}:
                            place_parts.append(ptoks[idx])
                            idx += 1
                        if place_parts:
                            persons_map[pkey]["birth_place"] = _normalize_place(" ".join(place_parts))
                    continue
                
                # Death date (starts with +)
                elif tok.startswith('+'):
                    death_date = tok[1:]  # Remove +
                    persons_map[pkey]["death_date"] = _clean_token(death_date)
                    idx += 1
                    # Check for 'in' keyword followed by place
                    if idx < len(ptoks) and ptoks[idx] == "in":
                        idx += 1
                        place_parts = []
                        while idx < len(ptoks) and ptoks[idx] not in {'fath', 'moth'}:
                            place_parts.append(ptoks[idx])
                            idx += 1
                        if place_parts:
                            persons_map[pkey]["death_place"] = _normalize_place(" ".join(place_parts))
                    continue
                
                # Father reference
                elif tok == "fath":
                    idx += 1
                    if idx < len(ptoks):
                        father_id = ptoks[idx]
                        # For now, store as string - will be resolved later
                        persons_map[pkey]["father_key"] = f"per_{father_id}"
                        idx += 1
                    continue
                
                # Mother reference
                elif tok == "moth":
                    idx += 1
                    if idx < len(ptoks):
                        mother_id = ptoks[idx]
                        # For now, store as string - will be resolved later
                        persons_map[pkey]["mother_key"] = f"per_{mother_id}"
                        idx += 1
                    continue
                
                else:
                    idx += 1
            
            i += 1
            continue

        # skip other lines
        i += 1

    # Create mapping from per_id to person key for resolving parent references
    per_id_to_key: Dict[str, str] = {}
    for key, data in persons_map.items():
        if data.get("per_id"):
            per_id_to_key[data["per_id"]] = key
    
    # Assign ids and build Person/Family objects
    alloc = IdAllocator(start=1)  # Start IDs from 1 to match test expectations
    key_to_id: Dict[str, int] = {}
    persons_out: List[Person] = []
    for key, data in persons_map.items():
        # Use per_id if available, otherwise allocate sequentially
        if data.get("per_id") and data["per_id"].isdigit():
            pid = int(data["per_id"])
        else:
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
    f_alloc = IdAllocator(start=1)  # Start family IDs from 1 to match test expectations
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

        if person.father_id is None and pdata["father_key"]:
            # Resolve father reference - could be a per_id or a person key
            father_key = pdata["father_key"]
            if father_key.startswith("per_"):
                # It's a per_id reference, resolve to actual key
                father_key = per_id_to_key.get(father_key, father_key)
            person.father_id = key_to_id.get(father_key)
            
        if person.mother_id is None and pdata["mother_key"]:
            # Resolve mother reference - could be a per_id or a person key
            mother_key = pdata["mother_key"]
            if mother_key.startswith("per_"):
                # It's a per_id reference, resolve to actual key
                mother_key = per_id_to_key.get(mother_key, mother_key)
            person.mother_id = key_to_id.get(mother_key)
        
        # Merge event data (pevt data overrides fam child data if present)
        if pdata["birth_date"]:
             person.birth_date = pdata["birth_date"]
        if pdata["birth_place"]:
             person.birth_place = pdata["birth_place"]
        if pdata["death_date"]:
             person.death_date = pdata["death_date"]
        if pdata["death_place"]:
             person.death_place = pdata["death_place"]


    return {"persons": persons_out, "families": families_out, "notes": notes_map}
