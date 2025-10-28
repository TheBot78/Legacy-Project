import os  # <-- AJOUTEZ CET IMPORT
import requests
from flask import Flask, render_template, request, redirect, url_for
from path import list_dir, BASE_DIR

app = Flask(
    __name__,
    static_folder="../static",
    template_folder="../templates"
)

@app.route("/")
def home():
    return redirect(url_for("welcome"))

@app.route("/welcome")
def welcome():
    lang = request.args.get("lang", "fr")
    return render_template("welcome.html", lang=lang)

@app.route("/ged2gwb")
def ged2gwb():
    lang = request.args.get("lang", "en")

    # VÉRIFIE SI L'UTILISATEUR A CLIQUE SUR "OK"
    if request.args.get("opt") == "check":
        # --- C'est la nouvelle logique de confirmation ---

        # Récupère le chemin du fichier sélectionné
        filepath = request.args.get("filepath", "")

        # Récupère le nom de la base (-o)
        db_name = request.args.get("o", "")

        # Si le nom de la base est vide, déduisez-le du nom du fichier
        if not db_name and filepath:
            # os.path.basename('/host_files/foo.ged') -> 'foo.ged'
            basename = os.path.basename(filepath)
            # os.path.splitext('foo.ged') -> ('foo', '.ged')
            db_name = os.path.splitext(basename)[0]

        all_options = request.args.to_dict()
        all_options['o'] = db_name

        return render_template(
            "management_creation/ged2gwb_confirm.html",
            lang=lang,
            filepath=filepath,     # Pour afficher la commande (ex: /host_files/foo.ged)
            db_name=db_name,       # Pour afficher le nom (ex: foo)
            all_options=all_options # Dictionnaire de toutes les options pour le formulaire caché
        )

    else:
        sel = request.args.get("sel", BASE_DIR)
        abs_sel, items, parent = list_dir(sel)
        return render_template(
            "management_creation/ged2gwb.html",
            sel=abs_sel,
            items=items,
            parent=parent,
            lang=lang
        )

@app.route("/ged2gwb", methods=["POST"])
def ged2gwb_post():
    lang = request.form.get("lang", "en")
    filepath = request.form.get("anon", "").strip()
    db_name = request.form.get("o", "").strip()

    if not filepath:
        return render_template(
            "management_creation/ged2gwb_confirm.html",
            lang=lang,
            filepath=filepath,
            db_name=db_name or "",
            all_options=request.form.to_dict(),
            error="Aucun fichier GEDCOM sélectionné",
        )

    # Lecture du contenu GEDCOM
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            ged_text = f.read()
    except Exception as e:
        return render_template(
            "management_creation/ged2gwb_confirm.html",
            lang=lang,
            filepath=filepath,
            db_name=db_name or "",
            all_options=request.form.to_dict(),
            error=str(e),
        )

    # Appel au backend avec fallback (localhost et host.docker.internal)
    candidates = []
    if os.environ.get("BACKEND_URL"):
        candidates.append(os.environ.get("BACKEND_URL"))
    candidates.append("http://127.0.0.1:8000/import_ged")
    candidates.append("http://localhost:8000/import_ged")
    candidates.append("http://host.docker.internal:8000/import_ged")

    last_error = None
    for backend_url in candidates:
        try:
            resp = requests.post(backend_url, json={
                "db_name": db_name,
                "ged_text": ged_text,
                "notes_origin_file": filepath,
            }, timeout=20)
            data = resp.json()
            if data.get("ok"):
                return redirect(url_for("ged2gwb_result", db=db_name, lang=lang))
            last_error = f"Backend error: {data}"
        except Exception as e:
            last_error = str(e)

    return render_template(
        "management_creation/ged2gwb_confirm.html",
        lang=lang,
        filepath=filepath,
        db_name=db_name or "",
        all_options=request.form.to_dict(),
        error=f"Appel backend échoué: {last_error}",
    )

@app.route("/ged2gwb_result")
def ged2gwb_result():
    lang = request.args.get("lang", "en")
    db_name = request.args.get("db")

    stats = {}
    error = None
    base_candidates = [
        os.environ.get("BACKEND_BASE", "http://127.0.0.1:8000"),
        "http://localhost:8000",
        "http://host.docker.internal:8000",
    ]
    for root in base_candidates:
        try:
            r = requests.get(f"{root}/db/{db_name}/stats", timeout=10)
            if r.status_code == 200:
                stats = r.json()
                error = None
                break
            error = f"HTTP {r.status_code}"
        except Exception as e:
            error = str(e)

    return render_template(
        "management_creation/ged2gwb_result.html",
        lang=lang,
        db_name=db_name,
        stats=stats,
        error=error,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2316, debug=True)