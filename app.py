import os
import secrets
import requests
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request

load_dotenv()

app = Flask(__name__)

WC_URL = os.environ["WC_URL"] + "/wp-json/wc/v3/products"
WC_AUTH = (os.environ["WC_KEY"], os.environ["WC_SECRET"])
ACCESS_KEY = os.environ["ACCESS_KEY"]

@app.before_request
def check_access():
    if request.path == "/health":
        return
    given = request.args.get("key", "")
    if not secrets.compare_digest(given.encode(), ACCESS_KEY.encode()):
        abort(403)



@app.get("/api/search")
def search():
    q =  request.args.get("q", "").strip().lower()
    if len(q) < 2:
        return jsonify([])

    # shortcut: alleen de eerste 50 treffers van WC worden gefiltered; bij te weinig resultaten per page naar 100 of pagineren

    response = requests.get(
    WC_URL,
    auth=WC_AUTH,
    params={"search": q, "per_page": 50, "_fields": "name,stock_quantity,stock_status"},
    timeout=10,
    )
    response.raise_for_status()

    words = q.split()
    results = []
    for product in response.json():
        name = product["name"]
        if all(word in name.lower() for word in words):
            results.append({
                "name": name,
                "stock": product["stock_quantity"],
                "status": product["stock_status"],
            })
    return jsonify(results)

@app.get("/")
def index():
    return app.send_static_file("index.html")

@app.get("/health")
def health():
    return "ok"