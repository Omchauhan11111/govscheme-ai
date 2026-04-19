from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import ConnectionFailure
from datetime import datetime
import logging

from .config import settings

logger = logging.getLogger(__name__)

client = None
db = None

def connect_db():
    global client, db
    try:
        client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Test connection
        db = client[settings.DB_NAME]
        _create_indexes()
        logger.info("✅ MongoDB connected successfully")
        return True
    except ConnectionFailure as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False

def _create_indexes():
    """Create indexes for better performance"""
    try:
        db.schemes.create_index([("url", ASCENDING)], unique=True)
    except Exception:
        pass
    try:
        db.schemes.create_index([("published_date", DESCENDING)])
    except Exception:
        pass
    try:
        db.schemes.create_index([("category", ASCENDING)])
    except Exception:
        pass
    try:
        # Purana conflicting text index drop karo
        db.schemes.drop_index("title_text")
    except Exception:
        pass
    try:
        db.schemes.create_index([("title", TEXT), ("summary", TEXT)])
    except Exception as e:
        logger.warning(f"Text index skipped: {e}")
    try:
        db.blogs.create_index([("scheme_id", ASCENDING)])
        db.blogs.create_index([("created_at", DESCENDING)])
        db.blogs.create_index([("status", ASCENDING)])
    except Exception:
        pass
    try:
        db.pipeline_logs.create_index([("timestamp", DESCENDING)])
    except Exception:
        pass

def get_db():
    return db

def disconnect_db():
    global client
    if client:
        client.close()
        logger.info("MongoDB disconnected")
