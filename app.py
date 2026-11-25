import os
import secrets
import requests
import threading
import time
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request

load_dotenv()

app = Flask(__name__)

WC_URL = os.environ["WC_URL"] + "/wp-json/wc/v3/products"
WC_AUTH = (os.environ["WC_KEY"], os.environ["WC_SECRET"])
ACCESS_KEY = os.environ["ACCESS_KEY"]
REFRESH_SECONDS = 5 * 60  # 5 minuten
products = []  # cache alle producten uit WooCommerce


def fetch_all_products():
    result = []
    page = 1
    while True:
        response = requests.get(
            WC_URL,
            auth=WC_AUTH,
            params={
                "per_page": 100,
                "page": page,
                "_fields": "id,name,stock_quantity,stock_status,global_unique_id",
            },
            timeout=30,
        )
        response.raise_for_status()
        batch = response.json()
        result.extend(batch)
        if len(batch) < 100:
            return result
        page += 1


def refresh_loop():
    global products
    while True:
        try:
            products = fetch_all_products()
            print(f"Cache ververst: {len(products)} producten")
        except requests.RequestException as error:
            print("Cache verversen mislukt, oude lijst blijft staan:", error)
        time.sleep(REFRESH_SECONDS)


threading.Thread(target=refresh_loop, daemon=True).start()


@app.before_request
def check_access():
    if request.path == "/health":
        return
    given = request.args.get("key", "")
    if not secrets.compare_digest(given.encode(), ACCESS_KEY.encode()):
        abort(403)


def name_matches(name, words):
    return all(word in name.lower() for word in words)


@app.get("/api/search")
def search():
    q = request.args.get("q", "").strip().lower()
    if len(q) < 2:
        return jsonify([])

    if not products:
        return jsonify({"error": "Voorraad wordt geladen"}), 503

    if q.isdigit():
        matches = [p for p in products if p["global_unique_id"] == q]
    else:
        words = q.split()
        matches = [p for p in products if name_matches(p["name"], words)]

    return jsonify(
        [
            {
                "id": p["id"],
                "name": p["name"],
                "stock": p["stock_quantity"],
                "status": p["stock_status"],
            }
            for p in matches[:50]
        ]
    )


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/health")
def health():
    return f"ok, {len(products)} producten in cache"
