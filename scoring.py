POINTS = {"clue": 10, "contradiction": 15, "connection": 5, "culprit": 30, "motive": 20, "wrong": -10}
MULT = {"easy": 0.8, "normal": 1.0, "hard": 1.5}
RANKS = [(150, "Grandmaster Detective"), (100, "Senior Inspector"), (50, "Field Investigator"), (-999, "Rookie")]

def award(st, key, kind):
    """Award points once per key. Returns points added."""
    if key in st["rewards"]:
        return 0
    base = POINTS[kind]
    pts = base if base < 0 else round(base * MULT[st["difficulty"]])
    st["rewards"].append(key); st["score"] += pts
    return pts

def rank(score):
    return next(r for t, r in RANKS if score >= t)
