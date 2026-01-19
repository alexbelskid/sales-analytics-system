"""
Cache Debugging Router
Provides endpoints to inspect and verify cache state
Useful for debugging cache-related issues
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from app.services.cache_service import cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cache-debug", tags=["Cache Debug"])


@router.get("/stats")
async def get_cache_stats():
    """
    Get overall cache statistics
    
    Returns:
        - Total entries in cache
        - Valid (non-expired) entries
        - Expired entries
        - List of all cache keys
    """
    try:
        stats = cache.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(500, str(e))


@router.get("/agent-keys")
async def get_agent_cache_keys(agent_id: Optional[str] = None):
    """
    Get all agent-related cache keys
    
    Args:
        agent_id: Optional UUID to filter for specific agent
    
    Returns:
        List of cache keys related to agents
    """
    try:
        keys = cache.get_agent_cache_keys(agent_id)
        return {
            "success": True,
            "agent_id": agent_id,
            "count": len(keys),
            "keys": keys
        }
    except Exception as e:
        logger.error(f"Error getting agent cache keys: {e}")
        raise HTTPException(500, str(e))


@router.get("/pattern/{pattern}")
async def get_cache_by_pattern(pattern: str):
    """
    Get cache state for a specific pattern
    
    Args:
        pattern: Pattern to search (e.g., "dashboard", "agent", "analytics")
    
    Returns:
        Detailed statistics for the pattern
    """
    try:
        # Add colon to pattern for consistency
        search_pattern = f"{pattern}:" if not pattern.endswith(":") else pattern
        
        state = cache.get_cache_state_by_pattern(search_pattern)
        return {
            "success": True,
            "state": state
        }
    except Exception as e:
        logger.error(f"Error getting cache state for pattern: {e}")
        raise HTTPException(500, str(e))


@router.get("/all-patterns")
async def get_all_agent_patterns():
    """
    Get cache state for all agent-related patterns
    
    Returns:
        Statistics for dashboard, agent, and analytics patterns
    """
    try:
        patterns = ["dashboard:", "agent:", "analytics:"]
        
        results = {}
        for pattern in patterns:
            results[pattern] = cache.get_cache_state_by_pattern(pattern)
        
        overall_stats = cache.get_stats()
        
        return {
            "success": True,
            "overall": {
                "total_entries": overall_stats["total_entries"],
                "valid_entries": overall_stats["valid_entries"],
                "expired_entries": overall_stats["expired_entries"]
            },
            "by_pattern": results
        }
    except Exception as e:
        logger.error(f"Error getting all patterns: {e}")
        raise HTTPException(500, str(e))


@router.post("/clear-all")
async def clear_all_cache():
    """
    Clear ALL cache entries (nuclear option)
    
    Returns:
        Number of entries cleared
    """
    try:
        count = cache.clear()
        logger.info(f"Manually cleared all cache: {count} entries")
        
        return {
            "success": True,
            "message": "All cache cleared",
            "cleared_count": count
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(500, str(e))


@router.post("/clear-agent-cache")
async def clear_agent_cache():
    """
    Clear all agent-related cache entries
    
    Returns:
        Number of entries cleared
    """
    try:
        count = cache.invalidate_all_agent_cache()
        logger.info(f"Manually cleared agent cache: {count} entries")
        
        return {
            "success": True,
            "message": "Agent cache cleared",
            "cleared_count": count
        }
    except Exception as e:
        logger.error(f"Error clearing agent cache: {e}")
        raise HTTPException(500, str(e))
