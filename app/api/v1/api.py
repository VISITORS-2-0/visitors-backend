from fastapi import APIRouter
from app.api.v1.endpoints import generation, transformation, analytics

api_router = APIRouter()

api_router.include_router(generation.router, prefix="/generate", tags=["generation"])
api_router.include_router(transformation.router, prefix="/transform", tags=["transformation"])
api_router.include_router(analytics.router, prefix="/summarize", tags=["analytics"])
