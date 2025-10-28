import os  # <-- AJOUTEZ CET IMPORT
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
            "Management_Creation/ged2gwb_confirm.html",
            lang=lang,
            filepath=filepath,     # Pour afficher la commande (ex: /host_files/foo.ged)
            db_name=db_name,       # Pour afficher le nom (ex: foo)
            all_options=all_options # Dictionnaire de toutes les options pour le formulaire caché
        )

    else:
        sel = request.args.get("sel", BASE_DIR)
        abs_sel, items, parent = list_dir(sel)
        return render_template(
            "Management_Creation/ged2gwb.html",
            sel=abs_sel,
            items=items,
            parent=parent,
            lang=lang
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2316, debug=True)