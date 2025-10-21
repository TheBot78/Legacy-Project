from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    lang = request.args.get("lang", "en").lower()
    valid_langs = ["de", "en", "es", "fr", "it", "lv", "nl", "no", "fi", "sv"]
    if lang not in valid_langs:
        lang = "en"
    return render_template("welcome.html", lang=lang)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2317, debug=True)
