# Spec: Workflow Database Updates and WebSocket Broadcasting

## Objective
Implement the missing logic in the Celery background worker tasks to persist workflow execution state to the database and broadcast real-time progress updates to connected WebSocket clients via Redis Pub/Sub.

## Tech Stack
- FastAPI (WebSocket Manager)
- Celery (Background Worker)
- SQLAlchemy (AsyncSession for DB updates)
- Redis (Pub/Sub for IPC between Celery and FastAPI)
- asyncio (Running async DB and Redis calls within sync Celery tasks)

## Commands
- Test worker logic: `docker-compose -f docker/docker-compose.yml restart worker api`
- View worker logs: `docker logs -f docker-worker-1`

## Project Structure
- `src/storytelling_workspace/workers/workflow_tasks.py` -> Update `# TODO`s with actual implementation.
- `src/storytelling_workspace/api/websocket/manager.py` -> Add a background task to listen to Redis Pub/Sub and broadcast to clients.
- `src/storytelling_workspace/db/repositories/workflow_state.py` -> Ensure CRUD operations are used for `update`.

## Code Style
```python
# Wrap async calls inside Celery tasks using asyncio.run
import asyncio

@celery_app.task(name="workflow.update_progress")
def update_workflow_progress(workflow_id: str, current_step: int, total_steps: int, phase: str, message: str):
    async def _update():
        # Update Database
        async with get_session_factory()() as session:
            repo = WorkflowStateRepository(session)
            await repo.update(workflow_id, progress_percentage=(current_step/total_steps)*100, current_phase=phase)
            await session.commit()
            
        # Broadcast via Redis
        redis = aioredis.from_url(settings.redis_url)
        payload = json.dumps({"workflow_id": workflow_id, "phase": phase, "message": message})
        await redis.publish("workflow_updates", payload)

    asyncio.run(_update())
```

## Testing Strategy
1. **Database Persistence**: Ensure `GET /api/workflow/{id}/status` correctly reflects the `progress_percentage` and `status` when polled.
2. **Real-time WebSockets**: Ensure the Angular UI instantly updates its progress bar and activity logs when a phase completes without polling.

## Boundaries
- Always: Wrap async DB operations in `asyncio.run()` when called from Celery. Use `get_session_factory()` correctly.
- Ask first: Restructuring the WebSocket manager entirely.
- Never: Call blocking sync functions inside async WebSocket code in FastAPI.

## Success Criteria
- The "Waiting for workflow to start..." message in the frontend is replaced by actual logs.
- The progress bar completes 15/15 steps.
- The status changes from "Running" to "Completed" automatically on the frontend.

## Open Questions
- None. Proceeding with implementation if approved.
