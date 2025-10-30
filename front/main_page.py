from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Bienvenue sur la page principale"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
