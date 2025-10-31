import os
import requests
from flask import Flask, render_template, request, redirect, url_for
from path import list_dir, BASE_DIR

app = Flask(
    __name__,
    static_folder="../static",
    template_folder="../templates"
)

def get_backend_candidates():
    candidates = []
    if os.environ.get("BACKEND_URL"):
        candidates.append(os.environ.get("BACKEND_URL"))
    candidates.append("http://127.0.0.1:8000")
    candidates.append("http://localhost:8000")
    candidates.append("http://host.docker.internal:8000")
    return candidates

@app.route("/")
def home():
    return redirect(url_for("welcome"))

@app.route("/welcome")
def welcome():
    lang = request.args.get("lang", "fr")
    return render_template("welcome.html", lang=lang)

@app.route("/ged2gwb", methods=['GET', 'POST'])
def ged2gwb():
    lang = request.args.get("lang", request.form.get("lang", "en"))

    if request.method == 'POST':
        if request.form.get("cancel"):
            return redirect(url_for('welcome'))

        filepath = request.form.get("anon", "").strip()
        db_name = request.form.get("o", "").strip()

        if not filepath:
            return render_template(
                "management_creation/ged2gwb_confirm.html",
                lang=lang, filepath=filepath, db_name=db_name,
                all_options=request.form.to_dict(),
                error="Aucun fichier GEDCOM sélectionné"
            )

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                ged_text = f.read()
        except Exception as e:
            return render_template(
                "management_creation/ged2gwb_confirm.html",
                lang=lang, filepath=filepath, db_name=db_name,
                all_options=request.form.to_dict(), error=str(e)
            )

        candidates = get_backend_candidates()
        last_error = None
        for base_url in candidates:
            try:
                backend_url = f"{base_url.rstrip('/')}/import_ged"
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
            lang=lang, filepath=filepath, db_name=db_name,
            all_options=request.form.to_dict(),
            error=f"Appel backend échoué: {last_error}"
        )
    else:
        if request.args.get("opt") == "check":
            filepath = request.args.get("filepath", "")
            db_name = request.args.get("o", "")

            if not db_name and filepath:
                basename = os.path.basename(filepath)
                db_name = os.path.splitext(basename)[0]

            all_options = request.args.to_dict()
            all_options['o'] = db_name

            return render_template(
                "management_creation/ged2gwb_confirm.html",
                lang=lang,
                filepath=filepath,
                db_name=db_name,
                all_options=all_options
            )
        else:
            sel = request.args.get("sel", BASE_DIR)
            abs_sel, items, parent = list_dir(sel)
            return render_template(
                "management_creation/ged2gwb.html",
                sel=abs_sel, items=items, parent=parent, lang=lang
            )

@app.route("/ged2gwb_result")
def ged2gwb_result():
    lang = request.args.get("lang", "en")
    db_name = request.args.get("db")
    stats, error = get_db_stats(db_name)

    return render_template(
        "management_creation/ged2gwb_result.html",
        lang=lang, db_name=db_name, stats=stats, error=error
    )


@app.route("/gwc", methods=['GET', 'POST'])
def gwc():
    lang = request.args.get("lang", request.form.get("lang", "en"))

    if request.method == 'POST':
        if request.form.get("cancel"):
            return redirect(url_for('welcome'))

        filepath = request.form.get("anon", "").strip()
        db_name = request.form.get("o", "").strip()
        gw_text = ""

        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    gw_text = f.read()
            except Exception as e:
                all_options = request.form.to_dict()
                all_options['o'] = db_name
                return render_template(
                    "management_creation/gwc_confirm.html",
                    lang=lang, filepath=filepath, db_name=db_name,
                    all_options=all_options, error=str(e)
                )
        
        candidates = get_backend_candidates()
        last_error = None
        for base_url in candidates:
            try:
                backend_url = f"{base_url.rstrip('/')}/import_gw"
                resp = requests.post(backend_url, json={
                    "db_name": db_name,
                    "gw_text": gw_text,
                    "notes_origin_file": filepath,
                }, timeout=20)
                data = resp.json()
                if data.get("ok"):
                    return redirect(url_for("gwc_result", db=db_name, lang=lang))
                last_error = f"Backend error: {data}"
            except Exception as e:
                last_error = str(e)

        if filepath:
            all_options = request.form.to_dict()
            all_options['o'] = db_name
            return render_template(
                "management_creation/gwc_confirm.html",
                lang=lang, filepath=filepath, db_name=db_name,
                all_options=all_options, error=f"Appel backend échoué: {last_error}"
            )
        else:
            return render_template(
                "management_creation/gwcempty_confirm.html",
                lang=lang, db_name=db_name, error=f"Appel backend échoué: {last_error}"
            )

    else:
        if request.args.get("opt") == "check":
            filepath = request.args.get("fname", "")
            db_name = request.args.get("o", "")

            if not db_name and filepath:
                basename = os.path.basename(filepath)
                db_name = os.path.splitext(basename)[0]

            all_options = request.args.to_dict()
            all_options['o'] = db_name

            return render_template(
                "management_creation/gwc_confirm.html",
                lang=lang,
                filepath=filepath,
                db_name=db_name,
                all_options=all_options
            )
        else:
            sel = request.args.get("sel", BASE_DIR)
            abs_sel, items, parent = list_dir(sel)
            return render_template(
                "management_creation/gwc.html",
                sel=abs_sel, items=items, parent=parent, lang=lang
            )

@app.route("/gwc_result")
def gwc_result():
    lang = request.args.get("lang", "en")
    db_name = request.args.get("db")
    stats, error = get_db_stats(db_name)

    return render_template(
        "management_creation/ged2gwb_result.html",
        lang=lang, db_name=db_name, stats=stats, error=error
    )

@app.route("/gwcempty", methods=['GET'])
def gwcempty():
    lang = request.args.get("lang", "en")
    db_name = request.args.get("o")

    if db_name:
        return render_template(
            "management_creation/gwcempty_confirm.html",
            lang=lang,
            db_name=db_name
        )
    else:
        return render_template(
            "management_creation/gwcempty.html",
            lang=lang
        )

@app.route("/rename", methods=['GET', 'POST'])
def rename():
    lang = request.args.get("lang", request.form.get("lang", "en"))
    geneweb_url = "http://localhost:2317"

    if request.method == 'POST':
        errors = []
        for old_name, new_name in request.form.items():
            if old_name == 'lang':
                continue
            if old_name != new_name:
                success, error = call_backend_rename(old_name, new_name)
                if not success:
                    errors.append(error)

        databases, list_error = get_all_dbs()
        if list_error:
            errors.append(list_error)
        
        return render_template(
            "management_creation/rename_confirm.html",
            lang=lang,
            databases=databases,
            geneweb_url=geneweb_url,
            errors=errors
        )
    
    else:
        databases, error = get_all_dbs()
        return render_template(
            "management_creation/rename.html",
            lang=lang,
            databases=databases,
            geneweb_url=geneweb_url,
            error=error
        )

@app.route("/delete", methods=['GET'])
def delete():
    lang = request.args.get("lang", "en")
    
    dbs_to_delete = [db for db in request.args if db != 'lang']

    if dbs_to_delete:
        geneweb_url = "http://localhost:2317"
        return render_template(
            "management_creation/delete_confirm.html",
            lang=lang,
            databases_to_delete=dbs_to_delete,
            geneweb_url=geneweb_url
        )

    else:
        databases, error = get_all_dbs()
        geneweb_url = "http://localhost:2317" 

        return render_template(
            "management_creation/delete.html",
            lang=lang,
            databases=databases,
            geneweb_url=geneweb_url,
            error=error
        )

@app.route("/delete_confirm", methods=['POST'])
def delete_confirm_action():
    lang = request.form.get("lang", "en")
    
    deleted_dbs_list = []
    errors = []

    for db_name, value in request.form.items():
        if value == 'del':
            success, error = call_backend_delete(db_name)
            if success:
                deleted_dbs_list.append(db_name)
            else:
                errors.append(f"Failed to delete {db_name}: {error}")

    return redirect(url_for(
        'delete_result', 
        lang=lang, 
        deleted=deleted_dbs_list, 
        errors=errors
    ))

@app.route("/delete_result")
def delete_result():
    lang = request.args.get("lang", "en")
    
    deleted_databases = request.args.getlist("deleted")
    errors = request.args.getlist("errors")
    
    remaining_databases, list_error = get_all_dbs()
    
    return render_template(
        "management_creation/delete_result.html",
        lang=lang,
        deleted_databases=deleted_databases,
        remaining_databases=remaining_databases,
        errors=errors,
        list_error=list_error
    )

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

def call_backend_delete(db_name):
    base_candidates = [
        os.environ.get("BACKEND_BASE", "http://127.0.0.1:8000"),
        "http://localhost:8000",
        "http://host.docker.internal:8000",
    ]
    last_error = None
    for root in base_candidates:
        try:
            r = requests.delete(f"{root.rstrip('/')}/db/{db_name}", timeout=10)
            if r.status_code in (200, 204):
                try:
                    data = r.json() if r.content else {"ok": True}
                except Exception:
                    data = {"ok": True}
                if data.get("ok", True):
                    return True, None
                return False, f"Backend error: {data}"
            last_error = f"HTTP {r.status_code}"
        except Exception as e:
            last_error = str(e)
    return False, last_error


def call_backend_rename(old_name, new_name):
    base_candidates = [
        os.environ.get("BACKEND_BASE", "http://127.0.0.1:8000"),
        "http://localhost:8000",
        "http://host.docker.internal:8000",
    ]
    last_error = None
    for root in base_candidates:
        try:
            url = f"{root.rstrip('/')}/db/{old_name}/rename"
            r = requests.post(url, json={"new_name": new_name}, timeout=10)
            if r.status_code == 200:
                try:
                    data = r.json()
                except Exception:
                    return True, None
                if data.get("ok", False):
                    return True, None
                return False, f"Backend error: {data}"
            last_error = f"HTTP {r.status_code}"
        except Exception as e:
            last_error = str(e)
    return False, last_error

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2316, debug=True)
