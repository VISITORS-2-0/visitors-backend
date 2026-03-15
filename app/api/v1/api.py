from fastapi import APIRouter
from app.api.v1.endpoints import generation, transformation, analytics, visitors_queries, concepts, concepts_v2

api_router = APIRouter()

api_router.include_router(concepts.router, prefix="/concept", tags=["concepts"])
api_router.include_router(concepts_v2.router, prefix="/concept-v2", tags=["concepts v2"])
# api_router.include_router(generation.router, prefix="/generate", tags=["generation"]) # Moved to visitors_queries
api_router.include_router(transformation.router, prefix="/states-normalization", tags=["transformation"])
api_router.include_router(visitors_queries.router, prefix="/visitors-queries", tags=["Visitors Queries"])
