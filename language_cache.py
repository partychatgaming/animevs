# language_cache.py
from typing import Dict, Optional
from cachetools import TTLCache

class LanguageCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.cache = TTLCache(maxsize=10000, ttl=3600)  # 1 hour cache
            self.initialized = True

    def get_user_language(self, users_col, user_id: int) -> str:
        """Get user's language preference"""
        # Try cache first
        if user_id in self.cache:
            return self.cache[user_id]

        # Query MongoDB using existing collection
        user_data = users_col.find_one(
            {"DID": str(user_id)},
            projection={"LANGUAGE": 1}
        )
        
        # Get language or default to 'en'
        language = user_data.get("LANGUAGE", "en") if user_data else "en"
        
        # Cache the result
        self.cache[user_id] = language
        
        return language

    def set_user_language(self, users_col, user_id: int, language: str) -> None:
        """Update user's language preference"""
        # Update MongoDB
        users_col.update_one(
            {"DID": str(user_id)},
            {"$set": {"LANGUAGE": language}},
            upsert=True
        )
        
        # Update cache
        self.cache[user_id] = language

    def clear_user_cache(self, user_id: int) -> None:
        """Clear a specific user's cached language"""
        self.cache.pop(user_id, None)