# E2E Tests for Gymmando

End-to-end tests for the complete Gymmando workflow, from LiveKit connection to database operations.

## Overview

These tests verify the complete user flow:
1. **LiveKit Connection** - Token generation and room connection
2. **Voice Workflow** - Agent processing and response generation
3. **Workout Logging** - Complete workout save workflow
4. **Error Scenarios** - Error handling and edge cases

## Prerequisites

- Docker and Docker Compose installed
- Python 3.10+ with dependencies installed
- Environment variables configured (see `.env.example`)

## Setup

### 1. Start Docker Compose Services

Start the local test environment:

```bash
docker-compose -f docker-compose.e2e.yml up -d
```

This starts:
- LiveKit server (port 7880)
- PostgreSQL test database (port 5433)
- FastAPI API service (port 8000)

### 2. Verify Services are Running

```bash
# Check services
docker-compose -f docker-compose.e2e.yml ps

# Check logs
docker-compose -f docker-compose.e2e.yml logs -f
```

### 3. Set Environment Variables

Create a `.env` file in the project root with:

```bash
# LiveKit (uses dev credentials from docker-compose)
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=devsecret

# API
API_BASE_URL=http://localhost:8000

# Optional: For full integration testing
OPENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here
```

## Running Tests

### Run All E2E Tests

```bash
# Make sure Docker Compose is running first
pytest tests/e2e/ -m e2e -v
```

### Run Specific Test File

```bash
pytest tests/e2e/test_livekit_connection.py -m e2e -v
pytest tests/e2e/test_voice_workflow.py -m e2e -v
pytest tests/e2e/test_workout_e2e.py -m e2e -v
pytest tests/e2e/test_error_scenarios.py -m e2e -v
```

### Run with Coverage

```bash
pytest tests/e2e/ -m e2e --cov=gymmando_graph --cov=gymmando_api
```

## Test Structure

```
tests/e2e/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_livekit_connection.py  # Point 2: Connection tests
├── test_voice_workflow.py      # Point 3: Voice processing
├── test_workout_e2e.py        # Point 4: Complete workflow
└── test_error_scenarios.py    # Point 5: Error handling
```

## Important Notes

### E2E Tests are Excluded from Pre-commit

E2E tests are **NOT** run automatically in pre-commit hooks. They require:
- Docker Compose services to be running
- Longer execution time
- External dependencies

To run E2E tests, you must explicitly use:
```bash
pytest tests/e2e/ -m e2e
```

### Test Markers

- `@pytest.mark.e2e` - Marks test as E2E (excluded by default)
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.asyncio` - Async tests

### Running in CI/CD

For CI/CD pipelines, you would:
1. Start Docker Compose services
2. Wait for health checks
3. Run E2E tests
4. Clean up services

Example GitHub Actions:
```yaml
- name: Start services
  run: docker-compose -f docker-compose.e2e.yml up -d
  
- name: Wait for services
  run: |
    timeout 60 bash -c 'until curl -f http://localhost:8000/token; do sleep 2; done'
  
- name: Run E2E tests
  run: pytest tests/e2e/ -m e2e
```

## Troubleshooting

### Services Not Starting

```bash
# Check Docker is running
docker ps

# Check logs
docker-compose -f docker-compose.e2e.yml logs

# Restart services
docker-compose -f docker-compose.e2e.yml restart
```

### Connection Errors

- Verify LiveKit is accessible: `curl http://localhost:7880/`
- Verify API is accessible: `curl http://localhost:8000/token?user_id=test`
- Check firewall/port conflicts

### Test Timeouts

Some tests may need longer timeouts. Adjust in `conftest.py` or use:
```bash
pytest tests/e2e/ -m e2e --timeout=60
```

## Cleanup

Stop and remove services:

```bash
docker-compose -f docker-compose.e2e.yml down

# Remove volumes (cleans test data)
docker-compose -f docker-compose.e2e.yml down -v
```
