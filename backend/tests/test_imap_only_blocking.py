import pytest
import asyncio
import time
from unittest.mock import MagicMock, patch
from app.routers.inbox import test_imap_only as target_function, EmailConfig
import sys
import os

# Ensure backend is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

@pytest.mark.asyncio
async def test_imap_only_blocking_behavior():
    """
    Test that verifies if test_imap_only blocks the event loop.
    """

    # Mock imaplib
    with patch("app.routers.inbox.imaplib.IMAP4_SSL") as mock_imap_cls:
        mock_imap = mock_imap_cls.return_value

        # Simulate slow connection/login
        def slow_login(*args, **kwargs):
            time.sleep(1.0) # Blocking sleep
            return "OK", [b"Logged in"]

        mock_imap.login.side_effect = slow_login
        mock_imap.select.return_value = ("OK", [b"10"])
        mock_imap.close.return_value = ("OK", [b"Closed"])
        mock_imap.logout.return_value = ("OK", [b"Logged out"])


        # Heartbeat task
        heartbeat_count = 0
        async def heartbeat():
            nonlocal heartbeat_count
            while True:
                heartbeat_count += 1
                await asyncio.sleep(0.1)

        # Start heartbeat
        task = asyncio.create_task(heartbeat())

        start_time = time.time()

        # Run test_imap_only
        config = EmailConfig(email="test@example.com", app_password="password")
        await target_function(config)

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

        # If blocking, heartbeat should NOT run during the sleep(1.0).
        # We expect this to FAIL (count < 2) before optimization.
        # After optimization, count should be ~10.

        # We verify that it is NOT blocking
        assert heartbeat_count > 5, f"Expected non-blocking behavior (high heartbeat count), but got {heartbeat_count}"
