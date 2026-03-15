from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base

Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8081", "http://localhost:5173"], # Add frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

from app.services.concept_manager_v2 import concept_manager_v2_instance

@app.on_event("startup")
async def startup_event():
    print("Initializing TAK entities...")
    concept_manager_v2_instance.init_entities()
    print(f"Loaded {len(concept_manager_v2_instance.get_all_entities())} TAK entities.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
