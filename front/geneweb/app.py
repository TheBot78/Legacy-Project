import os

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__, static_folder="../static",
            template_folder="../templates")


def check_db_exists():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           "../../db"))
    if not os.path.exists(db_path):
        return False
    files = []
    for f in os.listdir(db_path):
        file_path = os.path.join(db_path, f)
        if os.path.isfile(file_path):
            files.append(f)
    return len(files) > 0


@app.route("/")
def home():
    return redirect(url_for("choose_genealogy"))


@app.route("/choose_genealogy")
def choose_genealogy():
    lang = request.args.get("lang", "fr")
    if (
        not check_db_exists()
    ):  # If no database found, redirect to choose genealogy
        return render_template(
            "choose_genealogy.html", lang=lang
        )  # If no DB, show choose genealogy
    return render_template(
        "choose_genealogy.html", lang=lang
    )  # If DB exists, show the Family Tree of this genealogy


@app.errorhandler(404)
def page_not_found(e):
    lang = request.args.get("lang", "fr")
    return render_template("404.html", lang=lang, path=request.path), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2317, debug=True)
