import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from app.routers import analytics
from app.models.sales import DashboardMetrics
from datetime import date

# Helper to verify to_thread usage
async def check_optimization(coro_func, *args, **kwargs):
    with patch("app.routers.analytics.supabase") as mock_supabase, \
         patch("app.routers.analytics.cache") as mock_cache, \
         patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:

        # Setup common mock returns
        mock_rpc_result = MagicMock()
        mock_rpc_result.data = [{"total_revenue": 1000, "total_sales": 50, "average_check": 20}]

        mock_table_result = MagicMock()
        mock_table_result.data = [{"id": "1", "name": "Test"}]

        # RPC chain
        mock_supabase.rpc.return_value.execute.return_value = mock_rpc_result
        # Table chain
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_table_result
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_table_result
        mock_supabase.table.return_value.select.return_value.gte.return_value.execute.return_value = mock_table_result
        mock_supabase.table.return_value.select.return_value.in_.return_value.execute.return_value = mock_table_result
        mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = mock_table_result

        # to_thread return (needs to return what the wrapped function would return)
        mock_to_thread.return_value = mock_rpc_result

        # Force cache miss
        mock_cache.get.return_value = None

        # Execute
        try:
            await coro_func(*args, **kwargs)
        except Exception as e:
            # If function fails (e.g. return type mismatch due to mock), we still check if to_thread was called
            # But specific errors like validation should be fixed by passing args
            print(f"Function raised: {e}")
            pass

        return mock_to_thread.called

@pytest.mark.asyncio
async def test_dashboard_uses_to_thread():
    # Pass explicit None to override Query(None) default
    used_thread = await check_optimization(
        analytics.get_dashboard,
        start_date=None, end_date=None, customer_id=None,
        agent_id=None, product_id=None, region=None, category=None,
        force_refresh=True
    )
    assert used_thread, "get_dashboard should use asyncio.to_thread"

@pytest.mark.asyncio
async def test_customers_uses_to_thread():
    used_thread = await check_optimization(analytics.get_customers)
    assert used_thread, "get_customers should use asyncio.to_thread"

@pytest.mark.asyncio
async def test_products_uses_to_thread():
    used_thread = await check_optimization(analytics.get_products)
    assert used_thread, "get_products should use asyncio.to_thread"

@pytest.mark.asyncio
async def test_agents_uses_to_thread():
    used_thread = await check_optimization(analytics.get_agents)
    assert used_thread, "get_agents should use asyncio.to_thread"
