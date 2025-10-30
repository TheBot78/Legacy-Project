from typing import List, Dict, Tuple, Optional

from .models import Person, Family, IdAllocator
from .name_utils import crush_name


GED_TAG_LEVEL = {
    "INDI": 0,
    "FAM": 0,
}


class GedRecord:
    def __init__(self, tag: str, xref: Optional[str] = None):
        self.tag = tag
        self.xref = xref
        self.lines: List[Tuple[int, str, Optional[str]]] = []

    def add(self, level: int, tag: str, data: Optional[str]):
        self.lines.append((level, tag, data))


def _tokenize(ged_text: str) -> List[Tuple[int, Optional[str], str, Optional[str]]]:
    tokens: List[Tuple[int, Optional[str], str, Optional[str]]] = []
    for raw in ged_text.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        parts = line.split(" ")
        if not parts:
            continue
        try:
            level = int(parts[0])
        except ValueError:
            continue
        xref = None
        tag = None
        data = None
        idx = 1
        if idx < len(parts) and parts[idx].startswith("@") and parts[idx].endswith("@"):
            xref = parts[idx]
            idx += 1
        if idx < len(parts):
            tag = parts[idx]
            idx += 1
        if idx < len(parts):
            data = " ".join(parts[idx:])
        if tag is None:
            continue
        tokens.append((level, xref, tag, data))
    return tokens


def parse_ged_text(ged_text: str) -> Dict[str, List]:
    tokens = _tokenize(ged_text)

    indi_records: Dict[str, GedRecord] = {}
    fam_records: Dict[str, GedRecord] = {}

    current: Optional[GedRecord] = None
    current_level = -1

    for level, xref, tag, data in tokens:
        if level == 0:
            # Start new record
            if tag == "INDI" or tag == "FAM":
                current = GedRecord(tag, xref)
                current_level = 0
                if tag == "INDI" and xref:
                    indi_records[xref] = current
                elif tag == "FAM" and xref:
                    fam_records[xref] = current
            else:
                current = None
                current_level = -1
            continue
        if current is None:
            continue
        current.add(level, tag, data)

    pid_alloc = IdAllocator()
    fid_alloc = IdAllocator()

    # Map xref -> Person/Family ids
    person_id_by_xref: Dict[str, int] = {}
    family_id_by_xref: Dict[str, int] = {}

    persons: List[Person] = []
    families: List[Family] = []

    persons_by_id: Dict[int, Person] = {}

    # Pass 1: create Person entries
    for xref, rec in indi_records.items():
        first_names: List[str] = []
        surname: str = ""
        sex: Optional[str] = None
        birth_date: Optional[str] = None
        birth_place: Optional[str] = None
        death_date: Optional[str] = None
        death_place: Optional[str] = None
        # ... (famc, fams etc. non utilisés ici) ...

        i = 0
        while i < len(rec.lines):
            level, tag, data = rec.lines[i]
            if tag == "NAME" and data:
                name = data.strip()
                parts = name.split("/")
                if len(parts) >= 2:
                    before = parts[0].strip()
                    surname = parts[1].strip()
                    if before:
                        first_names = [x for x in before.split(" ") if x]
                else:
                    first_names = [name]
            elif tag == "SEX" and data:
                s = data.strip().upper()
                if s in ("M", "F", "U"):
                    sex = s
            elif tag == "BIRT":
                j = i + 1
                while j < len(rec.lines) and rec.lines[j][0] > level:
                    l2, t2, d2 = rec.lines[j]
                    if t2 == "DATE" and d2:
                        birth_date = d2.strip()
                    elif t2 == "PLAC" and d2:
                        birth_place = d2.strip()
                    j += 1
                i = j - 1
            elif tag == "DEAT":
                j = i + 1
                while j < len(rec.lines) and rec.lines[j][0] > level:
                    l2, t2, d2 = rec.lines[j]
                    if t2 == "DATE" and d2:
                        death_date = d2.strip()
                    elif t2 == "PLAC" and d2:
                        death_place = d2.strip()
                    j += 1
                i = j - 1
            i += 1 # Avancer dans tous les cas

        pid = pid_alloc.alloc()
        person_id_by_xref[xref] = pid
        
        person_obj = Person(
            id=pid,
            first_names=first_names or [],
            surname=surname or "",
            sex=sex,
            father_id=None,  # Sera défini en Passe 3
            mother_id=None,
            birth_date=birth_date,
            birth_place=birth_place,
            death_date=death_date,
            death_place=death_place,
        )
        persons.append(person_obj)
        persons_by_id[pid] = person_obj

    # Pass 2: create Family entries
    for xref, rec in fam_records.items():
        husband_xref: Optional[str] = None
        wife_xref: Optional[str] = None
        children_xrefs: List[str] = []
        marriage_date: Optional[str] = None
        marriage_place: Optional[str] = None

        i = 0
        while i < len(rec.lines):
            level, tag, data = rec.lines[i]
            if tag == "HUSB" and data:
                husband_xref = data.strip()
            elif tag == "WIFE" and data:
                wife_xref = data.strip()
            elif tag == "CHIL" and data:
                children_xrefs.append(data.strip())
            elif tag == "MARR":
                j = i + 1
                while j < len(rec.lines) and rec.lines[j][0] > level:
                    l2, t2, d2 = rec.lines[j]
                    if t2 == "DATE" and d2:
                        marriage_date = d2.strip()
                    elif t2 == "PLAC" and d2:
                        marriage_place = d2.strip()
                    j += 1
                i = j - 1
            i += 1

        fid = fid_alloc.alloc()
        family_id_by_xref[xref] = fid
        families.append(Family(
            id=fid,
            husband_id=person_id_by_xref.get(husband_xref) if husband_xref else None,
            wife_id=person_id_by_xref.get(wife_xref) if wife_xref else None,
            children_ids=[person_id_by_xref[c] for c in children_xrefs if c in person_id_by_xref],
            marriage_date=marriage_date,
            marriage_place=marriage_place,
        ))

    famc_by_child: Dict[int, str] = {}
    for xref, rec in indi_records.items():
        child_pid = person_id_by_xref.get(xref)
        famc_xref: Optional[str] = None
        for level, tag, data in rec.lines:
            if tag == "FAMC" and data:
                famc_xref = data.strip()
                break
        if child_pid is not None and famc_xref:
            famc_by_child[child_pid] = famc_xref

    for fam_xref, fid in family_id_by_xref.items():
        fam = next((f for f in families if f.id == fid), None)
        if fam is None:
            continue
        for child_id in fam.children_ids:
            famc_xref = famc_by_child.get(child_id)
            if famc_xref == fam_xref:
                child = persons_by_id.get(child_id)
                if child:
                    child.father_id = fam.husband_id
                    child.mother_id = fam.wife_id
    
    return {
        "persons": persons, 
        "families": families,
        "notes": {},
    }