from flask import Flask, render_template, request

app = Flask(
    __name__,
    static_folder="../static",
    template_folder="../templates"
)

@app.route("/")
def start():
    lang = request.accept_languages.best_match(
        ["de", "en", "es", "fr", "it", "lv", "nl", "no", "fi", "sv"]
    ) or "en"
    return render_template("geneweb.html", lang=lang)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2315)
