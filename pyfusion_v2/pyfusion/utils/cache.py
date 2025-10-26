"""
Caching system with TTL support
"""
import time
import pickle
from typing import Any, Optional
from ..core.logging import log

class Cache:
    """In-memory cache with TTL support"""
    
    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cache value with TTL"""
        try:
            self._cleanup_expired()
            
            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
            return True
        except Exception as e:
            log.error(f"Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        self._cleanup_expired()
        
        if key in self._cache:
            item = self._cache[key]
            return item['value']
        return None
    
    def delete(self, key: str) -> bool:
        """Delete cache value"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        self._cache.clear()
        return True
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        self._cleanup_expired()
        return key in self._cache
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        current_time = time.time()
        
        # Only cleanup every cleanup_interval to avoid performance issues
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        expired_keys = [
            key for key, item in self._cache.items()
            if item['expires_at'] < current_time
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        self._last_cleanup = current_time
        if expired_keys:
            log.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        self._cleanup_expired()
        return {
            'total_entries': len(self._cache),
            'memory_usage': f"{len(pickle.dumps(self._cache))} bytes"
        }