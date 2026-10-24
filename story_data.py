"""Public story data. The canonical solution lives in canon.py (server-side only)."""
CASE = {"id": "001", "title": "Echoes of the Last Train", "level": "Normal",
        "synopsis": "2042. The Asterion Express is stranded in a mountain storm. At 11:45 PM inventor Adrian Vale is found unconscious in his locked compartment and his AURORA CORE prototype is gone. Comms are down. Three suspects. One night."}

CLUES = {
 "c_watch": dict(name="Broken Watch", cat="Timeline evidence", loc="compartment", suspects=["alex"], requires=[], key=False,
   desc="Adrian's wristwatch, smashed and stopped at 11:22 PM.", sig="The attack happened at 11:22 PM."),
 "c_email": dict(name="Audit Email", cat="Motive evidence", loc="compartment", suspects=["alex"], requires=[], key=True,
   desc="An unsent email on Adrian's laptop: he is amending the agreement and ordering a full audit of Vale Dynamics' accounts on arrival.", sig="Someone with hidden finances had a reason to stop the audit."),
 "c_handoff": dict(name="Bartender's Statement", cat="Witness statements", loc="lounge", suspects=["ryan", "alex"], requires=[], key=True,
   desc="The bartender saw Ryan Cole pass a card to a man in a grey suit at 11:05 PM. Alex Mercer wore a grey suit at dinner.", sig="Ryan's card changed hands before the attack."),
 "c_doc": dict(name="Torn Ledger Page", cat="Motive evidence", loc="dining", suspects=["alex"], requires=[], key=True,
   desc="A torn page in the dining carriage bin lists transfers from investor funds into a private account, initialled A.M.", sig="Alex had hidden money an audit would expose."),
 "c_card": dict(name="Empty Key Slot", cat="Physical evidence", loc="security", suspects=["ryan"], requires=[], key=True,
   desc="Ryan's master access card is missing from the key board. Its slot number is 7.", sig="Ryan's card was not where he claims."),
 "c_log": dict(name="Door Access Log", cat="Digital evidence", loc="security", suspects=["ryan", "alex"], requires=["c_card"], key=True,
   desc="Card slot 7 opened Adrian's compartment door at 11:21 PM. Needs the slot number from the key board.", sig="Ryan's card was used one minute before the attack."),
 "c_note": dict(name="Maya's Warning Note", cat="Physical evidence", loc="research", suspects=["maya"], requires=[], key=False,
   desc="A torn draft in the research carriage: 'Adrian - AURORA can bypass any lock. Be careful who you trust.' Pushed under his door at 10:30 PM.", sig="Maya did speak up to Adrian - she is a witness, not the thief."),
}

LOCATIONS = {
 "compartment": dict(name="Adrian's Private Compartment", intro="Lights flicker. The bed is rumpled, the safe stands open and empty.",
   objects=[dict(id="o_floor", label="Examine the floor", clue="c_watch"), dict(id="o_laptop", label="Open the laptop", clue="c_email")]),
 "lounge": dict(name="Observation Lounge", intro="Storm-lashed windows, a quiet bar and one nervous bartender.",
   objects=[dict(id="o_bar", label="Question the bartender", clue="c_handoff")]),
 "dining": dict(name="Dining Carriage", intro="Half-finished glasses and linen napkins from a dinner nobody finished.",
   objects=[dict(id="o_bin", label="Search the waste bin", clue="c_doc")]),
 "security": dict(name="Security Office", intro="Monitors hiss with static. A key board hangs on the wall.",
   objects=[dict(id="o_keys", label="Inspect the key board", clue="c_card"), dict(id="o_terminal", label="Read the door terminal", clue="c_log")]),
 "research": dict(name="Research Carriage", intro="Prototype rigs and humming instruments. Maya's workspace.",
   objects=[dict(id="o_desk", label="Search Maya's desk", clue="c_note")]),
}

def T(id, kw, claim, ans, sug):
    return dict(id=id, keywords=kw, claim=claim, answer=ans, suggested=sug)

SUSPECTS = {
 "alex": dict(name="Alex Mercer", role="Business partner", color="#b08d57", initials="AM",
   bio="Charming, controlled, ambitious co-founder of Vale Dynamics.", public_motive="Dispute over ownership of the AURORA CORE.",
   alibi="Says he was in the dining carriage.", personality="charming, controlled, ambitious; avoids money questions; suddenly precise about times",
   generic="Detective, I'd love to help, but I'm not sure what you're asking.",
   topics=[T("alex_loc", ["where", "alibi", "evening", "whereabouts", "dining", "left"], "I never left the dining carriage after 10:45 PM.",
             "The dining carriage, all evening. I never left after 10:45 PM. Ask the steward.", "Where were you this evening?"),
           T("alex_saw", ["saw", "see", "goodnight", "last", "11:20", "argu", "adrian"], "I stopped by Adrian's compartment at 11:20 to say goodnight and he was fine.",
             "I looked in on Adrian at 11:20 to say goodnight. He was perfectly fine then.", "When did you last see Adrian?"),
           T("alex_money", ["money", "financ", "debt", "fund", "invest", "ledger", "audit"], "Vale Dynamics' finances are spotless; I have nothing to hide.",
             "Our finances are spotless. Why does everyone fixate on money?", "Are Vale Dynamics' finances in order?"),
           T("alex_own", ["own", "core", "dispute", "partner", "share"], "We argued about ownership of the AURORA CORE, as partners do.",
             "We disagreed about who owned the AURORA CORE. Partners argue. It isn't a crime.", "Tell me about the ownership dispute.")]),
 "maya": dict(name="Dr. Maya Chen", role="Research scientist", color="#4f7ea8", initials="MC",
   bio="Analytical and reserved; lead researcher on the AURORA CORE.", public_motive="Ethical dispute over how the invention could be used.",
   alibi="Says she was in the research carriage.", personality="intelligent, analytical, reserved; technical detail but guards a private conversation",
   generic="I'm not sure that relates to my work, Detective.",
   topics=[T("maya_talk", ["speak", "talk", "warn", "conversation", "met", "spoke", "adrian"], "I did not speak to Adrian tonight.",
             "I did not speak to Adrian tonight. We had said everything already.", "Did you speak to Adrian tonight?"),
           T("maya_tech", ["core", "aurora", "capab", "tech", "invention", "ethic", "work"], "The AURORA CORE is a power-routing prototype and my concerns were purely ethical.",
             "A power-routing prototype. My concerns are ethical, nothing more.", "What does the AURORA CORE do?"),
           T("maya_loc", ["where", "alibi", "evening", "carriage", "lab"], "I was in the research carriage all night checking test logs.",
             "In the research carriage, going over test logs. All night.", "Where were you tonight?")]),
 "ryan": dict(name="Ryan Cole", role="Train security", color="#a14a4a", initials="RC",
   bio="Observant, nervous and practical; runs the train's security desk.", public_motive="Possible involvement in the missing prototype.",
   alibi="Says he stayed in the security office.", personality="observant, nervous, practical; knows more about the system than he admits",
   generic="Look, I just run security. I don't follow, sir.",
   topics=[T("ryan_card", ["card", "key", "access", "master", "pocket"], "My access card never left my pocket tonight.",
             "My card never left my pocket. Not once.", "Where is your access card?"),
           T("ryan_shift", ["shift", "change", "office", "restricted", "where", "alibi"], "At the shift change I stayed at my desk in the security office.",
             "I stayed at my desk in the security office through the shift change.", "What did you do at the shift change?"),
           T("ryan_sys", ["system", "log", "camera", "comm", "radio", "failure", "security"], "The comms failure is a storm fault and nothing to do with me.",
             "The storm knocked out comms. That's a fault, not me.", "What caused the comms failure?")]),
}

MOTIVES = {"m_ownership": "Win the ownership dispute over the AURORA CORE", "m_ethics": "Stop the invention being misused",
           "m_audit": "Stop an audit that would expose a hidden financial arrangement", "m_sale": "Steal the prototype to sell it"}
TIMELINES = {"t_maya": "Maya delivered a warning at 10:30 and attacked Adrian at 11:22",
             "t_card": "Ryan handed his card over at 11:05; it opened the compartment at 11:21; Adrian was attacked at 11:22",
             "t_ryan": "Ryan used his own card at 11:21 to steal the core alone"}
