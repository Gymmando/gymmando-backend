"""Pytest configuration and fixtures for E2E tests."""
import asyncio
import os
from typing import AsyncGenerator, cast

import pytest
from livekit import api, rtc

# Test configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "devsecret")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_user_id() -> str:
    """Generate a unique test user ID."""
    import uuid

    return f"test_user_{uuid.uuid4().hex[:8]}"


@pytest.fixture
async def livekit_token(test_user_id: str) -> str:
    """Generate a LiveKit access token for testing."""
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.with_identity(test_user_id)
    token.with_name("Test User")
    token.with_grants(api.VideoGrants(room_join=True, room="test-room"))
    return cast(str, token.to_jwt())


@pytest.fixture
async def livekit_room() -> AsyncGenerator[rtc.Room, None]:
    """Create a LiveKit room for testing."""
    room = rtc.Room()
    yield room
    await room.disconnect()


@pytest.fixture
async def livekit_participant(
    livekit_token: str, livekit_room: rtc.Room
) -> AsyncGenerator[rtc.RemoteParticipant | rtc.LocalParticipant, None]:
    """Connect to LiveKit room as a participant."""
    await livekit_room.connect(LIVEKIT_URL, livekit_token)

    # Wait a bit for connection to establish
    await asyncio.sleep(1)

    # Return the local participant
    yield livekit_room.local_participant

    await livekit_room.disconnect()


@pytest.fixture
async def api_client():
    """HTTP client for API requests."""
    import httpx

    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(autouse=True)
async def cleanup_test_data(test_user_id: str):
    """Clean up test data after each test."""
    yield
    # Add cleanup logic here if needed
    # For example, delete test workouts from database
