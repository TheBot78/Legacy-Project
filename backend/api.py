from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
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

# --- NOUVELLE LOGIQUE DE RECHERCHE ---

# Classe pour typer la structure de l'arbre
class PersonNode(BaseModel):
    id: int
    surname: str
    first_names: List[str]
    birth_date: str = ""
    death_date: str = ""
    sex: Optional[str] = None
    spouse: Optional['PersonNode'] = None
    children: List['PersonNode'] = []

# Met à jour la classe pour permettre les références circulaires
PersonNode.model_rebuild()


class SearchContext:
    """Classe Helper pour stocker les données chargées pendant une recherche."""
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.persons_list: List[Dict] = []
        self.families_list: List[Dict] = []
        self.persons_by_id: Dict[int, Dict] = {}
        self.families_by_person_id: Dict[int, List[Dict]] = {} # Familles où la personne est parent
        self.families_by_child_id: Dict[int, Dict] = {} # Famille où la personne est enfant
        self.string_table: Dict[int, str] = {}
        self.snames_list: List[str] = []
        self.fnames_list: List[str] = []
        self.is_gedcom_format: bool = False
        self._load_data()

    def _load_data(self):
        try:
            base_data = load_db_file(self.db_name, "base.json", is_json=True)
            if "strings" in base_data:
                self.is_gedcom_format = True
                string_list = base_data.get("strings", [])
                for s_id, text in enumerate(string_list):
                    self.string_table[s_id] = text
                self.snames_list = string_list
                self.fnames_list = string_list
                self.persons_list = base_data.get("persons", [])
                if not self.persons_list and base_data.get("persons_by_id"):
                     self.persons_list = list(base_data.get("persons_by_id").values())
                self.families_list = base_data.get("families", [])
            
        except HTTPException:
            pass # Fichier non trouvé, on suppose le format GW
        except Exception as e:
             raise HTTPException(status_code=500, detail=f"Error loading base.json: {str(e)}")

        if not self.is_gedcom_format:
            try:
                self.snames_list = load_db_file(self.db_name, "snames.dat", is_json=False)
                self.fnames_list = load_db_file(self.db_name, "fnames.dat", is_json=False)
                gw_text = (BASES_DIR / f"{self.db_name}.gw").read_text(encoding="utf-8")
                parsed = parse_gw_text(gw_text)
                self.persons_list = [p.__dict__ for p in parsed["persons"]]
                self.families_list = [f.__dict__ for f in parsed["families"]]
            except Exception as e:
                 raise HTTPException(status_code=500, detail=f"Failed to load GW data for search: {str(e)}")
        
        # Créer des index pour un accès rapide
        for p in self.persons_list:
            self.persons_by_id[p["id"]] = p
            
        for f in self.families_list:
            if f.get("husband_id") is not None:
                self.families_by_person_id.setdefault(f["husband_id"], []).append(f)
            if f.get("wife_id") is not None:
                self.families_by_person_id.setdefault(f["wife_id"], []).append(f)
            for child_id in f.get("children_ids", []):
                self.families_by_child_id[child_id] = f

    def _build_person_node(self, person_id: int) -> PersonNode:
        """Construit un nœud de personne simple (sans enfants/conjoint)."""
        person = self.persons_by_id.get(person_id)
        if not person:
            return None

        if self.is_gedcom_format:
            surname_id = person.get("surname_id")
            firstname_ids = person.get("first_name_ids", [])
            surname = self.string_table.get(surname_id, "?")
            first_names = [self.string_table.get(fn_id, "?") for fn_id in firstname_ids]
            birth_date_id = person.get("birth_date_id")
            death_date_id = person.get("death_date_id")
            birth_date = self.string_table.get(birth_date_id, "") if birth_date_id is not None else ""
            death_date = self.string_table.get(death_date_id, "") if death_date_id is not None else ""
        else:
            surname = person.get("surname", "?")
            first_names = person.get("first_names", ["?"])
            birth_date = person.get("birth_date", "") or ""
            death_date = person.get("death_date", "") or ""

        return PersonNode(
            id=person_id,
            surname=surname,
            first_names=first_names,
            sex=person.get("sex"),
            birth_date=birth_date,
            death_date=death_date,
        )

    def _build_branch(self, person_id: int, processed_ids: set) -> Optional[PersonNode]:
        """Construit récursivement une branche à partir d'un individu."""
        if person_id in processed_ids:
            return None # Éviter les boucles infinies
        
        person_node = self._build_person_node(person_id)
        if not person_node:
            return None
            
        processed_ids.add(person_id)
        
        # Trouver les conjoints et les enfants
        families_as_parent = self.families_by_person_id.get(person_id, [])
        
        # Pour cet affichage, prenons la première famille trouvée
        if families_as_parent:
            fam = families_as_parent[0] # Simplification
            spouse_id = None
            if fam.get("husband_id") == person_id:
                spouse_id = fam.get("wife_id")
            else:
                spouse_id = fam.get("husband_id")

            if spouse_id:
                person_node.spouse = self._build_person_node(spouse_id)
            
            for child_id in fam.get("children_ids", []):
                child_node = self._build_branch(child_id, processed_ids)
                if child_node:
                    person_node.children.append(child_node)

        return person_node

    def find_by_list(self, crushed_n: str, crushed_p: str) -> List[Dict]:
        """Recherche simple (liste)."""
        matching_surname_ids = set()
        matching_firstname_ids = set()
        
        if crushed_n:
            for i, name in enumerate(self.snames_list):
                if crush_name(name) == crushed_n:
                    matching_surname_ids.add(i)
        
        if crushed_p:
            for i, name in enumerate(self.fnames_list):
                if crush_name(name) == crushed_p:
                    matching_firstname_ids.add(i)

        results = []
        for person in self.persons_list:
            found = False
            
            if self.is_gedcom_format:
                surname_id = person.get("surname_id")
                firstname_ids = person.get("first_name_ids", [])
                
                if crushed_n and surname_id not in matching_surname_ids:
                    continue # Doit correspondre au nom si fourni
                if crushed_p and not any(fn_id in matching_firstname_ids for fn_id in firstname_ids):
                    continue # Doit correspondre au prénom si fourni
                
                # Si on arrive ici, la personne correspond
                found = True

            else: # Format GW
                surname_str = person.get("surname", "")
                first_names_list = person.get("first_names", [])

                if crushed_n and crush_name(surname_str) != crushed_n:
                    continue
                if crushed_p and not any(crush_name(fn) == crushed_p for fn in first_names_list):
                    continue
                
                found = True

            if found:
                node = self._build_person_node(person.get("id"))
                if node:
                    # Renvoyer un dict simple pour le tableau, pas un objet Pydantic
                    results.append(node.model_dump())
        return results

    def find_by_surname_tree(self, crushed_n: str) -> List[PersonNode]:
        """Recherche le nom de famille et construit les arbres."""
        
        # 1. Trouver tous les individus avec ce nom de famille
        person_ids_with_surname = set()
        if self.is_gedcom_format:
            matching_surname_ids = set()
            for i, name in enumerate(self.snames_list):
                if crush_name(name) == crushed_n:
                    matching_surname_ids.add(i)
            for p in self.persons_list:
                if p.get("surname_id") in matching_surname_ids:
                    person_ids_with_surname.add(p["id"])
        else:
            for p in self.persons_list:
                if crush_name(p.get("surname", "")) == crushed_n:
                    person_ids_with_surname.add(p["id"])

        # 2. Trouver les "racines" (ceux dont les parents N'ONT PAS ce nom)
        root_ids = set()
        for pid in person_ids_with_surname:
            parent_family = self.families_by_child_id.get(pid)
            if not parent_family:
                root_ids.add(pid) # Pas de parents, c'est une racine
                continue

            father_id = parent_family.get("husband_id")
            mother_id = parent_family.get("wife_id")

            # Si les deux parents n'ont pas ce nom de famille, c'est une racine
            if father_id not in person_ids_with_surname and mother_id not in person_ids_with_surname:
                 root_ids.add(pid)
            # Cas spécial : un parent l'a, l'autre n'existe pas
            elif (father_id and father_id not in person_ids_with_surname and not mother_id):
                 root_ids.add(pid)
            elif (mother_id and mother_id not in person_ids_with_surname and not father_id):
                 root_ids.add(pid)

        # 3. Construire les branches à partir des racines
        branches = []
        processed_ids = set() # Pour éviter les doublons et les boucles
        for rid in sorted(list(root_ids)):
            branch = self._build_branch(rid, processed_ids)
            if branch:
                branches.append(branch)
        
        return branches


@app.get("/db/{db_name}/search")
def search_db(db_name: str, n: Optional[str] = None, p: Optional[str] = None):
    if not n and not p:
        raise HTTPException(status_code=400, detail="Search query (n or p) is required")

    try:
        ctx = SearchContext(db_name)
        crushed_n = crush_name(n) if n else None
        crushed_p = crush_name(p) if p else None

        # --- NOUVELLE LOGIQUE DE VUE ---
        # Si un prénom (p) est fourni, OU si aucun nom (n) n'est fourni,
        # OU si la recherche par arbre ne renvoie rien, on utilise la vue "liste".
        
        results_tree = []
        if crushed_n and not crushed_p:
            results_tree = ctx.find_by_surname_tree(crushed_n)

        if results_tree:
            # Mode Arbre (ex: "Potter")
            return {
                "ok": True, 
                "view_mode": "tree",
                "results": [branch.model_dump() for branch in results_tree]
            }
        else:
            # Mode Liste (ex: "Harry Potter" ou "Harry" ou "Potter" sans racines)
            results_list = ctx.find_by_list(crushed_n, crushed_p)
            return {
                "ok": True, 
                "view_mode": "list",
                "results": results_list
            }
                
    except HTTPException as e:
        return {"ok": False, "error": e.detail, "results": []}
    except Exception as e:
        return {"ok": False, "error": str(e), "results": []}