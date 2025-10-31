# GeneWeb Front – Quick Start Guide

This folder contains the Flask applications that serve GeneWeb's front pages.

## Overview
- Three Flask apps:
  - `start` (port `2315`): landing page (`geneweb.html`).
  - `gwsetup` (port `2316`): setup/management page (`welcome.html`).
  - `geneweb` (port `2317`): genealogy access (`choose_genealogy.html`).
- One RPC service (external port `5050`, mapped to container `2316`) for JSON calls.
- HTML templates under `front/templates` and assets under `front/static`.

## Prerequisites
- Docker Desktop installed and running.
- Optional (local dev without Docker): Python 3.11 and `pip`.

## Quick Start (Docker)
From the project root:
- Build and start:
  - `docker compose up --build`
  - or detached: `docker compose up -d --build`
- Services and URLs:
  - `start`: `http://localhost:2315/`
  - `gwsetup`: `http://localhost:2316/welcome?lang=fr`
  - `geneweb`: `http://localhost:2317/`
  - `rpc`: POST `http://localhost:5050/rpc`
- Restart after changes:
  - `docker compose restart start gwsetup geneweb rpc`
- Check status:
  - `docker compose ps`

## Page Access
- `start` serves `geneweb.html` and auto-detects browser language.
- `gwsetup` redirects `/` to `/welcome` and accepts `?lang=xx`.
- `geneweb` redirects `/` to `/choose_genealogy` and accepts `?lang=xx`.
- `front/app.py` (not used by Docker Compose) provides a simple main page and RPC ping if run standalone.

## Local Development (without Docker)
1. Install dependencies:
   - `pip install -r front/requirements.txt`
2. Run each app separately:
   - Start: `python front/start/start_app.py` → `http://localhost:2315/`
   - Gwsetup: `python front/gwsetup/app.py` → `http://localhost:2316/welcome?lang=fr`
   - Geneweb: `python front/geneweb/app.py` → `http://localhost:2317/`

## Front Structure
- `front/templates/`:
  - `geneweb.html`: multilingual landing page.
  - `welcome.html`: setup page (gwsetup).
  - `choose_genealogy.html`: select/access databases.
  - `main.html`: simple menu (used by `front/app.py`).
  - `404.html`: custom error page for unknown routes.
- `front/static/`: images, css, language files.

## Internationalization
- Pages support `?lang=de|en|es|fr|it|lv|nl|no|fi|sv`.
- Links in `geneweb.html` preserve `lang` to open pages in the selected language.

## 404 Errors
- A shared custom 404 page (`front/templates/404.html`) is rendered by each Flask app.
- Example: `http://localhost:2316/nonexistent` shows the helpful 404 page.
- The RPC service returns a structured JSON for 404:
  ```json
  {"error":"Not Found","detail":"Endpoint not found","path":"/missing"}
  ```

## Logging and Debugging
- Tail logs:
  - `docker compose logs -f start`
  - `docker compose logs -f gwsetup`
  - `docker compose logs -f geneweb`
  - `docker compose logs -f rpc`
- Containers mount `./front` as a volume: template changes are visible immediately (Flask debug).

## Troubleshooting
- Port in use: change ports in `docker-compose.yml` or stop the conflicting process.
- Default "Not Found" page appears: ensure the container restarted and 404 handlers loaded.
- Static assets: templates use `url_for('static', ...)`; verify files exist in `front/static`.

## RPC – Ping Test
- Request:
  ```bash
  curl -X POST http://localhost:5050/rpc \
    -H "Content-Type: application/json" \
    -d '{"method":"ping","params":{}}'
  ```
- Response:
  ```json
  {"result":"pong"}
  ```

## Notes
- `welcome.html` includes many legacy GeneWeb links; for consistent Flask navigation, prefer `url_for` and pass `lang` when relevant.
- Use `front/templates/base.html` to unify layout and navigation across pages if desired.