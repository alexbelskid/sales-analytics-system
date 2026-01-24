import pytest
from unittest.mock import MagicMock, patch
from app.routers.analytics import get_dashboard, get_top_customers, get_top_products
from app.services.cache_service import cache
from app.models.sales import DashboardMetrics

# We need to patch supabase in the analytics module because it was imported before the global patch
@pytest.fixture(autouse=True)
def patch_analytics_supabase(mock_supabase):
    with patch("app.routers.analytics.supabase", mock_supabase):
        yield

@pytest.mark.asyncio
async def test_dashboard_caching_miss(mock_supabase):
    """
    Test that proves dashboard caching is currently broken.
    We expect this test to FAIL if we assert correct behavior (1 DB call).
    Or PASS if we assert current broken behavior (2 DB calls).

    To be useful as a regression test later, we will write it asserting CORRECT behavior,
    so it fails now and passes after fix.
    """

    # Setup mock return data for RPC
    mock_supabase.rpc.return_value.execute.return_value.data = [{
        "total_revenue": 1000,
        "total_sales": 10,
        "average_check": 100
    }]
    # Also setup fallback just in case RPC fails (though we didn't mock rpc failure)
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    # Clear cache
    cache.clear()
    mock_supabase.reset_mock()

    # 1. Unfiltered request
    # First call - should hit DB
    # We must pass None explicitly because default values are Query(None) objects
    await get_dashboard(start_date=None, end_date=None, customer_id=None, agent_id=None, product_id=None, region=None, category=None, force_refresh=False)
    assert mock_supabase.rpc.call_count == 1

    # Second call - SHOULD hit cache
    await get_dashboard(start_date=None, end_date=None, customer_id=None, agent_id=None, product_id=None, region=None, category=None, force_refresh=False)

    # CURRENT BUG: It uses different keys for read/write, so it hits DB again.
    # We assert 1 to demonstrate the desired behavior.
    # This assertion is expected to FAIL.
    assert mock_supabase.rpc.call_count == 1, "Unfiltered dashboard request did not hit cache!"

@pytest.mark.asyncio
async def test_dashboard_filtered_caching_miss(mock_supabase):
    # Setup mock
    mock_supabase.rpc.return_value.execute.return_value.data = [{
        "total_revenue": 500,
        "total_sales": 5,
        "average_check": 100
    }]

    cache.clear()
    mock_supabase.reset_mock()

    # 1. Filtered request
    await get_dashboard(start_date=None, end_date=None, customer_id=None, agent_id=None, product_id=None, region="North", category=None, force_refresh=False)
    assert mock_supabase.rpc.call_count == 1

    # 2. Same filtered request
    await get_dashboard(start_date=None, end_date=None, customer_id=None, agent_id=None, product_id=None, region="North", category=None, force_refresh=False)

    # CURRENT BUG: It skips cache check if filters exist.
    # This assertion is expected to FAIL.
    assert mock_supabase.rpc.call_count == 1, "Filtered dashboard request did not hit cache!"

@pytest.mark.asyncio
async def test_top_customers_cache_collision(mock_supabase):
    """
    Test proving that top customers cache ignores filters (region), causing collisions.
    """
    # Setup mock for RPC
    # We want different results for different calls to prove collision

    # But since we mock the RPC globally, we need to inspect what arguments it was called with
    # or rely on the fact that if it was cached correctly, the second call wouldn't happen
    # or would return the cached result of the first call (which is wrong but shows collision)

    # Here we want to prove that:
    # 1. Call with Region A -> Caches result A
    # 2. Call with Region B -> Returns result A (Cache Hit on Wrong Key)

    mock_supabase.rpc.return_value.execute.return_value.data = [
        {"customer_id": "1", "customer_name": "Cust1", "total_revenue": 100}
    ]

    cache.clear()
    mock_supabase.reset_mock()

    # 1. Call with Region A
    res1 = await get_top_customers(region="North", force_refresh=True) # Force refresh to be sure we set it

    # 2. Call with Region B
    # We expect this to be a NEW computation (mock_supabase called again) or at least return different data if we could mock that.
    # But currently, it will HIT the cache of Region A because the key ignores region.

    # To demonstrate the bug:
    # If we force_refresh=False (default), it SHOULD query DB again for different region if logic was correct.

    mock_supabase.reset_mock()

    # Call with different region
    await get_top_customers(region="South")

    # CURRENT BUG: It uses same cache key "analytics:top_customers:10:7300", so it returns cached North data.
    # DB is NOT called.
    # Correct behavior: DB SHOULD be called.

    assert mock_supabase.rpc.call_count == 1, "Different region query incorrectly hit the cache!"
