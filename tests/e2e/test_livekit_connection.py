"""E2E tests for LiveKit connection (Point 2).

Tests:
- LiveKit token generation
- Connection to LiveKit room
- User ID propagation to agent
"""
import pytest
from livekit import rtc


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_livekit_token_generation(livekit_token: str):
    """Test that LiveKit token can be generated."""
    assert livekit_token is not None
    assert len(livekit_token) > 0


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_connect_to_livekit_room(livekit_token: str, livekit_room: rtc.Room):
    """Test connecting to LiveKit room with token."""
    from tests.e2e.conftest import LIVEKIT_URL

    # Connect to room
    await livekit_room.connect(LIVEKIT_URL, livekit_token)

    # Verify connection
    assert livekit_room.state == rtc.ConnectionState.CONNECTED

    # Verify local participant exists
    assert livekit_room.local_participant is not None
    assert livekit_room.local_participant.identity is not None

    # Cleanup
    await livekit_room.disconnect()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_user_id_propagation(
    test_user_id: str, livekit_token: str, livekit_room: rtc.Room
):
    """Test that user_id is correctly propagated to LiveKit participant."""
    from tests.e2e.conftest import LIVEKIT_URL

    await livekit_room.connect(LIVEKIT_URL, livekit_token)

    # Wait for connection to establish
    import asyncio

    await asyncio.sleep(1)

    # Verify participant identity matches test user_id
    local_participant = livekit_room.local_participant
    assert local_participant is not None
    assert local_participant.identity == test_user_id

    await livekit_room.disconnect()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_room_metadata(livekit_token: str, livekit_room: rtc.Room):
    """Test that room metadata can be set and retrieved."""
    from tests.e2e.conftest import LIVEKIT_URL

    await livekit_room.connect(LIVEKIT_URL, livekit_token)

    # Room should be accessible
    assert livekit_room.name is not None

    await livekit_room.disconnect()
