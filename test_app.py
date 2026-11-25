import json
from app import name_matches


def test_demo_producten_hebben_alle_velden():
    with open("demo_products.json", encoding="utf-8") as f:
        products = json.load(f)
        assert len(products) > 0
        for p in products:
            assert {"id", "name", "stock_quantity", "stock_status", "global_unique_id"} <= p.keys()


def test_deel_van_woord():
    assert name_matches("Easyfill PLA Zwart", ["easy"])


def test_alle_woorden_moeten_kloppen():
    assert not name_matches("Easyfill PLA Blauw", ["pla", "rood"])


def test_hoofdletters_maken_niet_uit():
    assert name_matches("PLA ROOD 1kg", ["pla", "rood"])

def test_geen_woorden_past_op_alles():
    assert name_matches("PLA Rood", [])