from fastapi import APIRouter
from app.services.concept_manager import ConceptManager
from app.models.schemas import ConceptSchema
import json
from pathlib import Path

router = APIRouter()

from app.services.menu_builder import get_navigation_structure
from app.core.config import settings

@router.get("/menu")
def get_menu():
    """
    Get menu by scanning TakEntities XML files.
    """
    try:
        # Pass the directory to get_navigation_structure to lazy-load if not built
        return get_navigation_structure(settings.TAK_FILES_DIR)
    except Exception as e:
        # In production we might want to log this or return a 500, but for now getting the error detail is helpful if it persists.
        raise e


@router.get("/{concept_name}", response_model=ConceptSchema)
def get_concept(concept_name: str):
    """
    Get concept definition. If not exists, generates and saves it (lazy creation).
    """
    return ConceptManager.get_or_create_concept(concept_name)
