"""
Cache Service - In-memory caching for analytics data
Provides fast access to pre-computed statistics
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl_seconds: int = 300):  # 5 minutes default
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if datetime.now() > entry["expires_at"]:
            # Expired, remove and return None
            del self._cache[key]
            return None
        
        logger.debug(f"Cache HIT: {key}")
        return entry["value"]
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self._cache[key] = {
            "value": value,
            "expires_at": datetime.now() + timedelta(seconds=ttl),
            "created_at": datetime.now()
        }
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    
    def invalidate(self, key: str) -> bool:
        """Remove specific key from cache"""
        if key in self._cache:
            del self._cache[key]
            logger.info(f"Cache INVALIDATED: {key}")
            return True
        return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Remove all keys matching pattern (simple startswith)"""
        keys_to_remove = [k for k in self._cache.keys() if k.startswith(pattern)]
        for key in keys_to_remove:
            del self._cache[key]
        if keys_to_remove:
            logger.info(f"Cache INVALIDATED {len(keys_to_remove)} keys matching '{pattern}'")
        return len(keys_to_remove)
    
    def clear(self) -> int:
        """Clear entire cache"""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache CLEARED: {count} entries removed")
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.now()
        valid_entries = sum(1 for e in self._cache.values() if now < e["expires_at"])
        expired_entries = len(self._cache) - valid_entries
        
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "keys": list(self._cache.keys())
        }
    
    def invalidate_all_agent_cache(self) -> int:
        """
        Clear ALL agent-related cache entries comprehensively
        
        This clears all cache patterns used by agent analytics:
        - dashboard:* - Dashboard metrics
        - agent:* - Individual agent performance
        - analytics:* - Legacy analytics cache
        
        Returns:
            Number of cache entries cleared
        """
        patterns = [
            "dashboard:",  # All dashboard metrics
            "agent:",      # Individual agent performance
            "analytics:",  # Legacy analytics (if still in use)
        ]
        
        total = 0
        for pattern in patterns:
            count = self.invalidate_pattern(pattern)
            total += count
            logger.info(f"Cleared {count} entries for pattern '{pattern}'")
        
        logger.info(f"Total agent cache entries cleared: {total}")
        return total
    
    def get_agent_cache_keys(self, agent_id: Optional[str] = None) -> List[str]:
        """
        Get all cache keys for specific agent or all agents
        
        Args:
            agent_id: Optional UUID string to filter by specific agent
        
        Returns:
            List of cache keys matching the criteria
        """
        if agent_id:
            # Get keys for specific agent
            return [k for k in self._cache.keys() if f"agent:{agent_id}" in k]
        # Get all agent-related keys
        return [k for k in self._cache.keys() if k.startswith("agent:")]
    
    def get_cache_state_by_pattern(self, pattern: str) -> Dict[str, Any]:
        """
        Get detailed cache state for a specific pattern
        
        Args:
            pattern: Pattern to search for (e.g., "dashboard:", "agent:")
        
        Returns:
            Dictionary with pattern statistics
        """
        matching_keys = [k for k in self._cache.keys() if k.startswith(pattern)]
        now = datetime.now()
        
        valid_keys = []
        expired_keys = []
        
        for key in matching_keys:
            entry = self._cache[key]
            if now < entry["expires_at"]:
                valid_keys.append(key)
            else:
                expired_keys.append(key)
        
        return {
            "pattern": pattern,
            "total_keys": len(matching_keys),
            "valid_keys": len(valid_keys),
            "expired_keys": len(expired_keys),
            "sample_keys": matching_keys[:5]  # Show first 5 as sample
        }


# Global cache instance
cache = CacheService(default_ttl_seconds=300)  # 5 minute TTL


def get_cache() -> CacheService:
    """Dependency injection for cache"""
    return cache
