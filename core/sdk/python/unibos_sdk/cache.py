"""
UNIBOS Cache Service
Provides unified caching interface for modules
"""

import logging
from typing import Any, Optional
from datetime import timedelta


class UnibosCache:
    """
    Unified cache interface for UNIBOS modules
    Wraps Django cache with additional features
    """

    def __init__(self, namespace: Optional[str] = None):
        """
        Initialize cache service

        Args:
            namespace: Optional namespace prefix for cache keys
        """
        self.namespace = namespace or "unibos"
        self.logger = logging.getLogger(f"unibos.cache.{self.namespace}")
        self._cache = None

    def _get_cache(self):
        """Get Django cache instance lazily"""
        if self._cache is None:
            try:
                from django.core.cache import cache
                self._cache = cache
            except ImportError:
                self.logger.warning("Django cache not available, using null cache")
                self._cache = NullCache()
        return self._cache

    def _make_key(self, key: str) -> str:
        """Create namespaced cache key"""
        return f"{self.namespace}:{key}"

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        try:
            cache_key = self._make_key(key)
            value = self._get_cache().get(cache_key, default)
            return value
        except Exception as e:
            self.logger.error(f"Error getting cache key '{key}': {e}")
            return default

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            timeout: Cache timeout in seconds (None = default, 0 = forever)

        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = self._make_key(key)
            self._get_cache().set(cache_key, value, timeout)
            return True
        except Exception as e:
            self.logger.error(f"Error setting cache key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = self._make_key(key)
            self._get_cache().delete(cache_key)
            return True
        except Exception as e:
            self.logger.error(f"Error deleting cache key '{key}': {e}")
            return False

    def clear(self) -> bool:
        """
        Clear all cache entries in this namespace

        Returns:
            True if successful, False otherwise
        """
        try:
            self._get_cache().clear()
            return True
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return False


class NullCache:
    """Null cache implementation for when Django cache is not available"""

    def get(self, key: str, default: Any = None) -> Any:
        return default

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        pass

    def delete(self, key: str) -> None:
        pass

    def clear(self) -> None:
        pass
