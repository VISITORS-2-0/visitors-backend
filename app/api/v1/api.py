from fastapi import APIRouter
from app.api.v1.endpoints import fetching, transformation, analytics, visitors_queries, concepts

api_router = APIRouter()

api_router.include_router(concepts.router, prefix="/concept", tags=["concepts"])
# api_router.include_router(fetching.router, prefix="/fetch", tags=["fetching"]) # Moved to visitors_queries
api_router.include_router(transformation.router, prefix="/states-normalization", tags=["transformation"])
api_router.include_router(visitors_queries.router, prefix="/visitors-queries", tags=["Visitors Queries"])
