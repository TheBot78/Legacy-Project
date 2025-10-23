# GeneWeb – Project Overview

This repository contains:
- Front-end Flask apps under `front/` (served via Docker Compose)
- A Python backend utility library under `backend/`
- An RPC service under `geneweb-master/rpc/server/` (exposed via Docker Compose)
- Sample data under `data/`

## Quick Start (Docker)
From the project root, start all services:
- `docker compose up -d --build`
- Check running services: `docker compose ps`

Accessible URLs:
- Start (Flask): `http://localhost:2315/`
- Gwsetup (Flask): `http://localhost:2316/welcome?lang=fr`
- Geneweb (Flask): `http://localhost:2317/`
- RPC (FastAPI): POST `http://localhost:5050/rpc`

Restart services after changes:
- `docker compose restart start gwsetup geneweb rpc`

## Local Development
- Front-only without Docker:
  - `pip install -r front/requirements.txt`
  - Run Start: `python front/start/start_app.py`
  - Run Gwsetup: `python front/gwsetup/app.py`
  - Run Geneweb: `python front/geneweb/app.py`
- Backend utilities are pure Python modules under `backend/` and can be imported in your own scripts.

## Structure
- `front/`: Flask apps, templates, static files
- `backend/`: Python models, storage, parsing utilities
- `geneweb-master/`: Upstream GeneWeb sources and RPC server
- `data/`: Sample genealogy datasets (`.gw`, `.gwb`)
- `docker/`: Dockerfiles for services
- `docker-compose.yml`: Service definitions and ports

## Data
- `data/demo_gw.gwb/`: JSON-based dataset used for testing/demo
- `data/galichet.gw`: Sample legacy GeneWeb format

## Notes
- The front uses a shared custom 404 page across Flask apps.
- The RPC service returns JSON responses and includes a `ping` method for testing.
- For detailed front usage, see `front/README.md`.