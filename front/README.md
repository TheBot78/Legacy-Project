# GeneWeb Front – Guide de démarrage

Ce dossier contient les applications Flask qui fournissent les pages d’accueil et d’administration côté front de GeneWeb.

## Aperçu
- Trois applications Flask:
  - `start` (port `2315`): page d’accueil multilingue (`geneweb.html`).
  - `gwsetup` (port `2316`): page de gestion/creation (`welcome.html`).
  - `geneweb` (port `2317`): accès aux arbres (`choose_genealogy.html`).
- Un service RPC (port `5050` mappé vers `2316` en container) pour les appels JSON.
- Templates HTML sous `front/templates` et assets sous `front/static`.

## Prérequis
- Docker Desktop installé et démarré.
- Optionnel (développement local hors Docker): Python 3.11 et `pip`.

## Démarrage rapide (Docker)
- Depuis la racine du projet:
  - `docker compose up --build`
  - ou en mode détaché: `docker compose up -d --build`
- Services et URLs:
  - `start`: `http://localhost:2315/`
  - `gwsetup`: `http://localhost:2316/welcome?lang=fr`
  - `geneweb`: `http://localhost:2317/`
  - `rpc`: POST `http://localhost:5050/rpc`
- Redémarrer après modifications:
  - `docker compose restart start gwsetup geneweb rpc`
- Voir l’état:
  - `docker compose ps`

## Accès aux pages
- `start` affiche `geneweb.html` et détecte automatiquement la langue du navigateur.
- `gwsetup` redirige `/` vers `/welcome` et accepte `?lang=xx`.
- `geneweb` redirige `/` vers `/choose_genealogy` et accepte `?lang=xx`.
- `front/app.py` (non utilisé par Docker Compose) propose une page principale et un ping RPC si lancé seul.

## Développement local (sans Docker)
1. Installer les dépendances:
   - `pip install -r front/requirements.txt`
2. Lancer chaque app séparément:
   - Start: `python front/start/start_app.py` → `http://localhost:2315/`
   - Gwsetup: `python front/gwsetup/app.py` → `http://localhost:2316/welcome?lang=fr`
   - Geneweb: `python front/geneweb/app.py` → `http://localhost:2317/`

## Structure du front
- `front/templates/`:
  - `geneweb.html`: page d’accueil multilingue.
  - `welcome.html`: page de gestion (gwsetup).
  - `choose_genealogy.html`: sélection/accès aux bases.
  - `main.html`: menu simple (utilisé par `front/app.py`).
  - `404.html`: page d’erreur personnalisée pour routes inconnues.
- `front/static/`: images, css, fichiers de langues.

## Internationalisation
- Les pages supportent `?lang=de|en|es|fr|it|lv|nl|no|fi|sv`.
- Les liens dans `geneweb.html` passent `lang` pour ouvrir les pages dans la langue souhaitée.

## Erreurs 404
- Une page 404 personnalisée (`front/templates/404.html`) est rendue par chaque app Flask.
- Exemple: `http://localhost:2316/nonexistent` affiche la 404 avec liens utiles.
- Le service RPC renvoie un JSON structuré pour 404:
  ```json
  {"error":"Not Found","detail":"Endpoint not found","path":"/missing"}
  ```

## Journalisation et débogage
- Voir les logs:
  - `docker compose logs -f start`
  - `docker compose logs -f gwsetup`
  - `docker compose logs -f geneweb`
  - `docker compose logs -f rpc`
- Les containers montent `./front` en volume: modifications des templates visibles immédiatement (Flask en mode debug).

## Dépannage
- Port déjà utilisé: changer les ports dans `docker-compose.yml` ou arrêter le processus en conflit.
- Page "Not Found" par défaut: vérifier que le container a bien redémarré et que les handlers 404 sont chargés.
- Ressources statiques: les chemins dans les templates utilisent `static/...`; vérifier que `front/static` est présent.

## RPC – Ping de test
- Requête:
  ```bash
  curl -X POST http://localhost:5050/rpc \
    -H "Content-Type: application/json" \
    -d '{"method":"ping","params":{}}'
  ```
- Réponse:
  ```json
  {"result":"pong"}
  ```

## Notes
- `welcome.html` contient beaucoup de liens hérités du projet GeneWeb; pour une navigation intégrée Flask, utilisez `url_for` et passez `lang` si nécessaire.
- Les pages et styles peuvent être harmonisés via `front/templates/base.html` si besoin.