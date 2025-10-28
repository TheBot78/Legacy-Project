# Python Backend (GeneWeb-like)

A small Python backend that parses GeneWeb `.gw` and GEDCOM files and writes a strict classic GeneWeb base folder (`.gwb`). It also produces API-friendly JSON files, but these are stored outside the `.gwb` directory to keep the classic layout pristine.

## Overview
- Strict classic output: `backend/bases/{db}.gwb` contains only GeneWeb-style files.
- JSON for API/testing: `backend/bases/json_bases/{db}/` holds `base.json`, `base.acc.json`, `names.inx.json`, `strings.inx.json`.
- Convenience files: `backend/bases/{db}.gw` and `backend/bases/{db}.gwf` are created next to the `.gwb` folder.

## Project Layout
- `backend/api.py` FastAPI endpoints.
- `backend/storage.py` writers for `.gwb`, `.gw`, `.gwf`, and JSON bases.
- `backend/gw_parser.py`, `backend/ged_parser.py` parsers.
- `backend/bases/` output directory.
- `data/` sample inputs and example classic `.gwb` (Harry-Potter).

## Strict GeneWeb Base Output
Classic files created under `backend/bases/{db}.gwb/`:
- `particles.txt`, `snames.dat`, `fnames.dat`
- `snames.inx`, `fnames.inx`, `names.inx`, `names.acc`
- `strings.inx`, `nb_persons`, `base`, `base.acc`

JSON base (for API/testing) is stored in `backend/bases/json_bases/{db}/`:
- `base.json`, `base.acc.json`, `names.inx.json`, `strings.inx.json`

## API Endpoints
- `POST /import_gw` → writes strict classic `.gwb`, `*.gw`, `*.gwf`, and JSON to `json_bases/{db}`.
- `POST /import_ged` → same as above, taking GEDCOM text.
- `GET /db/{db}/stats` → reads counts from `backend/bases/json_bases/{db}/base.json`.

## Quickstart (Windows)
1) Create venv and install deps:
```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```
2) Run the API server:
```
uvicorn backend.api:app --reload
```
3) Open docs:
```
http://127.0.0.1:8000/docs
```

## Import Examples
- Import GEDCOM (Python):
```
from pathlib import Path
from backend.api import GwImportGEDRequest, import_ged
text = Path('data/Harry-Potter.ged').read_text(encoding='utf-8')
req = GwImportGEDRequest(db_name='Harry-Potter', ged_text=text, notes_origin_file='data/Harry-Potter.ged')
resp = import_ged(req)
print(resp)
```
- Stats via HTTP:
```
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/db/Harry-Potter/stats
```

## Verify Output
- Classic base: `backend/bases/Harry-Potter.gwb/` (only classic files).
- JSON base: `backend/bases/json_bases/Harry-Potter/`.
- Convenience: `backend/bases/Harry-Potter.gw`, `backend/bases/Harry-Potter.gwf`.

Note: The script `tmp_verify_import.py` previously checked for JSON inside the `.gwb` folder. With strict mode, it will report those JSON files as “missing” in `.gwb` by design. Check them under `backend/bases/json_bases/{db}/` or adapt the script accordingly.

## Development Notes
- Lint: `pycodestyle --max-line-length=100`.
- On PowerShell, prefer listing files explicitly instead of wildcards, e.g.:
```
pycodestyle --max-line-length=100 backend\api.py backend\storage.py backend\ged_parser.py backend\gw_parser.py backend\models.py backend\name_utils.py backend\indexes.py main.py
```

## License
No license file is included. Use at your discretion for local testing and prototyping.