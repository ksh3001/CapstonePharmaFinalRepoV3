"""CachePort + in-process memo. Adapters live in services/integration."""

from packages.cache.store import CACHE, Cache, ProtectedCacheError, PROTECTED_NAMESPACES

__all__ = ["CACHE", "Cache", "ProtectedCacheError", "PROTECTED_NAMESPACES"]
