from pydantic import BaseModel

class Settings(BaseModel):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Visitors Backend"

settings = Settings()
