import pytest
import asyncio
import time
from unittest.mock import MagicMock, patch
from app.routers.analytics import get_dashboard, DashboardMetrics
import sys
import os

# Ensure backend is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

@pytest.mark.asyncio
async def test_get_dashboard_blocking_behavior():
    """
    Test that verifies if get_dashboard blocks the event loop.
    """

    # Mock supabase to simulate slow blocking I/O
    mock_supabase = MagicMock()

    def slow_execute():
        time.sleep(0.5)  # Simulate blocking I/O
        return MagicMock(data=[{
            "total_revenue": 1000,
            "total_sales": 10,
            "average_check": 100
        }])

    # Mock the chain: supabase.rpc(...).execute()
    mock_supabase.rpc.return_value.execute.side_effect = slow_execute

    # Mock the fallback chain: supabase.table(...).select(...).eq(...).execute()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = slow_execute

    # Mock cache to return None so we hit the database
    mock_cache = MagicMock()
    mock_cache.get.return_value = None

    # Patch dependencies
    # We need to patch where they are used in app.routers.analytics
    with patch("app.routers.analytics.supabase", mock_supabase), \
         patch("app.routers.analytics.cache", mock_cache):

        # Heartbeat task to measure event loop responsiveness
        heartbeat_count = 0
        async def heartbeat():
            nonlocal heartbeat_count
            while True:
                heartbeat_count += 1
                await asyncio.sleep(0.1)

        # Start heartbeat
        task = asyncio.create_task(heartbeat())

        start_time = time.time()

        # Call the endpoint function directly
        # We need to pass required parameters.
        # Optional params are None by default, but FastAPI injects them.
        # When calling directly, we can just pass defaults or named args.
        try:
            await get_dashboard(
                start_date=None,
                end_date=None,
                customer_id=None,
                agent_id=None,
                product_id=None,
                region=None,
                category=None,
                force_refresh=True
            )
        except Exception as e:
            print(f"Exception during test: {e}")

        end_time = time.time()

        # Cancel heartbeat
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        duration = end_time - start_time
        print(f"Duration: {duration:.2f}s")
        print(f"Heartbeat count: {heartbeat_count}")

        # If blocking: time.sleep(0.5) blocks everything. Heartbeat won't run. Count ~ 0 or 1.
        # If non-blocking: asyncio.to_thread runs sleep in thread. Heartbeat runs every 0.1s. Count ~ 5.

        # This assertion is expected to FAIL before optimization
        if heartbeat_count < 3:
             pytest.fail(f"Event loop was blocked! Heartbeat count: {heartbeat_count} (expected > 3)")
