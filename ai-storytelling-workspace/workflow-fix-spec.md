# Spec: Fix Workflow Execution Infinite Loop

## Objective
The AI Storytelling Workspace application currently gets stuck in an infinite loop during the "Setup" phase when executing a workflow. Activity logs remain empty, and the UI spins indefinitely. The objective is to identify all root causes across the backend (FastAPI, Celery, MySQL) and frontend (Angular, WebSocket) and implement a robust, fully working workflow execution pipeline that progresses through phases and updates the UI in real-time.

## Tech Stack
- **Backend:** FastAPI (Python 3.10), SQLAlchemy, Celery, Redis
- **Database:** MySQL 8.0, Alembic for migrations
- **Frontend:** Angular 17/18, RxJS, WebSockets
- **Infrastructure:** Docker Compose

## Commands
- Build/Restart Backend: `docker-compose -f docker/docker-compose.yml up -d --build api worker`
- Apply DB Migrations: `docker exec -i docker-api-1 alembic upgrade head`
- View API Logs: `docker logs -f docker-api-1`
- View Worker Logs: `docker logs -f docker-worker-1`

## Project Structure
- `src/storytelling_workspace/api/` -> FastAPI backend endpoints and WebSockets
- `src/storytelling_workspace/workers/` -> Celery background tasks orchestrating the workflow
- `src/storytelling_workspace/db/` -> SQLAlchemy models and DB session logic
- `web/src/app/` -> Angular frontend components and services

## Code Style
- **Python:** Use strong typing (`async def get_state(project_id: str) -> WorkflowState:`), proper dependency injection (e.g., `worker_session`), and explicitly catch and log exceptions to prevent silent failures in background tasks.
- **Angular:** Use functional RxJS streams, strong types for WebSocket payloads, and handle fallback states (like polling if WebSocket fails).

## Testing Strategy
- **Manual End-to-End Validation:** Create a test project, trigger the workflow, and verify that the UI progresses past "Setup" to the next phases without looping.
- **Log Verification:** Ensure `agent_deltas` and activity logs are successfully saved to the database and emitted over WebSockets.

## Boundaries
- **Always:** Use `worker_session` (which creates a fresh AsyncEngine) inside Celery tasks to avoid `Future attached to a different loop` errors. Ensure all DB columns match SQLAlchemy models.
- **Ask first:** Before completely dropping or migrating production data. 
- **Never:** Swallow exceptions in Celery tasks without logging them or emitting an error state to the UI.

## Success Criteria
- [ ] User can click "Start Workflow" and the system transitions from "Setup" -> "World Building" -> etc.
- [ ] Activity logs populate in the UI in real-time as background tasks complete.
- [ ] If an error occurs (e.g. LLM failure or DB issue), the workflow status changes to `FAILED` and displays an error message on the frontend, rather than spinning forever.
- [ ] The `workflow_states`, `projects`, and `agent_deltas` database tables correctly match the SQLAlchemy models without crashing.

## Open Questions
1. Is it acceptable to wipe the current local development database and re-run Alembic migrations from scratch to ensure the schema matches exactly?
