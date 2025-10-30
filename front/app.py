import os

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


def check_db_exists():
    db_path = os.path.join(os.getcwd(), "db")
    if not os.path.exists(db_path):
        return False
    files = [f for f in os.listdir(db_path) if os.path.isfile(os.path.join(db_path, f))]
    return len(files) > 0


@app.route("/")
def home():
    if (
        not check_db_exists()
    ):  # If no database found, redirect to choose genealogy ottherwise main page
        return render_template("choose_genealogy.html")
    return render_template("main.html")


@app.route("/ping_rpc")
def ping_rpc():
    try:
        response = requests.post(
            "http://rpc:2316/rpc", json={"method": "ping", "params": {}}
        )
        rpc_result = response.json().get("result", "Pas de résultat")
    except Exception as e:
        rpc_result = f"Erreur RPC : {e}"
    return jsonify({"result": rpc_result})


@app.route("/geneweb")
def geneweb():
    lang = request.args.get("lang", "fr")
    return render_template("geneweb.html", lang=lang)


@app.route("/welcome")
def welcome():
    lang = request.args.get("lang", "fr")
    return render_template("welcome.html", lang=lang)


@app.route("/choose_genealogy")
def choose_genealogy():
    return render_template("choose_genealogy.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
