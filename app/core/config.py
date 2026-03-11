import os
from pydantic import BaseModel
from pathlib import Path

# Assuming root of the project is where main.py is (app/..)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseModel):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Visitors Backend"
    TAK_FILES_DIR: str = str(BASE_DIR / "TakEntities")
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "VISITORS")

settings = Settings()
