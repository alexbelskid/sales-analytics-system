import pytest
import asyncio
import time
from unittest.mock import MagicMock, patch
from app.routers.inbox import sync_emails, EmailConfig
import sys

# Ensure backend is in path
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

@pytest.mark.asyncio
async def test_sync_emails_blocking_behavior():
    """
    Test that verifies if sync_emails blocks the event loop.
    """

    # Mock supabase
    mock_supabase = MagicMock()
    # Mock execute to simulate DB delay
    def slow_execute():
        time.sleep(0.5)
        return MagicMock(data=[])

    mock_supabase.table.return_value.select.return_value.execute.side_effect = slow_execute
    mock_supabase.table.return_value.insert.return_value.execute.side_effect = slow_execute

    # Mock imaplib
    with patch("app.routers.inbox.imaplib.IMAP4_SSL") as mock_imap_cls, \
         patch("app.routers.inbox.supabase", mock_supabase):

        mock_imap = mock_imap_cls.return_value

        # Simulate slow login
        def slow_login(*args, **kwargs):
            time.sleep(1.0)
            return "OK", [b"Logged in"]

        mock_imap.login.side_effect = slow_login

        # Mock search to return some email IDs
        mock_imap.search.return_value = ("OK", [b"1 2 3"])

        # Mock fetch to return some dummy email content
        mock_imap.fetch.return_value = ("OK", [(b"1 (RFC822 {100}", b"Subject: Test\r\n\r\nBody")])

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

        # Run sync_emails
        config = EmailConfig(email="test@example.com", app_password="password")
        await sync_emails(config)

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

        # Expected behavior for BLOCKING code:
        # The login takes 1.0s (blocking).
        # The heartbeat sleeps 0.1s.
        # If blocking, heartbeat should NOT run during the sleep(1.0).
        # So heartbeat_count should be very low (maybe 0 or 1 if it ran before blocking).
        # Expected count if NON-BLOCKING: duration / 0.1 ~= 10 to 15.

        # We fail if blocking was detected.
        # Allowing a small margin, but 1s blockage should result in < 2 heartbeats effectively if it blocks completely.
        # However, asyncio.sleep(1.0) is blocking in mock? No, time.sleep(1.0) is blocking.

        if heartbeat_count < 2:
            print("FAIL: Event loop was blocked!")
            assert True # We assert True here to confirm we reproduced it, but for the optimization step we want to see it fail or verify the behavior.
            # Actually, the plan says "Run this test to confirm failure".
            # So I should assert heartbeat_count > 5, which will fail now.
            assert heartbeat_count > 5, "Event loop was blocked! Heartbeat count too low."
        else:
            print("PASS: Event loop was NOT blocked.")
            # If it passes now, my assumption is wrong or the code is already async (unlikely).
