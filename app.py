import csv
from pathlib import Path

import joblib
from flask import Flask, render_template, request

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
model = joblib.load(BASE_DIR / "model.pkl")
features = joblib.load(BASE_DIR / "features.pkl")


def extract_features(url):
    """Build the 19 URL-based features in the exact training order."""
    u = url.strip()
    for scheme in ("https://", "http://"):
        if u.lower().startswith(scheme):
            u = u[len(scheme):]
            break
    counts = {
        "url_length": len(u),
        "n_dots": u.count("."),
        "n_hypens": u.count("-"),
        "n_underline": u.count("_"),
        "n_slash": u.count("/"),
        "n_questionmark": u.count("?"),
        "n_equal": u.count("="),
        "n_at": u.count("@"),
        "n_and": u.count("&"),
        "n_exclamation": u.count("!"),
        "n_space": u.count(" "),
        "n_tilde": u.count("~"),
        "n_comma": u.count(","),
        "n_plus": u.count("+"),
        "n_asterisk": u.count("*"),
        "n_hastag": u.count("#"),
        "n_dollar": u.count("$"),
        "n_percent": u.count("%"),
        "n_redirection": u.count("//"),
    }
    return [counts[f] for f in features]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    url = request.form.get("url", "").strip()
    if not url:
        return render_template("index.html", error="Please enter a URL.")
    x = [extract_features(url)]
    label = int(model.predict(x)[0])
    prob = float(model.predict_proba(x)[0][label]) * 100
    return render_template("result.html", url=url, phishing=(label == 1), prob=round(prob, 1))


@app.route("/dashboard")
def dashboard():
    with (BASE_DIR / "results.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return render_template("dashboard.html", header=rows[0], rows=rows[1:])


if __name__ == "__main__":
    app.run(debug=False)
