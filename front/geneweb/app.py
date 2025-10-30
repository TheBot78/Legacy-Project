import os
import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, static_folder="../static",
            template_folder="../templates")


# --- Fonctions Helper ---

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

def call_backend_search(db_name, surname, firstname):
    """Appelle le backend pour les résultats de recherche."""
    print(f"Appel backend pour RECHERCHER {db_name} n: {surname} p: {firstname}")
    params = {"n": surname, "p": firstname}
    base_candidates = [
        os.environ.get("BACKEND_BASE", "http://127.0.0.1:8000"),
        "http://localhost:8000",
        "http://host.docker.internal:8000",
    ]
    for root in base_candidates:
        try:
            r = requests.get(f"{root.rstrip('/')}/db/{db_name}/search", params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get("ok"):
                    return data, None
                else:
                    return None, data.get("error", "Erreur backend inconnue")
            error = f"HTTP {r.status_code}"
        except Exception as e:
            error = str(e)
    return None, error

# --- NOUVELLE FONCTION HELPER ---
def call_backend_person(db_name, surname, firstname):
    """Appelle le backend pour les détails d'UNE personne."""
    print(f"Appel backend pour PERSONNE {db_name} n: {surname} p: {firstname}")
    
    # Le prénom peut contenir des espaces (ex: "Many Generations")
    # L'URL (`p=Many+Generations`) est gérée par requests
    params = {"n": surname, "p": firstname}
    
    base_candidates = [
        os.environ.get("BACKEND_BASE", "http://127.0.0.1:8000"),
        "http://localhost:8000",
        "http://host.docker.internal:8000",
    ]
    
    for root in base_candidates:
        try:
            r = requests.get(f"{root.rstrip('/')}/db/{db_name}/person", params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get("ok"):
                    return data.get("details"), None
                else:
                    return None, data.get("error", "Erreur backend inconnue")
            error = f"HTTP {r.status_code}"
        except Exception as e:
            error = str(e)
    return None, error
# --- FIN DE LA NOUVELLE FONCTION ---


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

# --- ROUTE PRINCIPALE MODIFIÉE ---
@app.route("/<db_name>")
def search_page(db_name):
    lang = request.args.get("lang", "en")
    m = request.args.get("m")
    n = request.args.get("n")
    p = request.args.get("p")

    # --- LOGIQUE DE RECHERCHE (m=S) ---
    if m == 'S' and (n or p):
        search_query = n or p # Priorité au nom de famille pour le titre
        
        search_data, error = call_backend_search(db_name, n or "", p or "")
        
        if error:
             return redirect(url_for("choose_genealogy", lang=lang, error=f"Search error: {error}"))

        results = search_data.get("results", [])
        view_mode = search_data.get("view_mode", "list") # 'list' par défaut

        return render_template(
            "search/search_name.html",
            lang=lang,
            db_name=db_name,
            search_query=search_query,
            results=results,
            view_mode=view_mode 
        )
    
    # --- NOUVELLE LOGIQUE : VUE PERSONNE (n et p SANS m=S) ---
    if n and p and m != 'S':
        # Les prénoms avec des espaces (ex: "Many Generations") arrivent en
        # "Many Generations" (Flask les gère).
        person_details, error = call_backend_person(db_name, n, p)
        
        if error:
            # Si la personne n'est pas trouvée, on retourne à la recherche
            return redirect(url_for("search_page", db_name=db_name, lang=lang, error=f"Person not found: {error}"))

        # --- MODIFICATION ICI ---
        return render_template(
            "search/search_person.html", # Chemin mis à jour
            lang=lang,
            db_name=db_name,
            person=person_details.get("person"),
            father=person_details.get("father"),
            mother=person_details.get("mother"),
            families=person_details.get("families", [])
        )
    
    # --- Affiche la page de RECHERCHE (formulaire par défaut) ---
    stats, error = get_db_stats(db_name)

    if error:
        return redirect(url_for("choose_genealogy", lang=lang, error=f"Database '{db_name}' not found."))

    return render_template(
        "search/search.html",
        lang=lang,
        db_name=db_name,
        stats=stats
    )
# --- FIN DE LA ROUTE MODIFIÉE ---

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2317, debug=True)