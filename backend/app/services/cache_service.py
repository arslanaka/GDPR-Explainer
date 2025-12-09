import os
import json
import hashlib
import logging
from typing import Optional, Any, Union
from datetime import timedelta
from redis import Redis, ConnectionPool, RedisError
from redis.retry import Retry
from redis.backoff import ExponentialBackoff
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))

# Cache TTL configurations (in seconds)
CACHE_TTL_CHAT = int(os.getenv("CACHE_TTL_CHAT", "3600"))  # 1 hour
CACHE_TTL_SEARCH = int(os.getenv("CACHE_TTL_SEARCH", "7200"))  # 2 hours
CACHE_TTL_ARTICLE = int(os.getenv("CACHE_TTL_ARTICLE", "86400"))  # 24 hours
CACHE_TTL_EXPLANATION = int(os.getenv("CACHE_TTL_EXPLANATION", "43200"))  # 12 hours


class CacheService:
    """
    Production-ready Redis caching service with:
    - Connection pooling for scalability
    - Automatic retry with exponential backoff
    - Graceful degradation on Redis failures
    - Structured key namespacing
    - Type-safe serialization
    """

    def __init__(self):
        """Initialize Redis connection pool with retry logic"""
        try:
            # Connection pool for efficient connection reuse
            self.pool = ConnectionPool(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                max_connections=REDIS_MAX_CONNECTIONS,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )

            # Redis client with automatic retry
            retry = Retry(ExponentialBackoff(), retries=3)
            self.redis = Redis(
                connection_pool=self.pool,
                retry=retry,
                retry_on_error=[RedisError],
            )

            # Test connection
            self.redis.ping()
            logger.info(f"✅ Redis connected successfully at {REDIS_HOST}:{REDIS_PORT}")
            self.enabled = True

        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Caching disabled.")
            self.enabled = False
            self.redis = None

    def _generate_key(self, namespace: str, identifier: str, **kwargs) -> str:
        """
        Generate a consistent cache key with namespace.
        
        Args:
            namespace: Cache category (e.g., 'chat', 'search', 'article')
            identifier: Primary identifier (e.g., query text, article_id)
            **kwargs: Additional parameters to include in key (e.g., language, model)
        
        Returns:
            Formatted cache key: "namespace:hash:params"
        """
        # Create a deterministic hash of the identifier
        hash_input = identifier.lower().strip()
        key_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

        # Add additional parameters to key
        params = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()) if v)
        
        if params:
            return f"{namespace}:{key_hash}:{params}"
        return f"{namespace}:{key_hash}"

    def get(self, namespace: str, identifier: str, **kwargs) -> Optional[Any]:
        """
        Retrieve cached data.
        
        Args:
            namespace: Cache category
            identifier: Primary identifier
            **kwargs: Additional key parameters
        
        Returns:
            Cached data or None if not found/error
        """
        if not self.enabled:
            return None

        try:
            key = self._generate_key(namespace, identifier, **kwargs)
            cached = self.redis.get(key)

            if cached:
                logger.debug(f"✅ Cache HIT: {key}")
                return json.loads(cached)
            
            logger.debug(f"❌ Cache MISS: {key}")
            return None

        except Exception as e:
            logger.error(f"Cache GET error for {namespace}:{identifier}: {e}")
            return None

    def set(
        self,
        namespace: str,
        identifier: str,
        data: Any,
        ttl: Optional[int] = None,
        **kwargs
    ) -> bool:
        """
        Store data in cache.
        
        Args:
            namespace: Cache category
            identifier: Primary identifier
            data: Data to cache (must be JSON serializable)
            ttl: Time-to-live in seconds (uses namespace default if None)
            **kwargs: Additional key parameters
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            key = self._generate_key(namespace, identifier, **kwargs)
            
            # Use namespace-specific TTL if not provided
            if ttl is None:
                ttl = self._get_default_ttl(namespace)

            # Serialize and store
            serialized = json.dumps(data, ensure_ascii=False)
            self.redis.setex(key, ttl, serialized)
            
            logger.debug(f"💾 Cache SET: {key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Cache SET error for {namespace}:{identifier}: {e}")
            return False

    def delete(self, namespace: str, identifier: str, **kwargs) -> bool:
        """
        Delete cached data.
        
        Args:
            namespace: Cache category
            identifier: Primary identifier
            **kwargs: Additional key parameters
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            key = self._generate_key(namespace, identifier, **kwargs)
            self.redis.delete(key)
            logger.debug(f"🗑️ Cache DELETE: {key}")
            return True

        except Exception as e:
            logger.error(f"Cache DELETE error for {namespace}:{identifier}: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.
        
        Args:
            pattern: Redis key pattern (e.g., 'chat:*', 'article:ART-5:*')
        
        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            return 0

        try:
            keys = list(self.redis.scan_iter(match=pattern, count=100))
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"🗑️ Invalidated {deleted} keys matching '{pattern}'")
                return deleted
            return 0

        except Exception as e:
            logger.error(f"Cache invalidate pattern error for {pattern}: {e}")
            return 0

    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        if not self.enabled:
            return {"enabled": False}

        try:
            info = self.redis.info("stats")
            memory = self.redis.info("memory")
            
            return {
                "enabled": True,
                "total_keys": self.redis.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
                "memory_used_mb": round(memory.get("used_memory", 0) / 1024 / 1024, 2),
                "memory_peak_mb": round(memory.get("used_memory_peak", 0) / 1024 / 1024, 2),
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "error": str(e)}

    def _get_default_ttl(self, namespace: str) -> int:
        """Get default TTL for a namespace"""
        ttl_map = {
            "chat": CACHE_TTL_CHAT,
            "search": CACHE_TTL_SEARCH,
            "article": CACHE_TTL_ARTICLE,
            "explanation": CACHE_TTL_EXPLANATION,
        }
        return ttl_map.get(namespace, 3600)  # Default 1 hour

    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)

    def close(self):
        """Close Redis connection pool"""
        if self.enabled and self.pool:
            self.pool.disconnect()
            logger.info("Redis connection pool closed")


# Singleton instance
cache_service = CacheService()
