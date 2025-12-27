# Gymmando 🏋️

A voice-based gym workout tracking assistant powered by AI.

## Architecture

**Master Graph Pattern:**
- Router Node (START) → Routes to specialized subgraphs
- Workout Subgraph → Handles workout logging
- Nutrition Subgraph → (Future) Meal tracking
- Measurements Subgraph → (Future) Body measurements

## Tech Stack

- **Backend:** FastAPI + LangGraph
- **AI:** Groq (Llama 3.1 8B + 70B)
- **Voice:** LiveKit (Deepgram STT + OpenAI TTS)
- **Database:** Supabase (PostgreSQL)
- **Auth:** Firebase Authentication

## Project Structure

```
gymmando/
├── core/                 # Shared utilities
├── graphs/              # Master graph + state
│   ├── master_graph.py
│   └── state.py
├── agents/              # Router agent
│   └── router/
├── modules/             # Feature modules
│   ├── workout/
│   │   ├── graph.py     # Workout subgraph
│   │   ├── state.py
│   │   ├── agents/
│   │   ├── prompts/
│   │   └── nodes/
│   ├── nutrition/
│   └── measurements/
├── database/            # Supabase client
├── api/                 # FastAPI routes
└── tests/              # Unit + integration tests
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Add your API keys to .env
   ```

3. **Setup database:**
   ```bash
   python scripts/setup_db.py
   ```

4. **Run API:**
   ```bash
   uvicorn gymmando.api.main:app --reload
   ```

## Development

- **Run tests:** `pytest`
- **Format code:** `black gymmando/`
- **Type check:** `mypy gymmando/`

## Features

### Current
- ✅ Voice workout logging
- ✅ Multi-agent system (router + workout)
- ✅ Intelligent data collection
- ✅ User-specific data isolation
- ✅ Firebase authentication

### Planned
- 🚧 Nutrition tracking
- 🚧 Body measurements
- 🚧 Workout history queries
- 🚧 Progress analytics

## Cost Optimization

- Groq LLM: **FREE** tier (14,400 req/day)
- Supabase: **FREE** tier (500MB)
- Target: Stay within free tiers for 100 test users

## License

MIT
