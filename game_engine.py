"""Deterministic game logic: discovery, interviews, Truth Tracker, connections, accusation."""
import time
import canon, scoring, config
from story_data import CLUES, LOCATIONS, SUSPECTS, MOTIVES, TIMELINES

ACH = {"first_clue": "FIRST CLUE", "first_interrogation": "FIRST INTERROGATION", "pattern": "PATTERN RECOGNIZED",
       "truth_tracker": "TRUTH TRACKER", "case_closed": "CASE CLOSED", "perfect": "PERFECT RECONSTRUCTION"}

def new_case(difficulty="normal"):
    return {"started": True, "difficulty": difficulty if difficulty in scoring.MULT else "normal", "score": 0, "clues": [], "statements": {},
            "transcripts": {s: [] for s in SUSPECTS}, "contradictions": {}, "connections": [], "notes": "", "achievements": [],
            "events": [], "ending": None, "completed": False, "rewards": [], "accusation": None}

def log(st, text):
    st["events"].append({"n": len(st["events"]) + 1, "t": time.strftime("%H:%M:%S"), "text": text})

def grant(st, key):
    if key not in st["achievements"]:
        st["achievements"].append(key); log(st, "Achievement: " + ACH[key])

def verified(st):
    return [k for k, v in st["contradictions"].items() if v["status"] == "verified"]

def progress(st):
    if not st or not st.get("started"): return 0
    interviewed = sum(1 for s in st["transcripts"].values() if s)
    return round(100 * (len(st["clues"]) + len(verified(st)) + interviewed) / (len(CLUES) + len(canon.CONTRADICTIONS) + len(SUSPECTS)))

def discover(st, loc, obj_id):
    if st["completed"]: return "error", "The case is closed."
    obj = next((o for o in LOCATIONS.get(loc, {}).get("objects", []) if o["id"] == obj_id), None)
    if not obj: return "error", "Unknown location or object."
    cid = obj["clue"]; clue = CLUES[cid]
    if cid in st["clues"]: return "already", "You already examined this."
    missing = [r for r in clue["requires"] if r not in st["clues"]]
    if missing: return "locked", "You need more information first (" + CLUES[missing[0]]["name"] + ")."
    st["clues"].append(cid); pts = scoring.award(st, "clue:" + cid, "clue")
    log(st, f"Found clue: {clue['name']}"); grant(st, "first_clue"); _check(st)
    return "found", f"Found: {clue['name']} (+{pts})"

def match_topic(sid, q):
    q = q.lower()
    return next((t for t in SUSPECTS[sid]["topics"] if any(k in q for k in t["keywords"])), None)

def interview(st, sid, question, ai):
    if sid not in SUSPECTS: return None
    q = (question or "").strip()[:config.MAX_MESSAGE]
    if not q: return None
    sus = SUSPECTS[sid]; topic = match_topic(sid, q)
    names = [CLUES[c]["name"] for c in st["clues"] if sid in CLUES[c]["suspects"]]
    text, err = ai.reply(sus, topic, names, st["transcripts"][sid], q, st["difficulty"])
    if text: source = config.OLLAMA_MODEL
    else: text = topic["answer"] if topic else sus["generic"]; source = "fallback"
    st["transcripts"][sid].append({"q": q, "a": text, "source": source, "topic": topic["id"] if topic else None, "error": err})
    log(st, f"Interviewed {sus['name']}"); grant(st, "first_interrogation")
    if topic and topic["id"] not in st["statements"]:
        st["statements"][topic["id"]] = {"id": topic["id"], "suspect": sid, "text": topic["claim"], "context": q, "n": len(st["events"])}
        log(st, f"Statement recorded: {sus['name']}: \"{topic['claim']}\"")
    _check(st)
    return {"answer": text, "source": source, "error": err, "topic": topic["id"] if topic else None}

def _check(st):
    for c in canon.CONTRADICTIONS:
        if c["id"] in st["contradictions"] and st["contradictions"][c["id"]]["status"] == "verified": continue
        if c["a"] not in st["statements"] or (c["b"] and c["b"] not in st["statements"]): continue
        ok = (c["clue"] is None) or (c["clue"] in st["clues"])
        rec = st["contradictions"].setdefault(c["id"], {"status": "theory", "reviewed": False})
        if ok:
            rec["status"] = "verified"; scoring.award(st, "contra:" + c["id"], "contradiction"); log(st, "Contradiction verified: " + c["why"])
    n = len(verified(st))
    if n >= 3: grant(st, "truth_tracker")

def review(st, kid):
    if kid not in st["contradictions"]: return False
    st["contradictions"][kid]["reviewed"] = True; return True

def connect(st, a, b):
    if a == b or a not in st["clues"] or b not in st["clues"]: return None
    key = sorted((a, b))
    if any(sorted((c["a"], c["b"])) == key for c in st["connections"]): return None
    if frozenset((a, b)) in canon.CONFIRMED:
        kind, why = "confirmed", canon.CONFIRMED[frozenset((a, b))]
        scoring.award(st, "conn:" + "|".join(key), "connection"); grant(st, "pattern")
    elif set(CLUES[a]["suspects"]) & set(CLUES[b]["suspects"]) or CLUES[a]["loc"] == CLUES[b]["loc"]:
        kind, why = "plausible", "A reasonable theory, but not supported by the case facts."
    else:
        kind, why = "unsupported", "No supported link between these clues."
    c = {"a": a, "b": b, "kind": kind, "why": why}; st["connections"].append(c)
    log(st, f"Connected {CLUES[a]['name']} and {CLUES[b]['name']} ({kind})"); return c

def disconnect(st, a, b):
    n = len(st["connections"])
    st["connections"] = [c for c in st["connections"] if sorted((c["a"], c["b"])) != sorted((a, b))]
    return len(st["connections"]) < n

def objectives(st):
    return [("Discover 3 clues", len(st["clues"]) >= 3), ("Interview every suspect", all(st["transcripts"].values())),
            ("Verify a contradiction", bool(verified(st))), ("Confirm a clue connection", any(c["kind"] == "confirmed" for c in st["connections"])),
            ("Make your accusation", st["completed"])]

def hint(st):
    if st["difficulty"] == "hard": return None
    left = [c for c in CLUES if c not in st["clues"]]
    if not left: return "Interview suspects again and connect your clues, then accuse."
    if st["difficulty"] == "easy": return "Try the " + LOCATIONS[CLUES[left[0]]["loc"]]["name"] + "."
    return f"{len(left)} clue(s) remain undiscovered."

def accuse(st, sid, motive, evidence, timeline):
    if st["completed"]: return "The case is already closed."
    if sid not in SUSPECTS or motive not in MOTIVES or timeline not in TIMELINES: return "Choose a suspect, motive and timeline."
    if not isinstance(evidence, list) or not evidence or any(e not in st["clues"] for e in evidence): return "Select discovered evidence only."
    ev = set(evidence)
    cul = sid == canon.CULPRIT; mot = motive == canon.MOTIVE; tl = timeline == canon.TIMELINE
    strong = len(ev & (canon.KEY_OPPORTUNITY | canon.KEY_MOTIVE)) >= 3 and ev & canon.KEY_MOTIVE and ev & canon.KEY_OPPORTUNITY
    ending = "A" if cul and mot and tl and strong else "B" if cul else "C"
    if cul: scoring.award(st, "culprit", "culprit")
    else: scoring.award(st, "wrong", "wrong")
    if cul and mot: scoring.award(st, "motive", "motive")
    st["ending"] = ending; st["completed"] = True
    st["accusation"] = dict(suspect=sid, motive=motive, evidence=evidence, timeline=timeline, culprit_ok=cul, motive_ok=mot, timeline_ok=tl, strong=bool(strong))
    grant(st, "case_closed")
    if ending == "A": grant(st, "perfect")
    log(st, "Accusation submitted: " + SUSPECTS[sid]["name"])
    return None

def finish_profile(profile, st):
    profile["history"].append({"ending": st["ending"], "score": st["score"], "rank": scoring.rank(st["score"]), "progress": progress(st),
        "interviews": sum(len(v) for v in st["transcripts"].values()), "contradictions": len(verified(st)), "achievements": list(st["achievements"]), "difficulty": st["difficulty"]})
