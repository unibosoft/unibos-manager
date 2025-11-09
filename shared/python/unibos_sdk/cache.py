"""
UNIBOS Cache Helpers

Redis cache utilities for inter-module communication and data sharing.
"""

from typing import Any, Optional
from django.core.cache import cache
from django.conf import settings
import json


class UnibosCache:
    """
    Cache helpers for UNIBOS modules

    Uses Redis for cross-module data sharing and caching.
    """

    DEFAULT_TIMEOUT = 300  # 5 minutes

    @staticmethod
    def _make_key(namespace: str, key: str) -> str:
        """
        Create namespaced cache key

        Args:
            namespace: Namespace (usually module_id)
            key: Key name

        Returns:
            Namespaced key (e.g., 'unibos:birlikteyiz:earthquake_count')
        """
        prefix = getattr(settings, 'CACHE_KEY_PREFIX', 'unibos')
        return f'{prefix}:{namespace}:{key}'

    @staticmethod
    def set(namespace: str, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        Set value in cache

        Args:
            namespace: Namespace (usually module_id)
            key: Key name
            value: Value to cache (will be JSON serialized if complex type)
            timeout: Timeout in seconds (default: 5 minutes)

        Returns:
            True if successful
        """
        cache_key = UnibosCache._make_key(namespace, key)
        timeout = timeout or UnibosCache.DEFAULT_TIMEOUT

        try:
            cache.set(cache_key, value, timeout)
            return True
        except Exception:
            return False

    @staticmethod
    def get(namespace: str, key: str, default: Any = None) -> Any:
        """
        Get value from cache

        Args:
            namespace: Namespace (usually module_id)
            key: Key name
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        cache_key = UnibosCache._make_key(namespace, key)

        try:
            value = cache.get(cache_key, default)
            return value
        except Exception:
            return default

    @staticmethod
    def delete(namespace: str, key: str) -> bool:
        """
        Delete value from cache

        Args:
            namespace: Namespace
            key: Key name

        Returns:
            True if successful
        """
        cache_key = UnibosCache._make_key(namespace, key)

        try:
            cache.delete(cache_key)
            return True
        except Exception:
            return False

    @staticmethod
    def exists(namespace: str, key: str) -> bool:
        """
        Check if key exists in cache

        Args:
            namespace: Namespace
            key: Key name

        Returns:
            True if key exists
        """
        cache_key = UnibosCache._make_key(namespace, key)

        try:
            return cache.get(cache_key) is not None
        except Exception:
            return False

    @staticmethod
    def increment(namespace: str, key: str, delta: int = 1) -> Optional[int]:
        """
        Increment numeric value in cache

        Args:
            namespace: Namespace
            key: Key name
            delta: Amount to increment (default: 1)

        Returns:
            New value or None if failed
        """
        cache_key = UnibosCache._make_key(namespace, key)

        try:
            return cache.incr(cache_key, delta)
        except ValueError:
            # Key doesn't exist or isn't numeric
            cache.set(cache_key, delta, UnibosCache.DEFAULT_TIMEOUT)
            return delta
        except Exception:
            return None

    @staticmethod
    def decrement(namespace: str, key: str, delta: int = 1) -> Optional[int]:
        """
        Decrement numeric value in cache

        Args:
            namespace: Namespace
            key: Key name
            delta: Amount to decrement (default: 1)

        Returns:
            New value or None if failed
        """
        cache_key = UnibosCache._make_key(namespace, key)

        try:
            return cache.decr(cache_key, delta)
        except ValueError:
            # Key doesn't exist or isn't numeric
            cache.set(cache_key, -delta, UnibosCache.DEFAULT_TIMEOUT)
            return -delta
        except Exception:
            return None

    @staticmethod
    def set_user_data(user_id: int, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        Set user-specific data in cache

        Args:
            user_id: User ID
            key: Key name
            value: Value to cache
            timeout: Timeout in seconds

        Returns:
            True if successful
        """
        namespace = f'user:{user_id}'
        return UnibosCache.set(namespace, key, value, timeout)

    @staticmethod
    def get_user_data(user_id: int, key: str, default: Any = None) -> Any:
        """
        Get user-specific data from cache

        Args:
            user_id: User ID
            key: Key name
            default: Default value if not found

        Returns:
            Cached value or default
        """
        namespace = f'user:{user_id}'
        return UnibosCache.get(namespace, key, default)

    @staticmethod
    def delete_user_data(user_id: int, key: str) -> bool:
        """
        Delete user-specific data from cache

        Args:
            user_id: User ID
            key: Key name

        Returns:
            True if successful
        """
        namespace = f'user:{user_id}'
        return UnibosCache.delete(namespace, key)

    @staticmethod
    def clear_namespace(namespace: str) -> bool:
        """
        Clear all keys in a namespace

        WARNING: This can be slow for large namespaces

        Args:
            namespace: Namespace to clear

        Returns:
            True if successful
        """
        try:
            # This is not efficient for Redis, but works
            # In production, consider using Redis SCAN
            prefix = UnibosCache._make_key(namespace, '')
            cache.delete_pattern(f'{prefix}*')
            return True
        except Exception:
            return False

    @staticmethod
    def set_module_data(module_id: str, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        Set module-specific data (convenience method)

        Args:
            module_id: Module identifier
            key: Key name
            value: Value to cache
            timeout: Timeout in seconds

        Returns:
            True if successful
        """
        return UnibosCache.set(module_id, key, value, timeout)

    @staticmethod
    def get_module_data(module_id: str, key: str, default: Any = None) -> Any:
        """
        Get module-specific data (convenience method)

        Args:
            module_id: Module identifier
            key: Key name
            default: Default value

        Returns:
            Cached value or default
        """
        return UnibosCache.get(module_id, key, default)
