from app import name_matches


def test_deel_van_woord():
    assert name_matches("Easyfill PLA Zwart", ["easy"])


def test_alle_woorden_moeten_kloppen():
    assert not name_matches("Easyfill PLA Blauw", ["pla", "rood"])


def test_hoofdletters_maken_niet_uit():
    assert name_matches("PLA ROOD 1kg", ["pla", "rood"])

def test_geen_woorden_past_op_alles():
    assert name_matches("PLA Rood", [])