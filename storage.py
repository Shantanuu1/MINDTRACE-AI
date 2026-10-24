import json, os, tempfile

def default_save():
    return {"case": None, "profile": {"history": []}, "settings": {"sound": True, "animations": True}}

def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        base = default_save(); base.update(d); return base
    except (OSError, ValueError):
        return default_save()

def save(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)
