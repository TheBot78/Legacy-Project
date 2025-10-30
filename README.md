# GeneWeb Project - Management Interface (gwsetup)

## Overview

This project provides a comprehensive web interface for managing GeneWeb genealogy databases. It consists of a Python (Flask) frontend that communicates with a backend API to perform database operations. The entire project is orchestrated using Docker and Docker Compose for a consistent development and deployment environment.

## Project Context

This project is inspired by and intended to be a modern companion to the original GeneWeb software.
The original GeneWeb, first developed by Daniel de Rauglaudre at INRIA (France) in the 1990s, is a powerful, open-source genealogy program. It is distinguished by its high performance, robust relationship-path calculations, and its own persistent web server (gwd), all written in OCaml.

This new project provides a similar set of management tools and a modern viewing interface, built on a more common web stack (Python/Flask, Docker, and a separate backend API). It interfaces with the core `.gwb` database format by parsing `.gw` and GEDCOM files and writing a strict, classic GeneWeb base folder (`.gwb`).

## Features

### Database Import

* **From GEDCOM**: Import a database from a GEDCOM file (`.ged`) using a server-side file explorer.
* **From GeneWeb Source**: Import from a GeneWeb source file (`.gw`) using the file explorer.
* **From Empty**: Create a new, empty database with a specified name.

### Database Management

* **List Databases**: View all existing databases.
* **Rename Database**: Change the name of an existing database (frontend UI is complete; backend logic is pending).
* **Delete Database**: Remove one or more databases, including a multi-step confirmation process (frontend UI is complete; backend logic is pending).

### File Explorer

A secure, server-side, read-only file browser allows users to select import files from a pre-defined Docker volume (`~/` on the host, mapped to `/host_files` in the container).

## Project Structure

```
├── backend/
│   ├── api.py
│   ├── storage.py
│   ├── gw_parser.py
│   ├── ged_parser.py
│   ├── models.py
│   ├── bases/
│   │   ├── json_bases/
│   │   │   └── {db}/
│   │   └── {db}.gwb/
├── data/
│   └── Harry-Potter.ged
├── front/
│   ├── gwsetup/
│   ├── geneweb/
│   └── start/
├── docker/
│   ├── Dockerfile
│   └── Dockerfile.flask
├── docker-compose.yml
└── run.sh
```

## Database Output

* **Strict Classic Output**: `backend/bases/{db}.gwb/` contains only classic GeneWeb files.
* **API-Friendly JSON**: `backend/bases/json_bases/{db}/` contains JSON representations used by the API.

## Prerequisites

* Docker
* Docker Compose (typically included with Docker Desktop)

## Getting Started (Docker)

Make the script executable:

```bash
chmod +x run.sh
```

### Run All Services (Front + Back)

```bash
./run.sh
# or
./run.sh all
```

### Run Frontend Only

```bash
./run.sh front
```

### Run Backend Only

```bash
./run.sh back
```

### Stop All Services

```bash
./run.sh down
```

## Backend Development (Standalone)

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .\.venv\Scripts\activate  on Windows
pip install -r backend/requirements.txt
uvicorn backend.api:app --reload
```

Access API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Example linting:

```bash
pycodestyle --max-line-length=100 backend/api.py backend/storage.py
```

## Service Access

* Start/Landing Interface: [http://localhost:2315](http://localhost:2315)
* Management (gwsetup): [http://localhost:2316](http://localhost:2316)
* Homepage: [http://localhost:2316/welcome](http://localhost:2316/welcome)
* Viewing (geneweb): [http://localhost:2317](http://localhost:2317)
* RPC Service: [http://localhost:5050](http://localhost:5050)
* Backend API: [http://localhost:8000](http://localhost:8000)

## Development Status

* Core management features for creating, renaming, and deleting databases are implemented on the frontend.
* Current focus: family tree search functionality in the geneweb viewer.
* Next steps:

  * Implement backend logic for rename and delete.
  * Build search API and frontend components.
  * Enhance geneweb viewer with relationship path finding.

## Backend API Endpoints

### Current Endpoints

* **GET /dbs**: Retrieve list of databases.
* **GET /db/{db_name}/stats**: Retrieve stats for a specific database (`backend/bases/json_bases/{db}/base.json`).
* **POST /import_ged**: Create a new database from a GEDCOM text string.
  Payload: `{ "db_name": "...", "ged_text": "...", "notes_origin_file": "..." }`
* **POST /import_gw**: Create a database from `.gw` source text. Payload: `{ "db_name": "...", "gw_text": "...", "notes_origin_file": "..." }`
* **POST /db/rename**: Rename a database. Payload: `{ "old_db_name": "...", "new_db_name": "..." }`
* **POST /db/delete**: Delete a database. Payload: `{ "db_name": "..." }`

## License

No license file is included. Use at your discretion for local testing and prototyping.
