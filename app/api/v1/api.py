from fastapi import APIRouter
from app.api.v1.endpoints import generation, transformation, analytics, multiple_patients_abstraction, concepts

api_router = APIRouter()

api_router.include_router(concepts.router, prefix="/concept", tags=["concepts"])
api_router.include_router(generation.router, prefix="/generate", tags=["generation"])
api_router.include_router(transformation.router, prefix="/transform", tags=["transformation"])
api_router.include_router(multiple_patients_abstraction.router, prefix="/mult-patients-abstraction", tags=["Multiple Patients Abstraction"])
