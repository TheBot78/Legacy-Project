from flask import Flask, render_template, request, redirect, url_for

app = Flask(
    __name__,
    static_folder="../static",
    template_folder="../templates"
)

@app.route("/")
def home():
    return redirect(url_for("choose_genealogy"))

@app.route("/choose_genealogy")
def choose_genealogy():
    lang = request.args.get("lang", "fr")
    return render_template("choose_genealogy.html", lang=lang)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2317, debug=True)
