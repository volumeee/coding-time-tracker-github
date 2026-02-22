"""Upstash Redis cache service (serverless-compatible)."""
import json
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CacheService:
    """Handles caching via Upstash Redis REST API."""

    def __init__(self):
        self._redis = None
        url = os.getenv("UPSTASH_REDIS_REST_URL")
        token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        if url and token:
            try:
                from upstash_redis import Redis
                self._redis = Redis(url=url, token=token)
                logger.info("Upstash Redis connected")
            except Exception as e:
                logger.warning(f"Redis init failed: {e}")

    @property
    def available(self) -> bool:
        return self._redis is not None

    def get(self, key: str) -> Optional[dict]:
        if not self._redis:
            return None
        try:
            data = self._redis.get(key)
            if data:
                return json.loads(data) if isinstance(data, str) else data
        except Exception as e:
            logger.warning(f"Cache GET error: {e}")
        return None

    def set(self, key: str, value: Any, ttl: int = 43200):
        if not self._redis:
            return
        try:
            self._redis.setex(key, ttl, json.dumps(value, default=str))
        except Exception as e:
            logger.warning(f"Cache SET error: {e}")

    def delete(self, key: str):
        if not self._redis:
            return
        try:
            self._redis.delete(key)
        except Exception as e:
            logger.warning(f"Cache DELETE error: {e}")

    def check_rate_limit(self, identifier: str, limit: int = 30, window: int = 60) -> bool:
        """Simple fixed-window rate limiter utilizing Redis INCR."""
        if not self._redis:
            return True  # If cache is unavailable, fallback to allow
        key = f"rl:{identifier}"
        try:
            current = self._redis.incr(key)
            if current == 1:
                self._redis.expire(key, window)
            return current <= limit
        except Exception as e:
            logger.warning(f"Rate limit error: {e}")
            return True
