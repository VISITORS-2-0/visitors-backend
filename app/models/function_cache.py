from sqlalchemy import Column, String, Integer, Text, DateTime
from datetime import datetime
from app.core.database import Base

class FunctionCache(Base):
    __tablename__ = "function_cache"

    id = Column(Integer, primary_key=True, index=True)
    function_name = Column(String, index=True)
    cache_key = Column(String, unique=True, index=True)
    result_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
