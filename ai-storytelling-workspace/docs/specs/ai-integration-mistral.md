# Spec: Mistral AI Integration for Storytelling Workflow

## Objective
Integrate real AI logic into the Celery workflow (`workflow_tasks.py`) to replace the current mocked `time.sleep()` delays. The application will use Mistral AI's models to dynamically generate story bibles, characters, outlines, and chapters. 

We are targeting the **Mistral API** using the `openai` Python SDK with Mistral's base URL (`https://api.mistral.ai/v1`) and the provided API key.

## Tech Stack
- **Python 3.10+**
- **Celery / Redis** for background task management
- **SQLAlchemy (Async)** for data persistence
- **OpenAI Python SDK (`openai>=1.0.0`)** targeting the Mistral Base URL

## Commands
```bash
# Update .env with the API key
echo "MISTRAL_API_KEY=jKtySGbasQPW7ZHhswS0i3NEz84RE9kv" >> .env

# Rebuild the Docker containers after modifying the Python code
docker-compose -f docker/docker-compose.yml up -d --build api worker

# View Celery Logs to verify LLM completion times
docker logs -f docker-worker-1
```

## Project Structure
```text
src/storytelling_workspace/
├── agents/             # AI agent logic (Intake, Concept, Worldbuilding, etc.)
│   ├── base.py         # Base LLM client wrapper (to be updated for Mistral)
│   ├── worldbuilding.py
│   └── ...
├── workers/
│   └── workflow_tasks.py # Celery logic where agents will be invoked
└── config.py           # Configuration for MISTRAL_API_KEY
```

## Code Style
We will use the `openai` SDK mapped to Mistral to request JSON-structured responses.
```python
from openai import AsyncOpenAI
import json

client = AsyncOpenAI(
    api_key=settings.MISTRAL_API_KEY,
    base_url="https://api.mistral.ai/v1"
)

async def generate_character(prompt: str) -> dict:
    response = await client.chat.completions.create(
        model=settings.MISTRAL_TEXT_MODEL, # e.g., mistral-large-latest
        messages=[
            {"role": "system", "content": "You are a character generator. Output JSON only."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)
```

## Testing Strategy
- **Unit Tests**: Mock the `AsyncOpenAI` client in `pytest` to prevent real API calls during CI runs.
- **Integration**: Run the workflow manually via the Angular UI and verify that real data appears in the Database (e.g., characters added to the `characters` table).

## Boundaries
- **Always**: Parse the JSON outputs safely using `try-except` blocks. If the LLM returns malformed JSON, handle the error gracefully without crashing the Celery worker.
- **Ask first**: Before making any drastic changes to the `workflow_states` database schema.
- **Never**: Block the asynchronous event loop with synchronous HTTP requests. We must use `AsyncOpenAI` or wrap it securely in `asyncio.run()` since Celery is synchronous.

## Success Criteria
- The Celery workflow successfully queries the Mistral API during the 4 phases.
- The `workflow_tasks.py` parses the LLM outputs and saves them to the MySQL database using the existing SQLAlchemy models.
- The workflow progress continues to broadcast successfully via Redis Pub/Sub.

## Open Questions
1. Do you want me to update the `.env` file locally with the key you provided?
2. Should we start by implementing **Phase 1 (Setup/Worldbuilding)** first and verify the results in the database before moving to Phase 2?
