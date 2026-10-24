import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest, requests
import app as appmod, ai_service, config
import game_engine as ge

class FakeAI:
    def __init__(self, text="I was busy, detective."): self.text = text
    def reply(self, *a): return (self.text, None) if self.text else (None, "Ollama not running")
    def status(self): return {"online": False}

@pytest.fixture
def client(tmp_path):
    a = appmod.create_app(str(tmp_path / "save.json")); a.ai = FakeAI(); a.testing = True
    return a.test_client()

def start(c, d="normal"): return c.post("/case/start", data={"difficulty": d})
def find(c, loc, obj): return c.post("/discover", data={"loc": loc, "obj": obj}, follow_redirects=True)

def test_pages_load(client):
    for u in ["/", "/cases", "/settings", "/profile"]: assert client.get(u).status_code == 200
    assert client.get("/investigation").status_code == 302
    start(client)
    for u in ["/investigation", "/suspects", "/evidence", "/journal", "/accusation", "/interrogation/alex", "/investigation?loc=lounge"]:
        assert client.get(u).status_code == 200
    assert client.get("/interrogation/zzz").status_code == 404
    assert client.get("/resolution").status_code == 302

def test_duplicate_clue_scores_once(client):
    start(client); find(client, "compartment", "o_floor"); find(client, "compartment", "o_floor")
    assert client.get("/api/status").get_json()["clues"] == 1
    st = appmod.storage.load(client.application.config["SAVE_PATH"])["case"]
    assert st["score"] == 10

def test_locked_clue_and_invalid(client):
    start(client); find(client, "security", "o_terminal"); find(client, "nowhere", "x")
    assert client.get("/api/status").get_json()["clues"] == 0

def test_connections():
    st = ge.new_case()
    for loc, o in [("compartment", "o_floor"), ("security", "o_keys"), ("security", "o_terminal"), ("research", "o_desk")]: ge.discover(st, loc, o)
    assert ge.connect(st, "c_card", "c_log")["kind"] == "confirmed"
    assert ge.connect(st, "c_log", "c_card") is None
    assert ge.connect(st, "c_watch", "c_note")["kind"] == "unsupported"
    assert ge.connect(st, "c_watch", "c_nope") is None
    s = st["score"]; ge.disconnect(st, "c_card", "c_log"); ge.connect(st, "c_card", "c_log"); assert st["score"] == s

def test_contradiction_flow():
    st = ge.new_case(); ai = FakeAI()
    ge.interview(st, "ryan", "Where is your access card?", ai)
    assert st["contradictions"]["k_ryan_card"]["status"] == "theory"
    ge.discover(st, "lounge", "o_bar")
    ge.interview(st, "ryan", "Where is your access card?", ai)
    assert st["contradictions"]["k_ryan_card"]["status"] == "verified"
    sc = st["score"]; ge.interview(st, "ryan", "Where is your card again?", ai); assert st["score"] == sc
    ge.interview(st, "alex", "Where were you?", ai); ge.interview(st, "alex", "When did you last see Adrian?", ai)
    assert st["contradictions"]["k_alex_time"]["status"] == "verified"
    ge.interview(st, "alex", "Are the finances in order?", ai)
    assert st["contradictions"]["k_alex_money"]["status"] == "theory"

def test_fallback_labelled():
    st = ge.new_case(); r = ge.interview(st, "maya", "What does the core do?", FakeAI(None))
    assert r["source"] == "fallback" and r["error"]

def test_api_validation(client):
    start(client)
    assert client.post("/api/interrogate/alex", json={"message": ""}).status_code == 400
    assert client.post("/api/interrogate/alex", json={"message": "x" * 301}).status_code == 400
    assert client.post("/api/interrogate/bob", json={"message": "hi"}).status_code == 404
    r = client.post("/api/interrogate/alex", json={"message": "Where were you?"}).get_json()
    assert r["answer"] and r["source"] == config.OLLAMA_MODEL

def _all(st):
    for loc, o in [("compartment", "o_floor"), ("compartment", "o_laptop"), ("lounge", "o_bar"), ("dining", "o_bin"), ("security", "o_keys"), ("security", "o_terminal"), ("research", "o_desk")]: ge.discover(st, loc, o)

def test_endings():
    st = ge.new_case(); _all(st)
    assert ge.accuse(st, "alex", "m_audit", ["c_log", "c_card", "c_email", "c_doc"], "t_card") is None
    assert st["ending"] == "A" and "perfect" in st["achievements"]
    st = ge.new_case(); _all(st); ge.accuse(st, "alex", "m_ownership", ["c_watch"], "t_card"); assert st["ending"] == "B"
    st = ge.new_case(); _all(st); before = st["score"]; ge.accuse(st, "ryan", "m_sale", ["c_log"], "t_ryan")
    assert st["ending"] == "C" and st["score"] == before - 10
    assert ge.accuse(st, "alex", "m_audit", ["c_log"], "t_card")

def test_accuse_rejects_undiscovered(client):
    start(client)
    r = client.post("/accusation", data={"suspect": "alex", "motive": "m_audit", "evidence": ["c_log"], "timeline": "t_card"}, follow_redirects=True)
    assert b"discovered evidence only" in r.data

def test_persistence_and_reset(client):
    start(client); find(client, "compartment", "o_floor")
    assert b"Resume Case" in client.get("/cases").data
    client.post("/case/reset"); assert client.get("/api/status").get_json()["clues"] == 0

def test_ai_errors(monkeypatch):
    def boom(*a, **k): raise requests.ConnectionError()
    monkeypatch.setattr(requests, "post", boom); assert ai_service.chat([])[1] == "Ollama not running"
    class R:
        status_code = 200
        def __init__(s, j): s.j = j
        def raise_for_status(s): pass
        def json(s): return s.j
    for j in ({}, {"message": {"content": "  "}}):
        monkeypatch.setattr(requests, "post", lambda *a, j=j, **k: R(j)); assert ai_service.chat([])[0] is None
    monkeypatch.setattr(requests, "post", lambda *a, **k: R({"message": {"content": "Hi."}})); assert ai_service.chat([]) == ("Hi.", None)
    r = R({}); r.status_code = 404; monkeypatch.setattr(requests, "post", lambda *a, **k: r); assert "unavailable" in ai_service.chat([])[1]

def test_prompt_has_no_solution():
    from story_data import SUSPECTS
    m = ai_service.build_messages(SUSPECTS["alex"], SUSPECTS["alex"]["topics"][0], ["Broken Watch"], [], "hi", "normal")[0]["content"]
    assert "m_audit" not in m and "culprit" in m.lower() and "skimmed" not in m
