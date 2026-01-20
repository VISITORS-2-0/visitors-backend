from fastapi import APIRouter
from app.services.concept_manager import ConceptManager
from app.models.schemas import ConceptSchema
import json
from pathlib import Path

router = APIRouter()

@router.get("/menu")
def get_menu():
    """
    Get menu from json file.
    """
    try:
        menu_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "menu.json"
        
        with open(menu_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        # In production we might want to log this or return a 500, but for now getting the error detail is helpful if it persists.
        # But since we are confident it's the encoding, let's revert to a standard return or basic error if fails.
        raise e


@router.get("/{concept_name}", response_model=ConceptSchema)
def get_concept(concept_name: str):
    """
    Get concept definition. If not exists, generates and saves it (lazy creation).
    """
    return ConceptManager.get_or_create_concept(concept_name)
