from fastapi import FastAPI
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="AI Telegram Post Generator")

@app.get("/")
def root():
    return {
        "status": "ok",
        "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "env_loaded_from": str(env_path),
        "file_exists": env_path.exists()
    }