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
        # Fallback pour lire le fichier 'base' du dossier .gwb
        base_path = BASES_DIR / f"{db_name}.gwb" / "base"
        if not base_path.exists():
            raise HTTPException(status_code=404, detail="Base not found")
    
    try:
        base = json.loads(base_path.read_text(encoding="utf-8"))
        # Le fichier 'base' de galichet ne contient que les comptes
        if "persons_count" in base:
            return {"persons": base.get("persons_count"), "families": base.get("families_count")}
        return base.get("counts", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse base file: {str(e)}")


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
    dbs = []
    
    if json_bases_dir.exists():
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

    # Vérifie aussi les dossiers .gwb classiques qui n'ont pas de json_base
    for p in sorted(BASES_DIR.iterdir()):
        if p.is_dir() and p.suffix == ".gwb":
            db_name = p.stem
            if db_name not in dbs:
                dbs.append(db_name)
                
    return sorted(list(set(dbs))) # Retourne une liste unique triée

@app.delete("/db/{db_name}")
def delete_db(db_name: str):
    # Cible les deux dossiers
    json_dir = BASES_DIR / "json_bases" / db_name
    gwb_dir = BASES_DIR / f"{db_name}.gwb"
    
    matches = [p for p in [json_dir, gwb_dir] if p.exists() and p.is_dir()]
    
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

    # Cible les deux dossiers
    json_dir_old = BASES_DIR / "json_bases" / old_name
    gwb_dir_old = BASES_DIR / f"{old_name}.gwb"
    matches = [p for p in [json_dir_old, gwb_dir_old] if p.exists() and p.is_dir()]

    if not matches:
        raise HTTPException(status_code=404, detail="Database not found")

    renamed = []
    failed = []

    for src in matches:
        target = src.parent / (new_name if src.name == old_name else f"{new_name}.gwb")
        
        if target.exists() and target != src:
            failed.append({"path": str(src), "error": f"Target already exists: {target}"})
            continue
        try:
            src.rename(target)
            renamed.append({"from": str(src), "to": str(target)})

            # Met à jour le base.json si c'est le dossier json_bases
            if src.name == old_name: # C'est json_dir
                base_json = target / "base.json"
                if base_json.exists():
                    try:
                        base = json.loads(base_json.read_text(encoding="utf-8"))
                        base["name"] = new_name
                        base_json.write_text(json.dumps(base, ensure_ascii=False, indent=2), encoding="utf-8")
                    except Exception:
                        failed.append({"path": str(base_json), "error": "failed to update base.json name"})
        except Exception as e:
            failed.append({"path": str(src), "error": str(e)})

    if failed:
        return {"ok": False, "renamed": renamed, "failed": failed}
    return {"ok": True, "renamed": renamed}


def load_db_file(db_name: str, filename: str, is_json: bool = True):
    """Helper to load a file from json_bases or .gwb"""
    file_path = BASES_DIR / "json_bases" / db_name / filename
    if not file_path.exists():
        file_path = BASES_DIR / f"{db_name}.gwb" / filename
        if not file_path.exists():
             raise HTTPException(status_code=404, detail=f"{filename} not found for database {db_name}")
    try:
        content = file_path.read_text(encoding="utf-8")
        # Les .dat sont juste des listes de strings, un par ligne.
        if is_json:
            return json.loads(content)
        else:
            # Pour snames.dat, fnames.dat
            return [line for line in content.splitlines() if line.strip() and not line.startswith("#")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse {filename}: {str(e)}")


@app.get("/db/{db_name}/search")
def search_db(db_name: str, n: Optional[str] = None, p: Optional[str] = None):
    if not n and not p:
        raise HTTPException(status_code=400, detail="Search query (n or p) is required")

    try:
        base_data = None
        snames_list = []
        fnames_list = []
        persons_list = []
        string_table = {} 
        is_gedcom_format = False

        try:
            base_data = load_db_file(db_name, "base.json", is_json=True)
            if "strings" in base_data:
                is_gedcom_format = True
                string_list = base_data.get("strings", [])
                for s_id, text in enumerate(string_list):
                    string_table[s_id] = text
                snames_list = string_list
                fnames_list = string_list
                persons_list = base_data.get("persons", [])
                if not persons_list and base_data.get("persons_by_id"):
                     persons_list = base_data.get("persons_by_id").values()
            
        except HTTPException:
            pass # Fichier non trouvé, on suppose le format GW
        except Exception as e:
             return {"ok": False, "error": f"Error loading base.json: {str(e)}", "results": []}

        if not is_gedcom_format:
            try:
                if not base_data:
                    base_data = load_db_file(db_name, "base", is_json=True) # Fichier "base" pour galichet
                
                snames_list = load_db_file(db_name, "snames.dat", is_json=False)
                fnames_list = load_db_file(db_name, "fnames.dat", is_json=False)
                
                # Le format GW (d'après vos fichiers) n'a pas de liste "persons"
                # Nous devons la reconstruire en lisant le .gw brut
                gw_text = (BASES_DIR / f"{db_name}.gw").read_text(encoding="utf-8")
                parsed = parse_gw_text(gw_text)
                persons_list = [p.__dict__ for p in parsed["persons"]]
            except Exception as e:
                 return {"ok": False, "error": f"Failed to load GW data for search: {str(e)}", "results": []}

        matching_surname_ids = set()
        matching_firstname_ids = set()
        
        crushed_n = crush_name(n) if n else None
        crushed_p = crush_name(p) if p else None

        if n:
            for i, name in enumerate(snames_list):
                if crush_name(name) == crushed_n:
                    matching_surname_ids.add(i)
        
        if p:
            for i, name in enumerate(fnames_list):
                if crush_name(name) == crushed_p:
                    matching_firstname_ids.add(i)

        results = []
        
        for person in persons_list:
            found = False
            
            if is_gedcom_format:
                surname_id = person.get("surname_id")
                firstname_ids = person.get("first_name_ids", [])
                
                if n and surname_id in matching_surname_ids:
                    found = True
                
                if p and not found:
                    if any(fn_id in matching_firstname_ids for fn_id in firstname_ids):
                        found = True
            
            else:
                surname_str = person.get("surname", "")
                first_names_list = person.get("first_names", [])

                if n and crush_name(surname_str) == crushed_n:
                    found = True
                
                if p and not found:
                    if any(crush_name(fn) == crushed_p for fn in first_names_list):
                        found = True

            if found:
                # Reconstruire l'objet Personne avec les vrais noms
                if is_gedcom_format:
                    surname_id = person.get("surname_id")
                    firstname_ids = person.get("first_name_ids", [])
                    surname = string_table.get(surname_id, "?")
                    first_names = [string_table.get(fn_id, "?") for fn_id in firstname_ids]

                    birth_date_id = person.get("birth_date_id")
                    death_date_id = person.get("death_date_id")
                    birth_place_id = person.get("birth_place_id")
                    death_place_id = person.get("death_place_id")

                    birth_date = string_table.get(birth_date_id, "") if birth_date_id is not None else ""
                    death_date = string_table.get(death_date_id, "") if death_date_id is not None else ""
                    birth_place = string_table.get(birth_place_id, "") if birth_place_id is not None else ""
                    death_place = string_table.get(death_place_id, "") if death_place_id is not None else ""
                
                else:
                    surname = person.get("surname", "?")
                    first_names = person.get("first_names", ["?"])
                    birth_date = person.get("birth_date", "") or ""
                    death_date = person.get("death_date", "") or ""
                    birth_place = person.get("birth_place", "") or ""
                    death_place = person.get("death_place", "") or ""

                results.append({
                    "id": person.get("id"),
                    "surname": surname,
                    "first_names": first_names,
                    "sex": person.get("sex"),
                    "birth_date": birth_date,
                    "birth_place": birth_place,
                    "death_date": death_date,
                    "death_place": death_place
                })
                
    except HTTPException as e:
        return {"ok": False, "error": e.detail, "results": []}
    except Exception as e:
        return {"ok": False, "error": str(e), "results": []}

    return {"ok": True, "results": results}