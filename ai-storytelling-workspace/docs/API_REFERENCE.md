# API Reference

The AI Storytelling Workspace exposes a RESTful API built with FastAPI. Interactive Swagger documentation is available at `/docs` when running the server.

## Base URL
`http://localhost:8000/api/v1`

## Authentication
*(Currently relies on local network boundaries. JWT authentication planned for production public endpoints)*

## Endpoints

### Projects
Manage storytelling projects.

- `GET /projects`: List all projects (paginated).
- `POST /projects`: Create a new project.
- `GET /projects/{id}`: Retrieve a specific project.
- `PUT /projects/{id}`: Update project details.
- `DELETE /projects/{id}`: Soft delete a project.

### Workflows
Control the execution of the agent orchestration pipeline.

- `GET /workflows/{project_id}`: Get the current workflow status.
- `POST /workflows/{project_id}/start`: Initialize and start a generation workflow.
- `POST /workflows/{project_id}/pause`: Pause an active workflow.
- `POST /workflows/{project_id}/resume`: Resume a paused workflow.

### Story Bible
Manage the lore, characters, and settings.

- `GET /story-bible/{project_id}`: Retrieve the full story bible.
- `PUT /story-bible/{project_id}`: Update specific elements of the story bible.

### Checkpoints
Human-in-the-loop validation gates.

- `GET /checkpoints/{project_id}`: List pending checkpoints requiring human approval.
- `POST /checkpoints/{checkpoint_id}/approve`: Approve a checkpoint and continue workflow.
- `POST /checkpoints/{checkpoint_id}/reject`: Reject a checkpoint with feedback for regeneration.

### Images
Manage generated visual assets.

- `GET /images/{project_id}`: List all images associated with a project.
- `POST /images/generate`: Manually trigger image generation for a specific prompt/scene.
- `GET /images/download/{image_id}`: Download the image file.

## WebSockets
Real-time progress updates are pushed via WebSockets.

- `WS /ws/projects/{project_id}`
  - **Events Emitted**: `workflow_progress`, `agent_status`, `error`, `checkpoint_reached`.
  - **Message Format**: JSON encoded strings containing event type and payload.

## Error Handling
Standard HTTP status codes are used:
- `400 Bad Request`: Validation errors (Pydantic schemas).
- `404 Not Found`: Resource does not exist.
- `422 Unprocessable Entity`: Semantic errors in payload.
- `500 Internal Server Error`: Server or AI Provider failures.

All error responses follow the format:
```json
{
  "detail": "Error description message"
}
```
