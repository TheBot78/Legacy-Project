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
            "first_name_ids": [
                strings_map[fn] for fn in p.first_names
            ],
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


def _to_gw_token(text: Optional[str]) -> str:
    t = (text or "").strip()
    return t.replace(" ", "_")


def _first_names_token(first_names: List[str]) -> str:
    return _to_gw_token(" ".join(first_names)) if first_names else ""


def _year_from_date(text: Optional[str]) -> Optional[str]:
    t = (text or "").strip()
    if not t:
        return None
    m = re.search(r"(\d{4})", t)
    return m.group(1) if m else None


def write_gw(
    base_dir: Path,
    db_name: str,
    persons: List[Person],
    families: List[Family],
) -> Path:
    """Write a GW/GWPlus text file close to data/galichet.gw style.
    - Header with encoding + gwplus
    - fam line: "fam <H_SUR> <H_FIRST> 0 <H_YEAR> + <W_SUR> <W_FIRST> 0 <W_YEAR>"
    - fevt block always present with "#marr" (date optional) and optional "#mp"
    - beg/end children with "- h|f <SUR> <FIRST> [<BIRTH_DATE>] od"
    - per-person pevt with #birt/#deat and #bp/#dp
    """
    gw_path = base_dir / f"{db_name}.gw"

    by_id = {p.id: p for p in persons}
    lines: List[str] = []

    # Header
    lines.append("encoding: utf-8")
    lines.append("gwplus")
    lines.append("")

    # Families
    for fam in families:
        hus = by_id.get(fam.husband_id) if fam.husband_id is not None else None
        wife = by_id.get(fam.wife_id) if fam.wife_id is not None else None
        hus_sur = _to_gw_token(hus.surname) if hus else ""
        hus_first = _first_names_token(hus.first_names) if hus else ""
        wife_sur = _to_gw_token(wife.surname) if wife else ""
        wife_first = _first_names_token(wife.first_names) if wife else ""
        hus_year = _year_from_date(hus.birth_date) if hus else None
        wife_year = _year_from_date(wife.birth_date) if wife else None
        hus_age_tok = f"0 <{hus_year}" if hus_year else "0"
        wife_age_tok = f"0 <{wife_year}" if wife_year else "0"
        fam_line_parts = [
            "fam",
            hus_sur,
            hus_first,
            hus_age_tok,
            "+",
            wife_sur,
            wife_first,
            wife_age_tok,
        ]
        fam_line = " ".join(fam_line_parts).strip()
        lines.append(fam_line)

        # Optional 'src'/'csrc' lines not available in model; omitted

        # Marriage events block
        lines.append("fevt")
        if fam.marriage_date:
            lines.append(f"#marr {fam.marriage_date}")
        else:
            lines.append("#marr")
        if fam.marriage_place:
            place_tok = _to_gw_token(fam.marriage_place)
            lines.append(f"#mp {place_tok}")
        lines.append("end fevt")

        # Children
        if fam.children_ids:
            lines.append("beg")
            for cid in fam.children_ids:
                c = by_id.get(cid)
                if not c:
                    continue
                sex = (c.sex or "").upper()
                gender = "h" if sex == "M" else "f" if sex == "F" else "h"
                c_sur = _to_gw_token(c.surname)
                c_first = _first_names_token(c.first_names)
                child_line = f"- {gender} {c_sur} {c_first}"
                if c.birth_date:
                    child_line += f" {c.birth_date}"
                child_line += " od"
                lines.append(child_line)
            lines.append("end")

        lines.append("")

    # Person events
    for p in persons:
        has_evt = bool(p.birth_date or p.birth_place or p.death_date or p.death_place)
        if not has_evt:
            continue
        psur = _to_gw_token(p.surname)
        pfirst = _first_names_token(p.first_names)
        lines.append(f"pevt {psur} {pfirst}")
        if p.birth_date:
            lines.append(f"#birt {p.birth_date}")
        if p.birth_place:
            lines.append(f"#bp {_to_gw_token(p.birth_place)}")
        if p.death_date:
            lines.append(f"#deat {p.death_date}")
        if p.death_place:
            lines.append(f"#dp {_to_gw_token(p.death_place)}")
        lines.append("end pevt")
        lines.append("")

    gw_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return gw_path


def write_gwb(
    base_dir: Path,
    db_name: str,
    persons: List[Person],
    families: List[Family],
    notes_origin_file: Optional[str] = None,
) -> Path:
    """Create a directory dbname.gwb with base.json, base.acc.json,
    names.inx.json, strings.inx.json.
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
    (db_dir / "base.json").write_text(
        json.dumps(base_content, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (db_dir / "base.acc.json").write_text(
        json.dumps(base_acc, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (db_dir / "strings.inx.json").write_text(
        json.dumps(strings_idx, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (db_dir / "names.inx.json").write_text(
        json.dumps(names_idx, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return db_dir
