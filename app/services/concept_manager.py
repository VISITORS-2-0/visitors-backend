import random
from typing import Dict, Any
from pydantic import BaseModel
from app.core.database import SessionLocal
from app.models.concept import Concept
from app.models.schemas import ConceptSchema

class ConceptManager:
    @staticmethod
    def get_or_create_concept(concept_name: str) -> ConceptSchema:
        with SessionLocal() as db:
            # Check if concept exists
            concept = db.query(Concept).filter(Concept.name == concept_name).first()
            
            if concept:
                return ConceptSchema(
                    name=concept.name,
                    type=concept.type,
                    allowed_values=concept.allowed_values
                )
                
            # If not, generate it
            new_raw_concept = ConceptManager._generate_random_raw_concept(concept_name)
            
            # Save to DB
            db_concept = Concept(
                name=new_raw_concept["concept_name"],
                type=new_raw_concept["concept_type"],
                allowed_values=new_raw_concept["allowed_values"]
            )
            db.add(db_concept)
            db.commit()
            db.refresh(db_concept)
            
            return ConceptSchema(
                name=db_concept.name,
                type=db_concept.type,
                allowed_values=db_concept.allowed_values
            )

    @staticmethod
    def _generate_random_raw_concept(concept_name):
        """
        Generates a random RawConcept object based on TAK Schema v24.
        """
        # For now, only rawOrdinal is supported as per user request
        concept_types = [
            "rawOrdinal"
        ]
        
        selected_type = random.choice(concept_types)
        
        result = {
            "concept_name": concept_name,
            "concept_type": selected_type,
            "allowed_values": {}
        }

        if selected_type == "rawOrdinal":
            # Example sets
            options = [
                ["Low", "Medium", "High"],
                ["Trace", "1+", "2+", "3+"],
                ["Stage I", "Stage II", "Stage III", "Stage IV"]
            ]
            values = random.choice(options)
            result["allowed_values"] = {
                "values": values,
                "ordering": "asc"
            }
            
        return result
