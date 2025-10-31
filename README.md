# GeneWeb Project – Modern Python Management Interface (gwsetup)

🧬 Overview

This project is a modern reimplementation of GeneWeb’s management interface, providing a FastAPI-based backend and an optional Flask frontend for database handling and visualization. It supports importing, creating, renaming, and deleting genealogy databases while maintaining compatibility with GeneWeb’s .gwb structure.

⚙️ Project Context

Inspired by the original GeneWeb (Daniel de Rauglaudre, INRIA, 1990s), this Python rewrite offers:

- A FastAPI backend for database management and APIs.
- A Dockerized architecture for consistent development and deployment.
- GEDCOM (.ged) and GeneWeb (.gw) parsing and conversion.
- JSON and classic .gwb outputs for legacy compatibility.

✨ Features

🧩 Database Import

- From GEDCOM (.ged): POST /import_ged — parses GEDCOM and generates .gwb + JSON base.
- From GeneWeb source (.gw): POST /import_gw — parses .gw text and generates outputs.
- From structured JSON: POST /import — import directly from JSON objects (persons, families).

🗂️ Database Management

- List Databases → GET /dbs (json_bases + .gwb folders)
- Database Statistics → GET /db/{db_name}/stats (reads base.json or legacy base file)
- Rename Database → POST /db/{old_name}/rename (payload: { "new_name": "..." })
- Delete Database → DELETE /db/{db_name} (removes .gwb and json_bases entry)

🧭 Parsing Utilities

- Parse GeneWeb source → POST /parse_gw (returns structured persons/families/notes and counts)

💾 File Outputs

Each import produces:

- Classic GeneWeb: backend/bases/{db}.gwb/ (legacy GeneWeb files)
- API JSON Base: backend/bases/json_bases/{db}/ (JSON used by the API)
- GW / GWF files: textual .gw and .gwf exports

🧱 Project Structure

```
├── backend/
│   ├── api.py                # FastAPI main backend
│   ├── storage.py            # Read/write helpers for .gwb & JSON
│   ├── gw_parser.py          # GeneWeb text parser
│   ├── ged_parser.py         # GEDCOM parser
│   ├── models.py             # Core data structures
│   ├── bases/
│   │   ├── json_bases/
│   │   │   └── {db}/
│   │   └── {db}.gwb/
├── data/
├── front/
│   ├── gwsetup/              # Management interface (Flask)
│   ├── geneweb/              # Tree viewer (Flask)
│   └── start/
├── docker/
│   ├── Dockerfile
│   └── Dockerfile.flask
├── docker-compose.yml
└── run.sh
```

🐳 Running with Docker

Make the helper script executable:

```bash
chmod +x run.sh
```

Run all services:

```bash
./run.sh all
```

Run only backend (FastAPI):

```bash
./run.sh back
```

Run only frontend (Flask):

```bash
./run.sh front
```

Stop services:

```bash
./run.sh down
```

🧑‍💻 Local Backend Development

Create venv and run:

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
pip install -r backend/requirements.txt
uvicorn backend.api:app --reload
```

Access API docs: http://127.0.0.1:8000/docs

🌐 Service Access (defaults)

- Start / Landing Interface: http://localhost:2315
- Management (gwsetup): http://localhost:2316
- Viewer (geneweb): http://localhost:2317
- RPC Service: http://localhost:5050
- Backend API: http://localhost:8000

🔗 API Endpoints Summary

| Method | Endpoint                        | Description                                      |
|--------|---------------------------------|--------------------------------------------------|
| GET    | /                               | Redirect to /docs                               |
| GET    | /dbs                            | List available databases                         |
| GET    | /db/{db_name}/stats             | Retrieve database statistics                     |
| POST   | /import                         | Import database from JSON structures             |
| POST   | /import_gw                      | Import database from .gw text                   |
| POST   | /import_ged                     | Import database from .ged text                  |
| POST   | /parse_gw                       | Parse .gw content without saving                |
| POST   | /db/{old_name}/rename           | Rename an existing database                      |
| DELETE | /db/{db_name}                   | Delete database and JSON base                   |

📄 Documentation

Project documentation is available in the repository root `docs/` directory:

- docs/Plan de tests – GeneWeb (Legacy).pdf
- docs/QA-Strategy.pdf

📄 License

No license file included — use freely for local development, experimentation, and education.
