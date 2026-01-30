import pytest
import sys
import os
from unittest.mock import MagicMock, patch
import imaplib
from email.message import Message

# Ensure backend is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.routers.inbox import _sync_emails_blocking, EmailConfig

def test_imap_batch_fetch_logic():
    """
    Simulates the logic of batch fetching to ensure we handle the list of tuples/bytes correctly.
    """
    # Mock data structure returned by imaplib.fetch for 2 emails
    # [ (msg1_header, msg1_body), b')', (msg2_header, msg2_body), b')' ]

    mock_response_data = [
        (b'1 (RFC822 {10}', b'Subject: Test 1\r\n\r\nBody 1'),
        b')',
        (b'2 (RFC822 {10}', b'Subject: Test 2\r\n\r\nBody 2'),
        b')'
    ]

    parsed_emails = []

    # Logic to be implemented in the main code:
    for response_part in mock_response_data:
        if isinstance(response_part, tuple):
            # It's a message
            msg_data = response_part
            # msg_data[1] is the body/content in bytes
            parsed_emails.append(msg_data[1])

    assert len(parsed_emails) == 2
    assert b'Subject: Test 1' in parsed_emails[0]
    assert b'Subject: Test 2' in parsed_emails[1]

@patch("app.routers.inbox.imaplib.IMAP4_SSL")
@patch("app.routers.inbox.supabase")
def test_sync_emails_blocking_batch_optimization(mock_supabase, mock_imap_cls):
    """
    Tests that _sync_emails_blocking uses batch fetch.
    """
    mock_imap = mock_imap_cls.return_value

    # Mock settings
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [{
        "id": "settings_1",
        "email": "test@example.com",
        "app_password": "pass",
        "imap_server": "imap.test",
        "imap_port": 993
    }]

    # Mock search to return 3 IDs
    mock_imap.search.return_value = ("OK", [b"1 2 3"])

    # Mock fetch to return batch response for 3 emails
    # Note: The code slices [-5:], so for 3 emails it takes all 3.
    mock_imap.fetch.return_value = ("OK", [
        (b'1 (RFC822 {10}', b'Subject: Test 1\r\n\r\nBody 1'),
        b')',
        (b'2 (RFC822 {10}', b'Subject: Test 2\r\n\r\nBody 2'),
        b')',
        (b'3 (RFC822 {10}', b'Subject: Test 3\r\n\r\nBody 3'),
        b')'
    ])

    # Run the function
    result = _sync_emails_blocking()

    # Verify fetch was called with comma separated IDs
    # Expected call: fetch(b"1,2,3", "(RFC822)")
    # Note: The implementation details might vary (e.g. bytes vs string for IDs).
    # The existing code used: email_ids = messages[0].split() -> [b'1', b'2', b'3']
    # If we join them with b",", we get b"1,2,3"

    mock_imap.fetch.assert_called_once()
    call_args = mock_imap.fetch.call_args
    # call_args[0] are positional args. [0] is message_set, [1] is message_parts

    # We expect the message set to be b"1,2,3" or "1,2,3" depending on implementation
    assert b"1,2,3" in call_args[0][0] or "1,2,3" in call_args[0][0]

    # Verify result
    assert result["new_emails_count"] == 3
