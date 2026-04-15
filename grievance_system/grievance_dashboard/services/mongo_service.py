"""
MongoDB Integration Service
Handles storage and retrieval of grievance analytics data
"""

import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Try to import pymongo; fallback to mock if unavailable (dev mode)
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False


class MongoService:
    """MongoDB service with graceful fallback"""

    _client = None
    _db = None

    @classmethod
    def connect(cls, uri: str, db_name: str):
        if not MONGO_AVAILABLE:
            logger.warning("PyMongo not installed. Running in file-cache mode.")
            return None
        try:
            cls._client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            cls._client.admin.command('ping')
            cls._db = cls._client[db_name]
            logger.info(f"MongoDB connected: {db_name}")
            return cls._db
        except Exception as e:
            logger.warning(f"MongoDB unavailable ({e}). Running without DB persistence.")
            cls._client = None
            cls._db = None
            return None

    @classmethod
    def get_db(cls):
        return cls._db

    @classmethod
    def is_connected(cls) -> bool:
        return cls._db is not None

    @classmethod
    def upsert_insights(cls, insights: dict):
        if not cls.is_connected():
            return
        try:
            cls._db['insights'].replace_one(
                {'_id': 'latest'},
                {'_id': 'latest', 'data': insights, 'updated_at': datetime.now()},
                upsert=True
            )
        except Exception as e:
            logger.error(f"MongoDB upsert_insights error: {e}")

    @classmethod
    def get_insights(cls) -> dict:
        if not cls.is_connected():
            return {}
        try:
            doc = cls._db['insights'].find_one({'_id': 'latest'})
            return doc['data'] if doc else {}
        except Exception as e:
            logger.error(f"MongoDB get_insights error: {e}")
            return {}

    @classmethod
    def log_alert(cls, alert: dict):
        if not cls.is_connected():
            return
        try:
            alert['timestamp'] = datetime.now()
            cls._db['alerts'].insert_one(alert)
        except Exception as e:
            logger.error(f"MongoDB log_alert error: {e}")

    @classmethod
    def get_alert_history(cls, limit: int = 20) -> list:
        if not cls.is_connected():
            return []
        try:
            docs = list(cls._db['alerts'].find({}, {'_id': 0}).sort('timestamp', -1).limit(limit))
            return docs
        except Exception as e:
            logger.error(f"MongoDB get_alert_history error: {e}")
            return []

    @classmethod
    def save_report(cls, report: dict):
        if not cls.is_connected():
            return
        try:
            report['created_at'] = datetime.now()
            cls._db['reports'].insert_one(report)
        except Exception as e:
            logger.error(f"MongoDB save_report error: {e}")

    @classmethod
    def get_report_history(cls, limit: int = 10) -> list:
        if not cls.is_connected():
            return []
        try:
            docs = list(cls._db['reports'].find({}, {'_id': 0}).sort('created_at', -1).limit(limit))
            return docs
        except Exception as e:
            logger.error(f"MongoDB get_report_history error: {e}")
            return []

    @classmethod
    def cache_dashboard(cls, key: str, data: dict):
        if not cls.is_connected():
            return
        try:
            cls._db['dashboard_cache'].replace_one(
                {'_id': key},
                {'_id': key, 'data': data, 'cached_at': datetime.now()},
                upsert=True
            )
        except Exception as e:
            logger.error(f"MongoDB cache_dashboard error: {e}")

    @classmethod
    def get_cached_dashboard(cls, key: str) -> dict:
        if not cls.is_connected():
            return {}
        try:
            doc = cls._db['dashboard_cache'].find_one({'_id': key})
            return doc['data'] if doc else {}
        except Exception as e:
            return {}

    @classmethod
    def store_grievance_records(cls, records: list, batch_size: int = 500):
        """Store cleaned grievance records"""
        if not cls.is_connected():
            return 0
        try:
            col = cls._db['grievances']
            col.drop()
            inserted = 0
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                col.insert_many(batch)
                inserted += len(batch)
            return inserted
        except Exception as e:
            logger.error(f"MongoDB store_grievance_records error: {e}")
            return 0
