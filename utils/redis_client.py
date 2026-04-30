import redis
from typing import Any, Optional
from .config import Config

class RedisClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB
            )
        return cls._instance
    
    def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        try:
            if expire:
                self._client.setex(key, expire, value)
            else:
                self._client.set(key, value)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[str]:
        try:
            value = self._client.get(key)
            return value.decode('utf-8') if value else None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        try:
            self._client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        try:
            return self._client.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False