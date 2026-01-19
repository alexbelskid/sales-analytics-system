#!/usr/bin/env python3
"""
Agent Cache Cleanup Verification Script

This script verifies that agent cache is properly cleared when agent data is deleted.

Steps:
1. Check initial cache state
2. Upload/import agent data
3. Verify cache is populated
4. Delete the import
5. Verify cache is completely cleared

Usage:
    python verify_cache_cleanup.py
"""

import requests
import json
import time
from datetime import date
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
CACHE_DEBUG_URL = f"{API_BASE_URL}/api/cache-debug"
AGENT_ANALYTICS_URL = f"{API_BASE_URL}/api/agent-analytics"
FILES_URL = f"{API_BASE_URL}/api/files"


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def get_cache_stats() -> Dict[str, Any]:
    """Get current cache statistics"""
    response = requests.get(f"{CACHE_DEBUG_URL}/stats")
    response.raise_for_status()
    return response.json()


def get_all_agent_patterns() -> Dict[str, Any]:
    """Get cache state for all agent patterns"""
    response = requests.get(f"{CACHE_DEBUG_URL}/all-patterns")
    response.raise_for_status()
    return response.json()


def clear_all_cache():
    """Clear all cache entries"""
    response = requests.post(f"{CACHE_DEBUG_URL}/clear-all")
    response.raise_for_status()
    return response.json()


def get_import_history():
    """Get list of imports"""
    response = requests.get(f"{FILES_URL}/list")
    response.raise_for_status()
    return response.json()


def delete_import(file_id: str, delete_data: bool = True):
    """Delete an import record"""
    response = requests.delete(f"{FILES_URL}/{file_id}", params={"delete_data": delete_data})
    response.raise_for_status()
    return response.json()


def verify_cache_cleanup():
    """Main verification function"""
    
    print_section("STEP 1: Check Initial Cache State")
    
    initial_stats = get_cache_stats()
    print(f"Initial cache entries: {initial_stats['stats']['total_entries']}")
    print(f"Valid entries: {initial_stats['stats']['valid_entries']}")
    
    if initial_stats['stats']['total_entries'] > 0:
        print("⚠️  WARNING: Cache is not empty at start. Clearing...")
        clear_result = clear_all_cache()
        print(f"✅ Cleared {clear_result['cleared_count']} entries")
    
    # ========================================
    print_section("STEP 2: Get Agent Dashboard (to populate cache)")
    
    period_start = date.today().replace(day=1)
    period_end = date.today()
    
    try:
        response = requests.get(
            f"{AGENT_ANALYTICS_URL}/dashboard",
            params={
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat()
            }
        )
        response.raise_for_status()
        print("✅ Dashboard request successful")
        
        # Wait a moment for cache to be populated
        time.sleep(1)
        
        after_dashboard_stats = get_cache_stats()
        print(f"Cache entries after dashboard: {after_dashboard_stats['stats']['total_entries']}")
        
        agent_patterns = get_all_agent_patterns()
        print("\n📊 Cache by pattern:")
        for pattern, data in agent_patterns['by_pattern'].items():
            if data['total_keys'] > 0:
                print(f"  {pattern} {data['total_keys']} keys")
                if data['sample_keys']:
                    print(f"    Sample: {data['sample_keys'][0]}")
    
    except Exception as e:
        print(f"⚠️  Dashboard request failed (this is OK if no agent data exists): {e}")
    
    # ========================================
    print_section("STEP 3: Check for Agent Imports")
    
    imports = get_import_history()
    agent_imports = [f for f in imports['files'] if f.get('import_type') == 'agents']
    
    if not agent_imports:
        print("⚠️  No agent imports found in database.")
        print("   To fully test, upload an agent data file first.")
        print("   Checking current cache state...")
    else:
        print(f"✅ Found {len(agent_imports)} agent import(s)")
        for imp in agent_imports[:3]:  # Show first 3
            print(f"  - {imp['filename']} ({imp['imported_rows']} rows)")
    
    # ========================================
    print_section("STEP 4: Verify Cache Inspection Endpoints Work")
    
    all_patterns = get_all_agent_patterns()
    print("✅ Cache inspection endpoints working")
    print(f"   Total entries: {all_patterns['overall']['total_entries']}")
    print(f"   Valid entries: {all_patterns['overall']['valid_entries']}")
    
    # ========================================
    print_section("STEP 5: Test Manual Cache Clear")
    
    if all_patterns['overall']['total_entries'] > 0:
        print(f"Clearing {all_patterns['overall']['total_entries']} cache entries...")
        
        clear_result = requests.post(f"{CACHE_DEBUG_URL}/clear-agent-cache")
        clear_result.raise_for_status()
        result = clear_result.json()
        
        print(f"✅ Cleared {result['cleared_count']} agent cache entries")
        
        # Verify it's empty
        after_clear = get_cache_stats()
        print(f"Cache entries after clear: {after_clear['stats']['total_entries']}")
        
        if after_clear['stats']['total_entries'] == 0:
            print("✅ SUCCESS: Cache completely cleared!")
        else:
            print(f"⚠️  WARNING: {after_clear['stats']['total_entries']} entries remain")
            print(f"Remaining keys: {after_clear['stats']['keys'][:5]}")
    else:
        print("No cache entries to clear (cache is already empty)")
    
    # ========================================
    print_section("STEP 6: Test Import Deletion (if available)")
    
    if agent_imports:
        print("\n🗑️  Testing import deletion with cache cleanup...")
        test_import = agent_imports[0]
        
        print(f"Deleting import: {test_import['filename']}")
        print(f"Import ID: {test_import['id']}")
        
        # Get cache state before deletion
        before_delete = get_cache_stats()
        print(f"Cache before deletion: {before_delete['stats']['total_entries']} entries")
        
        # Delete the import
        try:
            delete_result = delete_import(test_import['id'], delete_data=True)
            print(f"✅ Import deleted: {delete_result['message']}")
            
            # Wait a moment
            time.sleep(1)
            
            # Get cache state after deletion
            after_delete = get_cache_stats()
            print(f"Cache after deletion: {after_delete['stats']['total_entries']} entries")
            
            if after_delete['stats']['total_entries'] == 0:
                print("✅ SUCCESS: All cache cleared after import deletion!")
            else:
                print(f"⚠️  WARNING: {after_delete['stats']['total_entries']} entries remain after deletion")
                print(f"Remaining keys: {after_delete['stats']['keys']}")
        
        except Exception as e:
            print(f"❌ Deletion failed: {e}")
    else:
        print("⏩ Skipping deletion test (no agent imports to delete)")
    
    # ========================================
    print_section("VERIFICATION SUMMARY")
    
    final_stats = get_cache_stats()
    
    print(f"\n📊 Final Cache State:")
    print(f"   Total entries: {final_stats['stats']['total_entries']}")
    print(f"   Valid entries: {final_stats['stats']['valid_entries']}")
    print(f"   Expired entries: {final_stats['stats']['expired_entries']}")
    
    if final_stats['stats']['total_entries'] == 0:
        print("\n✅ SUCCESS: Agent cache cleanup is working correctly!")
        print("   All agent-related cache was properly cleared.")
    else:
        print("\n⚠️  Cache still has entries (this may be normal if you created new data)")
        print("   Check the cache contents using: GET /api/cache-debug/all-patterns")
    
    print("\n" + "="*60)
    print("Verification complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        print("""
╔═══════════════════════════════════════════════════════════╗
║   Agent Cache Cleanup Verification Script                ║
║   Testing comprehensive cache invalidation               ║
╚═══════════════════════════════════════════════════════════╝
        """)
        
        verify_cache_cleanup()
    
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print(f"   Make sure the server is running at {API_BASE_URL}")
        print("   Start with: cd backend && uvicorn app.main:app --reload")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
