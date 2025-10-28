from flask import Flask, render_template, request, redirect, url_for
from path import list_dir

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
    sel = request.args.get("sel", "/")
    lang = request.args.get("lang", "en")
    abs_sel, items, parent = list_dir(sel)
    return render_template(
        "Management_Creation/ged2gwb.html",
        sel=abs_sel,
        items=items,
        parent=parent,
        lang=lang  # <-- AJOUTEZ CETTE LIGNE
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2316, debug=True)