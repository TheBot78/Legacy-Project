import os
import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(
    __name__,
    static_folder="../static",
    template_folder="../templates"
)

# --- Fonctions Helper ---

def get_backend_candidates():
    candidates = []
    if os.environ.get("BACKEND_URL"):
        candidates.append(os.environ.get("BACKEND_URL"))
    candidates.append("http://127.0.0.1:8000")
    candidates.append("http://localhost:8000")
    candidates.append("http://host.docker.internal:8000")
    return candidates

def get_all_dbs():
    databases = []
    error = None
    base_candidates = [
        os.environ.get("BACKEND_BASE", "http://127.0.0.1:8000"),
        "http://localhost:8000",
        "http://host.docker.internal:8000",
    ]
    for root in base_candidates:
        try:
            r = requests.get(f"{root.rstrip('/')}/dbs", timeout=10)
            if r.status_code == 200:
                databases = r.json()
                return databases, None
            error = f"HTTP {r.status_code}"
        except Exception as e:
            error = str(e)
    return databases, error

def get_db_stats(db_name):
    stats = {}
    error = None
    base_candidates = [
        os.environ.get("BACKEND_BASE", "http://127.0.0.1:8000"),
        "http://localhost:8000",
        "http://host.docker.internal:8000",
    ]
    for root in base_candidates:
        try:
            r = requests.get(f"{root.rstrip('/')}/db/{db_name}/stats", timeout=10)
            if r.status_code == 200:
                stats = r.json()
                return stats, None
            error = f"HTTP {r.status_code}"
        except Exception as e:
            error = str(e)
    return stats, error

# --- Routes de l'application ---

@app.route("/")
def home():
    return redirect(url_for("choose_genealogy"))

@app.route("/choose_genealogy")
def choose_genealogy():
    lang = request.args.get("lang", "en")
    db_name = request.args.get("b")

    if db_name:
        return redirect(url_for("search_page", db_name=db_name, lang=lang))

    databases, error = get_all_dbs()

    return render_template(
        "choose_genealogy.html",
        lang=lang,
        databases=databases,
        error=error
    )

@app.route("/<db_name>")
def search_page(db_name):
    lang = request.args.get("lang", "en")

    stats, error = get_db_stats(db_name)

    if error:
        return redirect(url_for("choose_genealogy", lang=lang, error=f"Database '{db_name}' not found."))

    return render_template(
        "search/search.html",
        lang=lang,
        db_name=db_name,
        stats=stats
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2317, debug=True)
