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


BASES_DIR = Path(__file__).resolve().parent / "bases"
BASES_DIR.mkdir(exist_ok=True)

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

    db_dir = write_gwb(BASES_DIR, req.db_name, persons, families, req.notes_origin_file)
    # Écriture classique .gwb pour reproduire la structure Legacy-Project/data/*.gwb
    from .storage import write_gwb_classic, write_gw, write_gwf
    write_gwb_classic(BASES_DIR, req.db_name, persons, families)
    gw_path = write_gw(BASES_DIR, req.db_name, persons, families)
    gwf_path = write_gwf(BASES_DIR, req.db_name)
    return {"ok": True, "db_dir": str(db_dir), "gw_path": str(gw_path), "gwf_path": str(gwf_path)}


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


@app.get("/db/{db_name}/stats")
def stats(db_name: str):
    # Lire les JSON depuis backend/bases/json_bases/{db_name}/
    db_dir = BASES_DIR / "json_bases" / db_name
    base_path = db_dir / "base.json"
    if not base_path.exists():
        raise HTTPException(status_code=404, detail="Base not found")
    base = json.loads(base_path.read_text(encoding="utf-8"))
    return base.get("counts", {})


@app.post("/import_gw")
def import_gw(req: GwImportGWRequest):
    parsed = parse_gw_text(req.gw_text)
    persons: List[Person] = parsed["persons"]
    families: List[Family] = parsed["families"]
    # Écrit la structure classique .gwb strictement
    from .storage import write_gwb_classic, write_gw, write_gwf, write_json_base
    db_dir = write_gwb_classic(BASES_DIR, req.db_name, persons, families)
    # Écrit les JSON dans json_bases/{db}
    json_dir = write_json_base(BASES_DIR, req.db_name, persons, families, req.notes_origin_file)
    gw_path = write_gw(BASES_DIR, req.db_name, persons, families)
    gwf_path = write_gwf(BASES_DIR, req.db_name)
    return {
        "ok": True,
        "db_dir": str(db_dir),
        "json_dir": str(json_dir),
        "gw_path": str(gw_path),
        "gwf_path": str(gwf_path),
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
    # Écrit la structure classique .gwb strictement
    from .storage import write_gwb_classic, write_gw, write_gwf, write_json_base
    db_dir = write_gwb_classic(BASES_DIR, req.db_name, persons, families)
    # Écrit les JSON dans json_bases/{db}
    json_dir = write_json_base(BASES_DIR, req.db_name, persons, families, req.notes_origin_file)
    gw_path = write_gw(BASES_DIR, req.db_name, persons, families)
    gwf_path = write_gwf(BASES_DIR, req.db_name)
    return {
        "ok": True,
        "db_dir": str(db_dir),
        "json_dir": str(json_dir),
        "gw_path": str(gw_path),
        "gwf_path": str(gwf_path),
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

# end
