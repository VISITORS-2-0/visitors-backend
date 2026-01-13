from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.concept_manager import ConceptManager, ConceptSchema

router = APIRouter()

@router.get("/{concept_name}", response_model=ConceptSchema)
def get_concept(concept_name: str, db: Session = Depends(get_db)):
    """
    Get concept definition. If not exists, generates and saves it (lazy creation).
    """
    return ConceptManager.get_or_create_concept(db, concept_name)
