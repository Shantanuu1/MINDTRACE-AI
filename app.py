import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, g
import config, storage, scoring, canon, ai_service
import game_engine as ge
from story_data import CASE, CLUES, LOCATIONS, SUSPECTS, MOTIVES, TIMELINES

GAME = {"investigation", "suspects", "interrogation", "evidence", "journal", "accusation", "resolution"}

def create_app(save_path=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=config.SECRET_KEY, SAVE_PATH=save_path or config.SAVE_PATH,
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
    app.ai = ai_service

    @app.before_request
    def _load():
        g.d = storage.load(app.config["SAVE_PATH"]); g.st = g.d["case"]
        if request.endpoint in GAME and not (g.st and g.st["started"]):
            return redirect(url_for("cases"))
        if request.endpoint == "resolution" and not g.st["completed"]:
            return redirect(url_for("accusation"))

    def commit(): storage.save(app.config["SAVE_PATH"], g.d)

    @app.context_processor
    def _ctx():
        st = getattr(g, "st", None)
        return dict(st=st, prog=ge.progress(st) if st else 0, cfg=getattr(g, "d", {}).get("settings", {}), model=config.OLLAMA_MODEL,
                    CASE=CASE, CLUES=CLUES, SUSPECTS=SUSPECTS, LOCATIONS=LOCATIONS, scoring=scoring)

    @app.route("/")
    def landing(): return render_template("landing.html")

    @app.route("/cases")
    def cases():
        hist = g.d["profile"]["history"]
        return render_template("case_files.html", best=max([h["score"] for h in hist], default=None))

    @app.post("/case/start")
    def case_start():
        g.d["case"] = ge.new_case(request.form.get("difficulty", "normal")); commit(); return redirect(url_for("investigation"))

    @app.post("/case/reset")
    def case_reset():
        diff = g.st["difficulty"] if g.st else "normal"
        g.d["case"] = ge.new_case(diff); commit(); flash("Case restarted."); return redirect(url_for("investigation"))

    @app.route("/investigation")
    def investigation():
        loc = request.args.get("loc", "compartment")
        if loc not in LOCATIONS: loc = "compartment"
        return render_template("investigation.html", loc=loc, hint=ge.hint(g.st), objectives=ge.objectives(g.st))

    @app.post("/discover")
    def discover():
        res, msg = ge.discover(g.st, request.form.get("loc", ""), request.form.get("obj", ""))
        commit(); flash(msg); return redirect(url_for("investigation", loc=request.form.get("loc") if request.form.get("loc") in LOCATIONS else None))

    @app.route("/suspects")
    def suspects(): return render_template("suspects.html", ge=ge, canon=canon)

    @app.route("/interrogation/<sid>")
    def interrogation(sid):
        if sid not in SUSPECTS: return render_template("404.html"), 404
        return render_template("interrogation.html", sid=sid, s=SUSPECTS[sid], hist=g.st["transcripts"][sid])

    @app.post("/api/interrogate/<sid>")
    def api_interrogate(sid):
        if sid not in SUSPECTS: return jsonify(error="Unknown suspect"), 404
        if g.st["completed"]: return jsonify(error="The case is closed"), 400
        q = (request.get_json(silent=True) or {}).get("message", "")
        if not isinstance(q, str) or not q.strip() or len(q) > config.MAX_MESSAGE: return jsonify(error=f"Message must be 1-{config.MAX_MESSAGE} characters"), 400
        r = ge.interview(g.st, sid, q, app.ai); commit()
        r["verified"] = len(ge.verified(g.st)); return jsonify(r)

    @app.get("/api/history/<sid>")
    def api_history(sid):
        if sid not in SUSPECTS or not g.st: return jsonify(error="Unknown suspect"), 404
        return jsonify(g.st["transcripts"][sid])

    @app.route("/evidence")
    def evidence_board(): return render_template("evidence_board.html")
    app.add_url_rule("/evidence", endpoint="evidence", view_func=evidence_board)

    @app.post("/evidence/connect")
    def ev_connect():
        c = ge.connect(g.st, request.form.get("a", ""), request.form.get("b", ""))
        commit(); flash(f"Connection: {c['kind']}. {c['why']}" if c else "Invalid or duplicate connection."); return redirect(url_for("evidence"))

    @app.post("/evidence/remove")
    def ev_remove():
        ge.disconnect(g.st, request.form.get("a", ""), request.form.get("b", "")); commit(); return redirect(url_for("evidence"))

    @app.route("/journal")
    def journal(): return render_template("journal.html", ks={c["id"]: c for c in canon.CONTRADICTIONS}, q=request.args.get("q", "").lower())

    @app.post("/journal/notes")
    def notes():
        g.st["notes"] = request.form.get("notes", "")[:5000]; commit(); flash("Notes saved."); return redirect(url_for("journal"))

    @app.post("/contradiction/<kid>/review")
    def kreview(kid):
        ge.review(g.st, kid); commit(); return redirect(url_for("journal"))

    @app.route("/accusation")
    def accusation(): return render_template("accusation.html", MOTIVES=MOTIVES, TIMELINES=TIMELINES)

    @app.post("/accusation")
    def accuse():
        err = ge.accuse(g.st, request.form.get("suspect"), request.form.get("motive"), request.form.getlist("evidence"), request.form.get("timeline"))
        if err: flash(err); return redirect(url_for("accusation"))
        ge.finish_profile(g.d["profile"], g.st); commit(); return redirect(url_for("resolution"))

    @app.route("/resolution")
    def resolution():
        t, text = canon.ENDINGS[g.st["ending"]]
        return render_template("resolution.html", ending=t, text=text, explanation=canon.EXPLANATION, ge=ge, MOTIVES=MOTIVES, canon=canon,
                               rank=scoring.rank(g.st["score"]), ACH=ge.ACH)

    @app.route("/profile")
    def profile():
        h = g.d["profile"]["history"]
        ach = sorted({a for x in h for a in x["achievements"]})
        return render_template("detective_profile.html", h=h, best=max([x["score"] for x in h], default=0),
                               avg=round(sum(x["progress"] for x in h) / len(h)) if h else 0, ach=ach, ACH=ge.ACH,
                               interviews=sum(x["interviews"] for x in h), contr=sum(x["contradictions"] for x in h))

    @app.route("/settings")
    def settings(): return render_template("settings.html")

    @app.post("/settings")
    def settings_save():
        if g.st and not g.st["completed"] and request.form.get("difficulty") in scoring.MULT:
            g.st["difficulty"] = request.form["difficulty"]
        g.d["settings"] = {"sound": "sound" in request.form, "animations": "animations" in request.form}
        commit(); flash("Settings saved."); return redirect(url_for("settings"))

    @app.post("/settings/clear")
    def clear():
        g.d = storage.default_save(); commit(); flash("All progress cleared."); return redirect(url_for("landing"))

    @app.get("/api/ai-status")
    def api_ai(): return jsonify(app.ai.status())

    @app.get("/api/status")
    def api_status():
        st = g.st
        if not st: return jsonify(started=False)
        return jsonify(started=True, progress=ge.progress(st), score=st["score"], clues=len(st["clues"]), completed=st["completed"])

    @app.get("/api/stats")
    def api_stats():
        h = g.d["profile"]["history"]; return jsonify(cases_completed=len(h), best=max([x["score"] for x in h], default=0))

    @app.errorhandler(404)
    def e404(e): return render_template("404.html"), 404

    @app.errorhandler(500)
    def e500(e): return render_template("500.html"), 500
    return app

app = create_app()
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
