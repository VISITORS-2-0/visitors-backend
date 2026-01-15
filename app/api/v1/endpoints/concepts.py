from fastapi import APIRouter
from app.services.concept_manager import ConceptManager
from app.models.schemas import ConceptSchema

router = APIRouter()

@router.get("/{concept_name}", response_model=ConceptSchema)
def get_concept(concept_name: str):
    """
    Get concept definition. If not exists, generates and saves it (lazy creation).
    """
    return ConceptManager.get_or_create_concept(concept_name)
