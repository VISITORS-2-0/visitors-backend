import hashlib
import json
import functools
import pickle
import codecs
from pydantic.json import pydantic_encoder
from app.core.database import SessionLocal
from app.models.function_cache import FunctionCache

def db_cache(func):
    """
    Decorator to cache function results in the database.
    Hash includes: module name, function name, args, kwargs.
    Uses pickle for serialization to handle complex objects (Pydantic models, etc.).
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. Create a stable representation of arguments for hashing
        try:
            serialize_args = json.dumps(args, default=pydantic_encoder, sort_keys=True)
            serialize_kwargs = json.dumps(kwargs, default=pydantic_encoder, sort_keys=True)
        except Exception as e:
            print(f"Cache key serialization failed for {func.__name__}: {e}")
            return func(*args, **kwargs)

        # 2. Construct unique cache key
        # User requirement: include function name
        raw_key = f"{func.__module__}:{func.__name__}:{serialize_args}:{serialize_kwargs}"
        cache_key = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

        # 3. Check DB
        db = SessionLocal()
        try:
            cached_entry = db.query(FunctionCache).filter(FunctionCache.cache_key == cache_key).first()
            if cached_entry:
                try:
                    # Decode base64 then unpickle
                    decoded = codecs.decode(cached_entry.result_json.encode('utf-8'), "base64")
                    return pickle.loads(decoded)
                except Exception as e:
                    print(f"Cache deserialization failed: {e}. Re-computing.")
                    # Fall through to re-compute
        except Exception as e:
            print(f"DB cache read error: {e}")
        finally:
            db.close()

        # 4. Compute result
        result = func(*args, **kwargs)

        # 5. Save to DB
        db = SessionLocal()
        try:
            # Pickle then encode to base64 string
            pickled = pickle.dumps(result)
            encoded_str = codecs.encode(pickled, "base64").decode('utf-8')
            
            # Check existence again to avoid race conditions (simple version)
            existing = db.query(FunctionCache).filter(FunctionCache.cache_key == cache_key).first()
            if not existing:
                new_entry = FunctionCache(
                    function_name=func.__name__,
                    cache_key=cache_key,
                    result_json=encoded_str # Storing pickled object string
                )
                db.add(new_entry)
                db.commit()
        except Exception as e:
            print(f"DB cache write error: {e}")
        finally:
            db.close()

        return result
        
    return wrapper
