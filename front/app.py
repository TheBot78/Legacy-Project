from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("main.html")

@app.route("/ping_rpc")
def ping_rpc():
    try:
        # Appel RPC interne Docker
        response = requests.post(
            "http://rpc:2316/rpc",
            json={"method": "ping", "params": {}}
        )
        rpc_result = response.json().get("result", "Pas de résultat")
    except Exception as e:
        rpc_result = f"Erreur RPC : {e}"
    return jsonify({"result": rpc_result})

@app.route("/geneweb")
def geneweb():
    lang = request.args.get('lang', 'fr')
    return render_template("geneweb.html", lang=lang)

@app.route("/welcome")
def welcome():
    lang = request.args.get('lang', 'fr')
    return render_template("welcome.html", lang=lang)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
