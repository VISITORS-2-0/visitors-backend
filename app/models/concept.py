from sqlalchemy import Column, Integer, String, JSON
from app.core.database import Base

class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(String)
    allowed_values = Column(JSON)
