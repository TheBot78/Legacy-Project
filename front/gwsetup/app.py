from flask import Flask, render_template, request, redirect, url_for

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2316, debug=True)
