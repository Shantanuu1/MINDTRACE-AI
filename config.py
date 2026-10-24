import os
BASE = os.path.dirname(os.path.abspath(__file__))
try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "90"))
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
SAVE_PATH = os.getenv("SAVE_PATH", os.path.join(BASE, "data", "save.json"))
MAX_MESSAGE = 300
