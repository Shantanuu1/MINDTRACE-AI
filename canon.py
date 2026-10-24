"""Canonical solution. Server-side only: never sent to templates before the case ends or to the AI."""
CULPRIT, MOTIVE, TIMELINE = "alex", "m_audit", "t_card"
KEY_OPPORTUNITY = {"c_log", "c_card", "c_handoff"}
KEY_MOTIVE = {"c_email", "c_doc"}
CONFIRMED = {
 frozenset(("c_watch", "c_log")): "The door opened at 11:21; the watch stopped at 11:22 - the attack followed immediately.",
 frozenset(("c_card", "c_log")): "The log's slot 7 is the empty slot on the key board: Ryan's card opened the door.",
 frozenset(("c_card", "c_handoff")): "Ryan's card left the key board and was handed over at 11:05.",
 frozenset(("c_handoff", "c_log")): "The card handed over at 11:05 was used at 11:21 by its new holder.",
 frozenset(("c_email", "c_doc")): "The audit would expose the hidden transfers - a motive for whoever initialled them.",
}
# kind "pair": both statements enough. kind "evidence": statement + discovered clue.
CONTRADICTIONS = [
 dict(id="k_alex_time", suspect="alex", a="alex_loc", b="alex_saw", clue=None,
      why="Alex says he never left the dining carriage, yet claims to have visited Adrian's compartment at 11:20."),
 dict(id="k_alex_money", suspect="alex", a="alex_money", b=None, clue="c_doc",
      why="Alex claims spotless finances, but the torn ledger page shows hidden transfers initialled A.M."),
 dict(id="k_ryan_card", suspect="ryan", a="ryan_card", b=None, clue="c_handoff",
      why="Ryan says his card never left his pocket, but the bartender saw him hand a card over at 11:05."),
 dict(id="k_maya_talk", suspect="maya", a="maya_talk", b=None, clue="c_note",
      why="Maya denies speaking to Adrian, but her warning note was pushed under his door."),
]
EXPLANATION = ("Alex Mercer had skimmed investor funds. Adrian's new agreement and audit would expose him. Alex obtained Ryan Cole's "
  "master card at the 11:05 shift change, used it to enter at 11:21, struck Adrian at 11:22 and took the AURORA CORE so the theft "
  "would hide his motive. Ryan concealed the handoff out of fear and money; Maya only tried to warn Adrian.")
ENDINGS = {
 "A": ("Perfect Reconstruction", "Alex crumbles as you lay out card, log, ledger and email in order. The core is found in his briefcase. Every thread ties together."),
 "B": ("Justice with Unanswered Questions", "Alex is arrested at the next station, but gaps in your case leave the how and why partly unproven."),
 "C": ("The Wrong Conclusion", "The accusation falls apart. At the next station the real culprit steps off the train and vanishes."),
}
