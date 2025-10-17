import json
from pathlib import Path
from typing import List, Dict, Optional

from .models import Person, Family, in_memory_strings
from .indexes import build_strings_index, build_names_index


MAGIC = "PY_GWB_01"  # magic number (8 chars)


def _encode_persons(persons: List[Person], strings_map: Dict[str, int]) -> List[Dict]:
    out = []
    for p in persons:
        out.append({
            "id": p.id,
            "surname_id": strings_map.get(p.surname),
            "first_name_ids": [strings_map[fn] for fn in p.first_names],
            "sex_id": strings_map.get(p.sex),
            "father_id": p.father_id,
            "mother_id": p.mother_id,
            "birth_date_id": strings_map.get(p.birth_date),
            "birth_place_id": strings_map.get(p.birth_place),
            "death_date_id": strings_map.get(p.death_date),
            "death_place_id": strings_map.get(p.death_place),
        })
    return out


def _encode_families(families: List[Family], strings_map: Dict[str, int]) -> List[Dict]:
    out = []
    for f in families:
        out.append({
            "id": f.id,
            "husband_id": f.husband_id,
            "wife_id": f.wife_id,
            "children_ids": f.children_ids,
            "marriage_date_id": strings_map.get(f.marriage_date),
            "marriage_place_id": strings_map.get(f.marriage_place),
        })
    return out


def write_gwb(base_dir: Path, db_name: str, persons: List[Person], families: List[Family], notes_origin_file: Optional[str] = None) -> Path:
    """Create a directory dbname.gwb with base.json, base.acc.json, names.inx.json, strings.inx.json.
    Inspired by GeneWeb storage (see docs) but JSON-encoded for Python backend.
    """
    db_dir = base_dir / f"{db_name}.gwb"
    db_dir.mkdir(parents=True, exist_ok=True)

    # Build strings mapping
    str_map = in_memory_strings(persons, families)
    # Keep array of strings ordered by id
    strings_arr = [None] * len(str_map)
    for s, sid in str_map.items():
        strings_arr[sid] = s

    # Encode arrays with string ids
    persons_enc = _encode_persons(persons, str_map)
    families_enc = _encode_families(families, str_map)

    # Base file content (JSON)
    base_content = {
        "magic": MAGIC,
        "counts": {
            "persons": len(persons_enc),
            "families": len(families_enc),
            "strings": len(strings_arr),
        },
        "offsets": {
            # Logical offsets (array start positions by index), JSON doesn't need byte offsets
            "persons_array_offset": 0,
            "families_array_offset": 0,
            "strings_array_offset": 0,
        },
        "notes_origin_file": notes_origin_file,
        "persons": persons_enc,
        "families": families_enc,
        "strings": strings_arr,
    }

    # base.acc: direct "offsets" are just positions for each id
    base_acc = {
        "persons_offsets": list(range(len(persons_enc))),
        "families_offsets": list(range(len(families_enc))),
        "strings_offsets": list(range(len(strings_arr))),
    }

    # Build indices
    strings_idx = build_strings_index(strings_arr)
    names_idx = build_names_index(persons_enc, strings_arr)

    # Write files
    (db_dir / "base.json").write_text(json.dumps(base_content, ensure_ascii=False, indent=2), encoding="utf-8")
    (db_dir / "base.acc.json").write_text(json.dumps(base_acc, ensure_ascii=False, indent=2), encoding="utf-8")
    (db_dir / "strings.inx.json").write_text(json.dumps(strings_idx, ensure_ascii=False, indent=2), encoding="utf-8")
    (db_dir / "names.inx.json").write_text(json.dumps(names_idx, ensure_ascii=False, indent=2), encoding="utf-8")

    return db_dir