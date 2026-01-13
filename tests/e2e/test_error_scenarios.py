"""E2E tests for error scenarios (Point 5).

Tests:
- Invalid tokens
- Connection failures
- Error handling
"""
import pytest
from livekit import rtc


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_invalid_livekit_token(livekit_room: rtc.Room):
    """Test that invalid token is rejected."""
    from tests.e2e.conftest import LIVEKIT_URL

    invalid_token = "invalid_token_string"

    # Attempt to connect with invalid token
    with pytest.raises(Exception):  # Should raise connection error
        await livekit_room.connect(LIVEKIT_URL, invalid_token)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_expired_token_handling(livekit_room: rtc.Room):
    """Test handling of expired tokens.

    Note: Creating an actually expired token is complex,
    so this is a placeholder for the test structure.
    """

    # In a real scenario, you would:
    # 1. Create a token with past expiration
    # 2. Try to connect
    # 3. Verify proper error handling

    # For now, this is a placeholder


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_connection_timeout():
    """Test connection timeout handling."""

    room = rtc.Room()

    # Try to connect to non-existent server
    invalid_url = "ws://localhost:9999"

    with pytest.raises(Exception):  # Should timeout or fail
        await room.connect(invalid_url, "dummy_token", timeout=2.0)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_disconnect_handling(livekit_token: str, livekit_room: rtc.Room):
    """Test that disconnection is handled gracefully."""
    from tests.e2e.conftest import LIVEKIT_URL

    await livekit_room.connect(LIVEKIT_URL, livekit_token)

    # Verify connected
    assert livekit_room.state == rtc.ConnectionState.CONNECTED

    # Disconnect
    await livekit_room.disconnect()

    # Verify disconnected
    assert livekit_room.state == rtc.ConnectionState.DISCONNECTED
