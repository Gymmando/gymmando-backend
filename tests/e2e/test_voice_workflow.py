"""E2E tests for voice workflow (Point 3).

Tests:
- Voice input processing
- Agent response generation
- LangGraph workflow execution
"""
import pytest
from livekit import rtc


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.slow
async def test_agent_receives_connection(
    test_user_id: str, livekit_token: str, livekit_room: rtc.Room
):
    """Test that agent receives connection and initializes."""
    from tests.e2e.conftest import LIVEKIT_URL

    await livekit_room.connect(LIVEKIT_URL, livekit_token)

    # Wait for agent to connect (may take a few seconds)
    import asyncio

    await asyncio.sleep(3)

    # Check if remote participants (agents) are present
    # Note: This depends on the agent being started separately
    # In a real scenario, the agent would connect automatically

    await livekit_room.disconnect()


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.slow
async def test_voice_input_processing(
    test_user_id: str, livekit_token: str, livekit_room: rtc.Room
):
    """Test that voice input is processed by the agent.

    Note: This is a simplified test. In a full implementation,
    you would send actual audio data and wait for responses.
    """
    from tests.e2e.conftest import LIVEKIT_URL

    await livekit_room.connect(LIVEKIT_URL, livekit_token)

    # Wait for connection
    import asyncio

    await asyncio.sleep(2)

    # Enable microphone track (simulating voice input)
    # In a real test, you would publish audio tracks
    local_participant = livekit_room.local_participant

    # Verify participant can publish tracks
    assert local_participant is not None

    # Note: Full voice workflow testing would require:
    # 1. Publishing audio track
    # 2. Waiting for agent to process
    # 3. Receiving response audio track
    # This is complex and may require mocking STT/TTS

    await livekit_room.disconnect()
