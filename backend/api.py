from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import json

from .models import Person, Family, IdAllocator
from .storage import write_gwb
from .name_utils import crush_name
from .gw_parser import parse_gw_text
from .ged_parser import parse_ged_text
from fastapi.responses import RedirectResponse


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI(title="GeneWeb-like Python Backend", version="0.1")


class PersonInput(BaseModel):
    id: Optional[int] = None
    first_names: List[str]
    surname: str
    sex: Optional[str] = None
    father_id: Optional[int] = None
    mother_id: Optional[int] = None
    birth_date: Optional[str] = None
    birth_place: Optional[str] = None
    death_date: Optional[str] = None
    death_place: Optional[str] = None


class FamilyInput(BaseModel):
    id: Optional[int] = None
    husband_id: Optional[int] = None
    wife_id: Optional[int] = None
    children_ids: List[int] = []
    marriage_date: Optional[str] = None
    marriage_place: Optional[str] = None


class ImportRequest(BaseModel):
    db_name: str
    persons: List[PersonInput]
    families: List[FamilyInput]
    notes_origin_file: Optional[str] = None


@app.post("/import")
def import_database(req: ImportRequest):
    pid_alloc = IdAllocator()
    fid_alloc = IdAllocator()

    persons: List[Person] = []
    for p in req.persons:
        pid = p.id if p.id is not None else pid_alloc.alloc()
        persons.append(Person(
            id=pid,
            first_names=p.first_names,
            surname=p.surname,
            sex=p.sex,
            father_id=p.father_id,
            mother_id=p.mother_id,
            birth_date=p.birth_date,
            birth_place=p.birth_place,
            death_date=p.death_date,
            death_place=p.death_place,
        ))

    families: List[Family] = []
    for f in req.families:
        fid = f.id if f.id is not None else fid_alloc.alloc()
        families.append(Family(
            id=fid,
            husband_id=f.husband_id,
            wife_id=f.wife_id,
            children_ids=f.children_ids,
            marriage_date=f.marriage_date,
            marriage_place=f.marriage_place,
        ))

    db_dir = write_gwb(DATA_DIR, req.db_name, persons, families, req.notes_origin_file)
    return {"ok": True, "db_dir": str(db_dir)}


@app.get("/db/{db_name}/persons/{person_id}")
def get_person(db_name: str, person_id: int):
    db_dir = DATA_DIR / f"{db_name}.gwb"
    base_path = db_dir / "base.json"
    if not base_path.exists():
        raise HTTPException(status_code=404, detail="Base not found")
    base = json.loads(base_path.read_text(encoding="utf-8"))
    persons = base.get("persons", [])
    for p in persons:
        if p.get("id") == person_id:
            return p
    raise HTTPException(status_code=404, detail="Person not found")


@app.get("/db/{db_name}/families/{family_id}")
def get_family(db_name: str, family_id: int):
    db_dir = DATA_DIR / f"{db_name}.gwb"
    base_path = db_dir / "base.json"
    if not base_path.exists():
        raise HTTPException(status_code=404, detail="Base not found")
    base = json.loads(base_path.read_text(encoding="utf-8"))
    families = base.get("families", [])
    for f in families:
        if f.get("id") == family_id:
            return f
    raise HTTPException(status_code=404, detail="Family not found")


@app.get("/db/{db_name}/search/name")
def search_by_name(db_name: str, q: str):
    db_dir = DATA_DIR / f"{db_name}.gwb"
    names_path = db_dir / "names.inx.json"
    base_path = db_dir / "base.json"
    if not names_path.exists() or not base_path.exists():
        raise HTTPException(status_code=404, detail="Index or base not found")
    names_idx = json.loads(names_path.read_text(encoding="utf-8"))
    base = json.loads(base_path.read_text(encoding="utf-8"))
    persons = base.get("persons", [])
    strings = base.get("strings", [])

    key = crush_name(q)
    table_size = names_idx["name_to_person"]["table_size"]
    buckets = names_idx["name_to_person"]["buckets"]

    import hashlib
    h = hashlib.sha256(key.encode("utf-8")).digest()
    slot = int.from_bytes(h[:8], "big") % (table_size or 1)
    ids = buckets[slot] if table_size > 0 else []

    # Filter exact crushed full name matches
    results = []
    for pid in ids:
        p = next((x for x in persons if x.get("id") == pid), None)
        if p is None:
            continue
        fnames = [strings[i] for i in p.get("first_name_ids", [])]
        sname = strings[p.get("surname_id")] if p.get("surname_id") is not None else ""
        full = crush_name(" ".join([*fnames, sname]).strip())
        if full == key:
            results.append(p)
    return {"query": q, "results": results}


@app.get("/db/{db_name}/search/string")
def search_by_string(db_name: str, q: str):
    db_dir = DATA_DIR / f"{db_name}.gwb"
    strings_path = db_dir / "strings.inx.json"
    base_path = db_dir / "base.json"
    if not strings_path.exists() or not base_path.exists():
        raise HTTPException(status_code=404, detail="Index or base not found")
    s_idx = json.loads(strings_path.read_text(encoding="utf-8"))
    strings = json.loads(base_path.read_text(encoding="utf-8")).get("strings", [])

    key = crush_name(q)
    table_size = s_idx["table_size"]
    buckets = s_idx["buckets"]

    import hashlib
    h = hashlib.sha256(key.encode("utf-8")).digest()
    slot = int.from_bytes(h[:8], "big") % (table_size or 1)
    ids = buckets[slot] if table_size > 0 else []

    # Filter strings that match the crushed form
    results = [
        {"id": sid, "value": s}
        for sid in ids
        for s in [strings[sid]]
        if crush_name(s) == key
    ]
    return {"query": q, "results": results}


@app.get("/db/{db_name}/stats")
def stats(db_name: str):
    db_dir = DATA_DIR / f"{db_name}.gwb"
    base_path = db_dir / "base.json"
    if not base_path.exists():
        raise HTTPException(status_code=404, detail="Base not found")
    base = json.loads(base_path.read_text(encoding="utf-8"))
    return base.get("counts", {})


class GwParseRequest(BaseModel):
    gw_text: str


class GwImportGWRequest(BaseModel):
    db_name: str
    gw_text: str
    notes_origin_file: Optional[str] = None


class GwImportGEDRequest(BaseModel):
    db_name: str
    ged_text: str
    notes_origin_file: Optional[str] = None


@app.post("/parse_gw")
def parse_gw(req: GwParseRequest):
    parsed = parse_gw_text(req.gw_text)
    persons = [p.__dict__ for p in parsed["persons"]]
    families = [f.__dict__ for f in parsed["families"]]
    return {
        "counts": {
            "persons": len(persons),
            "families": len(families),
            "notes": len(parsed["notes"]),
        },
        "persons": persons,
        "families": families,
        "notes": parsed["notes"],
    }


@app.post("/import_gw")
def import_gw(req: GwImportGWRequest):
    parsed = parse_gw_text(req.gw_text)
    persons: List[Person] = parsed["persons"]
    families: List[Family] = parsed["families"]
    db_dir = write_gwb(
        DATA_DIR,
        req.db_name,
        persons,
        families,
        req.notes_origin_file,
    )
    return {
        "ok": True,
        "db_dir": str(db_dir),
        "counts": {
            "persons": len(persons),
            "families": len(families),
        },
        "persons": [p.__dict__ for p in persons],
        "families": [f.__dict__ for f in families],
        "notes": parsed.get("notes", {}),
    }


@app.post("/import_ged")
def import_ged(req: GwImportGEDRequest):
    parsed = parse_ged_text(req.ged_text)
    persons: List[Person] = parsed["persons"]
    families: List[Family] = parsed["families"]
    db_dir = write_gwb(
        DATA_DIR,
        req.db_name,
        persons,
        families,
        req.notes_origin_file,
    )
    # Create a textual .gw alongside the JSON base
    from .storage import write_gw
    gw_path = write_gw(DATA_DIR, req.db_name, persons, families)
    return {
        "ok": True,
        "db_dir": str(db_dir),
        "gw_path": str(gw_path),
        "counts": {
            "persons": len(persons),
            "families": len(families),
        },
        "persons": [p.__dict__ for p in persons],
        "families": [f.__dict__ for f in families],
        "notes": parsed.get("notes", {}),
    }


@app.get("/")
def root():
    return RedirectResponse(url="/docs")