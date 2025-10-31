from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

from .models import Person, Family


class StringsMap:
    def __init__(self):
        self.strings: List[str] = []
        self.index_by_string: Dict[str, int] = {}

    def get_id(self, s: Optional[str]) -> Optional[int]:
        if s is None:
            return None
        key = s.strip()
        if key == "":
            return None
        if key in self.index_by_string:
            return self.index_by_string[key]
        idx = len(self.strings)
        self.strings.append(key)
        self.index_by_string[key] = idx
        return idx


def _encode_persons(persons: List[Person], strings: StringsMap) -> List[Dict]:
    out: List[Dict] = []
    for p in persons:
        out.append({
            "id": p.id,
            "first_name_ids": [strings.get_id(fn) for fn in p.first_names],
            "surname_id": strings.get_id(p.surname),
            "sex": p.sex,
            "father_id": p.father_id,
            "mother_id": p.mother_id,
            "birth_date_id": strings.get_id(p.birth_date),
            "birth_place_id": strings.get_id(p.birth_place),
            "death_date_id": strings.get_id(p.death_date),
            "death_place_id": strings.get_id(p.death_place),
        })
    return out


def _encode_families(families: List[Family], strings: StringsMap) -> List[Dict]:
    out: List[Dict] = []
    for f in families:
        out.append({
            "id": f.id,
            "husband_id": f.husband_id,
            "wife_id": f.wife_id,
            "children_ids": f.children_ids,
            "marriage_date_id": strings.get_id(f.marriage_date),
            "marriage_place_id": strings.get_id(f.marriage_place),
        })
    return out


def write_gwb(
    root_dir: Path,
    db_name: str,
    persons: List[Person],
    families: List[Family],
    notes_origin_file: Optional[str] = None,
) -> Path:
    db_dir = root_dir / f"{db_name}.gwb"
    db_dir.mkdir(parents=True, exist_ok=True)

    strings_map = StringsMap()
    persons_enc = _encode_persons(persons, strings_map)
    families_enc = _encode_families(families, strings_map)

    base = {
        "counts": {
            "persons": len(persons_enc),
            "families": len(families_enc),
            "strings": len(strings_map.strings),
        },
        "persons": persons_enc,
        "families": families_enc,
        "strings": strings_map.strings,
        "notes_origin_file": notes_origin_file,
    }

    (db_dir / "base.json").write_text(
        json.dumps(base, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Simple access index with logical offsets (here just identity)
    acc = {
        "persons": {str(p["id"]): p["id"] for p in persons_enc},
        "families": {str(f["id"]): f["id"] for f in families_enc},
    }
    (db_dir / "base.acc.json").write_text(
        json.dumps(acc, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Names index (hashed buckets by crushed full name)
    from .name_utils import crush_name
    name_buckets: Dict[int, List[int]] = {}
    table_size = max(1, len(persons_enc))
    for p in persons_enc:
        full_name = " ".join(
            [
                strings_map.strings[i]
                for i in p["first_name_ids"]
                if i is not None
            ]
        )
        surname = (
            strings_map.strings[p["surname_id"]]
            if p["surname_id"] is not None
            else ""
        )
        full_name = (full_name + " " + surname).strip()
        h = abs(hash(crush_name(full_name))) % table_size
        name_buckets.setdefault(h, []).append(p["id"])
    names_json = {
        "table_size": table_size,
        "buckets": name_buckets,
    }
    (db_dir / "names.inx.json").write_text(
        json.dumps(names_json, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Strings index (hashed buckets)
    s_buckets: Dict[int, List[int]] = {}
    s_table_size = max(1, len(strings_map.strings))
    for sid, s in enumerate(strings_map.strings):
        key = crush_name(s)
        import hashlib
        slot = (
            int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big")
            % s_table_size
        )
        s_buckets.setdefault(slot, []).append(sid)
    s_inx = {
        "table_size": s_table_size,
        "buckets": [s_buckets.get(i, []) for i in range(s_table_size)],
    }
    (db_dir / "strings.inx.json").write_text(
        json.dumps(s_inx, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return db_dir


def _to_gw_token(s: Optional[str]) -> str:
    if not s:
        return ""
    return s.replace(" ", "_")


def _first_names_token(first_names: List[str]) -> str:
    return _to_gw_token(" ".join([fn for fn in first_names if fn]))


def _year_from_date(date_str: Optional[str]) -> str:
    if not date_str:
        return "0"
    # Accept forms like "7/9/1830", "1839", "<1849", etc.
    for ch in date_str:
        if ch.isdigit():
            break
    digits = "".join([c for c in date_str if c.isdigit()])
    if len(digits) >= 4:
        return digits[-4:]
    return "0"


# Write a .gw textual file (GeneWeb style) matching data/galichet.gw format
# This is a minimal generator for interoperability/tests

def write_gw(root_dir: Path, db_name: str, persons: List[Person], families: List[Family]) -> Path:
    gw_path = root_dir / f"{db_name}.gw"
    lines: List[str] = []
    lines.append("encoding: utf-8")
    lines.append("gwplus")
    lines.append("")

    persons_by_id: Dict[int, Person] = {p.id: p for p in persons}

    # Families first
    for f in families:
        h = persons_by_id.get(f.husband_id) if f.husband_id is not None else None
        w = persons_by_id.get(f.wife_id) if f.wife_id is not None else None
        h_year = _year_from_date(h.birth_date) if h else "0"
        w_year = _year_from_date(w.birth_date) if w else "0"
        fam_line_parts = [
            "fam",
            _to_gw_token(h.surname) if h else "",
            _first_names_token(h.first_names) if h else "",
            "0",
            h_year,
            "+",
            _to_gw_token(w.surname) if w else "",
            _first_names_token(w.first_names) if w else "",
            "0",
            w_year,
        ]
        lines.append(" ".join([x for x in fam_line_parts if x != ""]))
        lines.append("fevt")
        if f.marriage_date:
            lines.append(f"#marr {f.marriage_date}")
        else:
            lines.append("#marr ")
        if f.marriage_place:
            lines.append(f"#mp {f.marriage_place}")
        lines.append("end fevt")
        if f.children_ids:
            lines.append("beg")
            for cid in f.children_ids:
                c = persons_by_id.get(cid)
                if not c:
                    continue
                sex_tok = "h" if c.sex == "M" else "f" if c.sex == "F" else "h"
                child = [
                    "-",
                    sex_tok,
                    _to_gw_token(c.surname),
                    _first_names_token(c.first_names),
                ]
                if c.birth_date:
                    child.append(c.birth_date)
                child.append("od")
                lines.append(" ".join(child))
            lines.append("end")
        lines.append("")

    # Person events
    for p in persons:
        lines.append(f"pevt {_to_gw_token(p.surname)} {_first_names_token(p.first_names)}")
        if p.birth_date:
            if p.birth_place:
                lines.append(f"#birt {p.birth_date} #p {p.birth_place}")
            else:
                lines.append(f"#birt {p.birth_date}")
        else:
            lines.append("#birt ")
        if p.death_date:
            if p.death_place:
                lines.append(f"#deat {p.death_date} #p {p.death_place}")
            else:
                lines.append(f"#deat {p.death_date}")
        else:
            lines.append("#deat ")
        lines.append("end pevt")
        lines.append("")

    gw_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return gw_path


def write_gwf(root_dir: Path, db_name: str) -> Path:
    """
    Write a minimal .gwf configuration file alongside the base.
    The content mirrors common GeneWeb options; can be extended later.
    """
    gwf_path = root_dir / f"{db_name}.gwf"
    content = "\n".join([
        "access_by_key=yes",
        "disable_forum=yes",
        "hide_private_names=no",
        "use_restrict=no",
        "show_consang=yes",
        "display_sosa=yes",
        "place_surname_link_to_ind=yes",
        "max_anc_level=8",
        "max_anc_tree=7",
        "max_desc_level=12",
        "max_desc_tree=4",
        "max_cousins=2000",
        "max_cousins_level=5",
        "latest_event=20",
        "template=*",
        "long_date=no",
        "counter=no",
        "full_siblings=yes",
        "hide_advanced_request=no",
        "perso_module_i=individu",
        "perso_module_p=parents",
        "perso_module_g=gr_parents",
        "perso_module_u=unions",
        "perso_module_f=fratrie",
        "perso_module_r=relations",
        "perso_module_c=chronologie",
        "perso_module_n=notes",
        "perso_module_s=sources",
        "perso_module_a=arbres",
        "perso_module_h=htrees",
        "perso_module_d=data_3col",
        "perso_module_l=ligne",
        "p_mod=",
    ])
    gwf_path.write_text(content + "\n", encoding="utf-8")
    return gwf_path


def write_gwb_classic(
    root_dir: Path,
    db_name: str,
    persons: List[Person],
    families: List[Family],
) -> Path:
    """
    Écrit un dossier .gwb classique (structure GeneWeb) avec les fichiers attendus.
    Contenus générés minimaux (placeholders) pour correspondre exactement aux noms de fichiers.
    """
    db_dir = root_dir / f"{db_name}.gwb"
    db_dir.mkdir(parents=True, exist_ok=True)

    # nb_persons
    (db_dir / "nb_persons").write_text(str(len(persons)) + "\n", encoding="utf-8")

    # particles.txt (liste par défaut)
    particles = [
        "de", "du", "des", "la", "le", "les", "van", "von", "d'", "da", "di",
    ]
    (db_dir / "particles.txt").write_text("\n".join(particles) + "\n", encoding="utf-8")

    # snames.dat / fnames.dat : listes uniques de noms/prénoms
    surnames = sorted({p.surname.strip() for p in persons if p.surname})
    firstnames = sorted({fn.strip() for p in persons for fn in p.first_names if fn})
    (db_dir / "snames.dat").write_text("\n".join(surnames) + "\n", encoding="utf-8")
    (db_dir / "fnames.dat").write_text("\n".join(firstnames) + "\n", encoding="utf-8")

    # inx/acc placeholders : contenu simple textuel indiquant des offsets/hashs simulés
    # names.inx / names.acc
    names_inx = {
        "table_size": max(1, len(surnames)),
        "buckets": [[i] for i in range(len(surnames))],
    }
    (db_dir / "names.inx").write_text(json.dumps(names_inx), encoding="utf-8")
    names_acc = {
        "offsets": list(range(len(surnames))),
    }
    (db_dir / "names.acc").write_text(json.dumps(names_acc), encoding="utf-8")

    # fnames.inx
    fnames_inx = {
        "table_size": max(1, len(firstnames)),
        "buckets": [[i] for i in range(len(firstnames))],
    }
    (db_dir / "fnames.inx").write_text(json.dumps(fnames_inx), encoding="utf-8")

    # strings.inx : index pour toutes chaînes simples (dates/lieux)
    strings_set = set()
    for p in persons:
        for s in [p.birth_date, p.birth_place, p.death_date, p.death_place]:
            if s:
                strings_set.add(s)
    for f in families:
        if f.marriage_date:
            strings_set.add(f.marriage_date)
        if f.marriage_place:
            strings_set.add(f.marriage_place)
    strings = sorted(strings_set)
    s_inx = {
        "table_size": max(1, len(strings)),
        "buckets": [[i] for i in range(len(strings))],
    }
    (db_dir / "strings.inx").write_text(json.dumps(s_inx), encoding="utf-8")

    # snames.inx : index des patronymes
    sn_inx = {
        "table_size": max(1, len(surnames)),
        "buckets": [[i] for i in range(len(surnames))],
    }
    (db_dir / "snames.inx").write_text(json.dumps(sn_inx), encoding="utf-8")

    # base / base.acc : placeholders textuels
    base_placeholder = {
        "persons_count": len(persons),
        "families_count": len(families),
    }
    (db_dir / "base").write_text(json.dumps(base_placeholder), encoding="utf-8")
    base_acc_placeholder = {
        "persons_offsets": list(range(len(persons))),
        "families_offsets": list(range(len(families))),
    }
    (db_dir / "base.acc").write_text(json.dumps(base_acc_placeholder), encoding="utf-8")

    return db_dir


def write_json_base(
    root_dir: Path,
    db_name: str,
    persons: List[Person],
    families: List[Family],
    notes_origin_file: Optional[str] = None,
) -> Path:
    """
    Écrit la base JSON lisible par l’API dans un dossier séparé
    backend/bases/json_bases/{db_name}/, sans polluer le .gwb classique.
    """
    json_dir = root_dir / "json_bases" / db_name
    json_dir.mkdir(parents=True, exist_ok=True)

    strings_map = StringsMap()
    persons_enc = _encode_persons(persons, strings_map)
    families_enc = _encode_families(families, strings_map)

    base = {
        "counts": {
            "persons": len(persons_enc),
            "families": len(families_enc),
            "strings": len(strings_map.strings),
        },
        "persons": persons_enc,
        "families": families_enc,
        "strings": strings_map.strings,
        "notes_origin_file": notes_origin_file,
    }

    (json_dir / "base.json").write_text(
        json.dumps(base, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    acc = {
        "persons": {str(p["id"]): p["id"] for p in persons_enc},
        "families": {str(f["id"]): f["id"] for f in families_enc},
    }
    (json_dir / "base.acc.json").write_text(
        json.dumps(acc, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Names/strings index JSON lisibles
    from .name_utils import crush_name
    name_buckets: Dict[int, List[int]] = {}
    table_size = max(1, len(persons_enc))
    for p in persons_enc:
        full_name = " ".join(
            [
                strings_map.strings[i]
                for i in p["first_name_ids"]
                if i is not None
            ]
        )
        surname = (
            strings_map.strings[p["surname_id"]]
            if p["surname_id"] is not None
            else ""
        )
        full_name = (full_name + " " + surname).strip()
        h = abs(hash(crush_name(full_name))) % table_size
        name_buckets.setdefault(h, []).append(p["id"])
    names_json = {
        "table_size": table_size,
        "buckets": name_buckets,
    }
    (json_dir / "names.inx.json").write_text(
        json.dumps(names_json, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    str_table_size = max(1, len(strings_map.strings))
    str_buckets: Dict[int, List[int]] = {}
    for i, s in enumerate(strings_map.strings):
        h = abs(hash(crush_name(s))) % str_table_size
        str_buckets.setdefault(h, []).append(i)
    strings_json = {
        "table_size": str_table_size,
        "buckets": str_buckets,
    }
    (json_dir / "strings.inx.json").write_text(
        json.dumps(strings_json, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return json_dir
