from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./visitors.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import models here to ensure they are registered with Base metadata
from app.models.function_cache import FunctionCache
import os

def delete_db(db_path: str = "./visitors.db"):
    """
    Deletes the SQLite database file if it exists.
    Ensures connections are closed before deletion.
    """
    try:
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Database at {db_path} deleted successfully.")
            return True
        else:
            print(f"No database found at {db_path}.")
            return False
    except Exception as e:
        print(f"Error deleting database: {e}")
        return False
