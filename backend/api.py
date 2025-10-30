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
import shutil
from pydantic import BaseModel as PydanticBaseModel


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
    from .storage import write_gwb_classic, write_gw, write_gwf, write_json_base
    db_dir = write_gwb_classic(BASES_DIR, req.db_name, persons, families)
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
    from .storage import write_gwb_classic, write_gw, write_gwf, write_json_base
    db_dir = write_gwb_classic(BASES_DIR, req.db_name, persons, families)
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


@app.get("/dbs")
def list_dbs():
    json_bases_dir = BASES_DIR / "json_bases"
    if not json_bases_dir.exists():
        return []

    dbs = []
    for p in sorted(json_bases_dir.iterdir()):
        if not p.is_dir():
            continue
        base_file = p / "base.json"
        if base_file.exists():
            try:
                base = json.loads(base_file.read_text(encoding="utf-8"))
                dbs.append(base.get("name", p.name))
            except Exception:
                dbs.append(p.name)
        else:
            dbs.append(p.name)
    return dbs

@app.delete("/db/{db_name}")
def delete_db(db_name: str):
    matches = [p for p in BASES_DIR.rglob(db_name) if p.is_dir() and p.name == db_name]
    if not matches:
        raise HTTPException(status_code=404, detail="Database not found")

    deleted = []
    failed = []
    for p in matches:
        try:
            shutil.rmtree(p)
            deleted.append(str(p))
        except Exception as e:
            failed.append({"path": str(p), "error": str(e)})

    if failed:
        return {"ok": False, "deleted": deleted, "failed": failed}
    return {"ok": True, "deleted": deleted}


class RenameRequest(PydanticBaseModel):
    new_name: str


@app.post("/db/{old_name}/rename")
def rename_db(old_name: str, req: RenameRequest):
    new_name = req.new_name.strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="new_name must not be empty")

    matches = [p for p in BASES_DIR.rglob(old_name) if p.is_dir() and p.name == old_name]
    if not matches:
        raise HTTPException(status_code=404, detail="Database not found")

    for src in matches:
        target = src.parent / new_name
        if target.exists() and target != src:
            raise HTTPException(status_code=400, detail=f"Target already exists: {target}")

    renamed = []
    failed = []
    for src in matches:
        target = src.parent / new_name
        try:
            src.rename(target)
            renamed.append({"from": str(src), "to": str(target)})

            base_json = target / "base.json"
            if base_json.exists():
                try:
                    base = json.loads(base_json.read_text(encoding="utf-8"))
                    base["name"] = new_name
                    base_json.write_text(json.dumps(base, ensure_ascii=False, indent=2), encoding="utf-8")
                except Exception:
                    failed.append({"path": str(base_json), "error": "failed to update base.json"})
        except Exception as e:
            failed.append({"path": str(src), "error": str(e)})

    if failed:
        return {"ok": False, "renamed": renamed, "failed": failed}
    return {"ok": True, "renamed": renamed}


def load_db_json(db_name: str, filename: str):
    """Helper pour charger un fichier JSON d'une base."""
    db_dir = BASES_DIR / "json_bases" / db_name
    file_path = db_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"{filename} not found for database {db_name}")
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse {filename}: {str(e)}")

@app.get("/db/{db_name}/search")
def search_db(db_name: str, n: Optional[str] = None, p: Optional[str] = None):
    if not n and not p:
        raise HTTPException(status_code=400, detail="Search query (n or p) is required")

    try:
        base = load_db_json(db_name, "base.json")
        names_inx = load_db_json(db_name, "names.inx.json")
    except HTTPException as e:
        return {"ok": False, "error": e.detail, "results": []}

    persons_by_id = base.get("persons_by_id", {})
    surname_idx = names_inx.get("surnames", {})
    firstname_idx = names_inx.get("firstnames", {})
    
    matching_ids = set()

    if n:
        crushed_n = crush_name(n)
        # *** CORRECTION ***
        # Itère sur les clés de l'index et compare les versions "crush"
        for surname_key, id_list in surname_idx.items():
            if crush_name(surname_key) == crushed_n:
                matching_ids.update(id_list)
    
    if p:
        crushed_p = crush_name(p)
        # *** CORRECTION ***
        # Itère sur les clés de l'index et compare les versions "crush"
        for firstname_key, id_list in firstname_idx.items():
            if crush_name(firstname_key) == crushed_p:
                matching_ids.update(id_list)

    results = []
    for person_id in matching_ids:
        person_data = persons_by_id.get(str(person_id))
        if person_data:
            results.append(person_data)

    return {"ok": True, "results": results}