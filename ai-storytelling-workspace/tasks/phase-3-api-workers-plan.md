# Phase 3: API & Workers - Detailed Implementation Plan

## Overview

Transform the CLI-based orchestrator into a production-ready API with async workers and real-time updates. This phase bridges the database layer (Phase 2) with the web UI (Phase 4).

**Duration:** Week 3-4 (2 weeks)  
**Tasks:** 10-15 (6 tasks)  
**Estimated Effort:** 60-80 hours  
**Dependencies:** Phase 2 complete (database, repositories, models)

---

## Architecture Design

### System Components

```
┌─────────────┐     HTTP/WS      ┌──────────────┐
│   Next.js   │ ◄──────────────► │   FastAPI    │
│   Web UI    │                  │   API Server │
└─────────────┘                  └──────┬───────┘
                                        │
                                        │ Redis
                                        │ (broker)
                                        │
                                 ┌──────▼───────┐
                                 │    Celery    │
                                 │   Workers    │
                                 └──────┬───────┘
                                        │
                                        │
                                 ┌──────▼───────┐
                                 │    MySQL     │
                                 │   Database   │
                                 └──────────────┘
```

### Communication Patterns

1. **Synchronous (REST API)**
   - CRUD operations on projects, checkpoints, images
   - Quick queries (status, metadata)
   - Response time: <200ms p95

2. **Asynchronous (Celery Tasks)**
   - Long-running workflows (5-45 minutes)
   - Agent executions (1-5 minutes each)
   - Image generation (10-30 seconds)
   - Background processing

3. **Real-time (WebSocket)**
   - Workflow progress updates
   - Agent status changes
   - Checkpoint notifications
   - Error alerts

---

## Task 10: FastAPI Application Structure

### Objectives

Create a production-ready FastAPI application with proper middleware, error handling, and database integration.

### File Structure

```
src/storytelling_workspace/api/
├── __init__.py
├── main.py                    # FastAPI app + middleware
├── dependencies.py            # Dependency injection
├── middleware.py              # Custom middleware
├── exceptions.py              # Custom exceptions
├── routes/
│   ├── __init__.py
│   ├── projects.py           # Project CRUD
│   ├── workflow.py           # Workflow control
│   ├── checkpoints.py        # Checkpoint management
│   ├── images.py             # Image retrieval
│   └── story_bible.py        # Story Bible access
├── schemas/                   # Pydantic models (Task 11)
└── websocket/                 # WebSocket handlers (Task 15)
```

### Implementation Details

#### 1. Main Application (`main.py`)

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from .routes import projects, workflow, checkpoints, images, story_bible
from .middleware import LoggingMiddleware, ErrorHandlerMiddleware
from .exceptions import APIException
from ..db.session import init_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Storytelling Workspace API",
    description="Production API for AI-powered novel generation",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Middleware stack (order matters!)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Startup/shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool."""
    logger.info("Starting API server...")
    await init_db()
    logger.info("Database connection pool initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections."""
    logger.info("Shutting down API server...")
    await close_db()
    logger.info("Database connections closed")

# Exception handlers
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """Handle custom API exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "details": exc.details}
    )

# Health check
@app.get("/health")
async def health_check():
    """Health check for Docker/K8s."""
    return {
        "status": "healthy",
        "service": "ai-storytelling-workspace-api",
        "version": "2.0.0"
    }

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(workflow.router, prefix="/api/workflow", tags=["Workflow"])
app.include_router(checkpoints.router, prefix="/api/checkpoints", tags=["Checkpoints"])
app.include_router(images.router, prefix="/api/images", tags=["Images"])
app.include_router(story_bible.router, prefix="/api/story-bible", tags=["Story Bible"])
```

#### 2. Dependencies (`dependencies.py`)

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from ..db.session import get_db_session
from ..db.repositories import (
    ProjectRepository,
    StoryBibleRepository,
    CheckpointRepository,
    ImageRepository,
    WorkflowStateRepository
)

# Database session dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async for session in get_db_session():
        yield session

# Repository dependencies
async def get_project_repo(db: AsyncSession = Depends(get_db)) -> ProjectRepository:
    """Get project repository."""
    return ProjectRepository(db)

async def get_story_bible_repo(db: AsyncSession = Depends(get_db)) -> StoryBibleRepository:
    """Get story bible repository."""
    return StoryBibleRepository(db)

async def get_checkpoint_repo(db: AsyncSession = Depends(get_db)) -> CheckpointRepository:
    """Get checkpoint repository."""
    return CheckpointRepository(db)

async def get_image_repo(db: AsyncSession = Depends(get_db)) -> ImageRepository:
    """Get image repository."""
    return ImageRepository(db)

async def get_workflow_repo(db: AsyncSession = Depends(get_db)) -> WorkflowStateRepository:
    """Get workflow state repository."""
    return WorkflowStateRepository(db)
```

#### 3. Middleware (`middleware.py`)

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import traceback

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} "
            f"({duration*1000:.2f}ms) "
            f"{request.method} {request.url.path}"
        )
        
        return response

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catch and log all unhandled exceptions."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}")
            logger.error(traceback.format_exc())
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": str(e)
                }
            )
```

#### 4. Custom Exceptions (`exceptions.py`)

```python
from fastapi import HTTPException

class APIException(HTTPException):
    """Base API exception."""
    
    def __init__(self, status_code: int, message: str, details: dict = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message)

class ProjectNotFoundException(APIException):
    """Project not found."""
    def __init__(self, project_id: str):
        super().__init__(
            status_code=404,
            message=f"Project not found: {project_id}"
        )

class WorkflowAlreadyRunningException(APIException):
    """Workflow already running."""
    def __init__(self, project_id: str):
        super().__init__(
            status_code=409,
            message=f"Workflow already running for project: {project_id}"
        )

class CheckpointNotFoundException(APIException):
    """Checkpoint not found."""
    def __init__(self, checkpoint_id: str):
        super().__init__(
            status_code=404,
            message=f"Checkpoint not found: {checkpoint_id}"
        )
```

### Acceptance Criteria

- [x] FastAPI app structure created
- [ ] Middleware configured (CORS, logging, error handling)
- [ ] Database connection pool initialized
- [ ] Health check endpoint works
- [ ] Structured JSON logging operational
- [ ] API documentation accessible at /api/docs
- [ ] All imports resolve correctly

### Testing Strategy

```python
# tests/integration/test_api/test_main.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    """Test CORS headers are set."""
    response = await client.options("/api/projects")
    assert "access-control-allow-origin" in response.headers

@pytest.mark.asyncio
async def test_api_docs_accessible(client: AsyncClient):
    """Test API documentation is accessible."""
    response = await client.get("/api/docs")
    assert response.status_code == 200
```

---

## Task 11: Pydantic Schemas

### Objectives

Define all request/response models with validation rules for type safety and API documentation.

### Schema Categories

1. **Project Schemas** - CRUD operations
2. **Workflow Schemas** - Execution control
3. **Checkpoint Schemas** - Review/approval
4. **Story Bible Schemas** - Content access
5. **Image Schemas** - Metadata retrieval

### Implementation Details

#### 1. Project Schemas (`schemas/project.py`)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID

# Request schemas
class ProjectCreate(BaseModel):
    """Create new project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    genre: Optional[str] = Field(None, max_length=100)
    target_length: int = Field(80000, ge=10000, le=200000)
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class ProjectUpdate(BaseModel):
    """Update existing project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    genre: Optional[str] = None
    target_length: Optional[int] = Field(None, ge=10000, le=200000)
    status: Optional[Literal['draft', 'in_progress', 'paused', 'completed', 'archived']] = None

# Response schemas
class ProjectResponse(BaseModel):
    """Project response."""
    id: UUID
    name: str
    description: Optional[str]
    genre: Optional[str]
    target_length: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    """List of projects."""
    projects: list[ProjectResponse]
    total: int
    page: int
    page_size: int
```

#### 2. Workflow Schemas (`schemas/workflow.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID

class WorkflowStartRequest(BaseModel):
    """Start workflow execution."""
    resume_from_checkpoint: Optional[str] = None

class WorkflowPauseRequest(BaseModel):
    """Pause workflow execution."""
    reason: Optional[str] = None

class WorkflowStatusResponse(BaseModel):
    """Workflow status."""
    id: UUID
    project_id: UUID
    status: Literal['running', 'paused', 'completed', 'failed', 'cancelled']
    current_phase: str
    current_agent: Optional[str]
    progress_percentage: float
    completed_steps: int
    total_steps: int
    started_at: datetime
    paused_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True

class WorkflowProgressUpdate(BaseModel):
    """Real-time progress update (WebSocket)."""
    project_id: UUID
    workflow_id: UUID
    phase: str
    agent: str
    progress: float
    message: str
    timestamp: datetime
```

#### 3. Checkpoint Schemas (`schemas/checkpoint.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal, Any
from datetime import datetime
from uuid import UUID

class CheckpointResponse(BaseModel):
    """Checkpoint response."""
    id: UUID
    project_id: UUID
    checkpoint_type: Literal['concept', 'characters', 'outline', 'chapter', 'final']
    phase: str
    agent_name: str
    status: Literal['pending', 'approved', 'rejected', 'skipped']
    content: dict[str, Any]
    changes: Optional[dict[str, Any]]
    user_feedback: Optional[str]
    rejection_reason: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class CheckpointApprovalRequest(BaseModel):
    """Approve checkpoint."""
    feedback: Optional[str] = None

class CheckpointRejectionRequest(BaseModel):
    """Reject checkpoint."""
    reason: str = Field(..., min_length=1)
    feedback: Optional[str] = None
```

#### 4. Story Bible Schemas (`schemas/story_bible.py`)

```python
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from uuid import UUID

class StoryBibleResponse(BaseModel):
    """Story Bible response."""
    id: UUID
    project_id: UUID
    version: int
    brief: Optional[dict[str, Any]]
    concept: Optional[dict[str, Any]]
    world_rules: Optional[dict[str, Any]]
    characters: Optional[dict[str, Any]]
    locations: Optional[dict[str, Any]]
    timeline: Optional[dict[str, Any]]
    plot_threads: Optional[dict[str, Any]]
    terminology: Optional[dict[str, Any]]
    style_guide: Optional[dict[str, Any]]
    metadata: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CharacterResponse(BaseModel):
    """Individual character from Story Bible."""
    name: str
    role: str
    traits: list[str]
    arc: str
    voice_signature: str
```

#### 5. Image Schemas (`schemas/image.py`)

```python
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID

class ImageResponse(BaseModel):
    """Image metadata response."""
    id: UUID
    project_id: UUID
    image_type: Literal['cover_art', 'character_portrait', 'scene_illustration']
    file_path: str
    file_size: int
    prompt: str
    model: str
    provider: str
    width: int
    height: int
    format: str
    character_name: Optional[str]
    chapter_number: Optional[int]
    generation_cost: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class ImageListResponse(BaseModel):
    """List of images."""
    images: list[ImageResponse]
    total: int
```

### Acceptance Criteria

- [ ] All schemas defined with proper types
- [ ] Validation rules enforce constraints
- [ ] Request/response models separated
- [ ] OpenAPI schema generated correctly
- [ ] Schema tests pass

### Testing Strategy

```python
# tests/unit/test_api/test_schemas/test_project.py
import pytest
from pydantic import ValidationError
from storytelling_workspace.api.schemas.project import ProjectCreate

def test_project_create_valid():
    """Test valid project creation."""
    data = {
        "name": "My Novel",
        "description": "A great story",
        "genre": "Fantasy",
        "target_length": 80000
    }
    project = ProjectCreate(**data)
    assert project.name == "My Novel"

def test_project_create_invalid_length():
    """Test invalid target length."""
    with pytest.raises(ValidationError):
        ProjectCreate(name="Test", target_length=5000)  # Too short

def test_project_create_empty_name():
    """Test empty name validation."""
    with pytest.raises(ValidationError):
        ProjectCreate(name="   ")  # Whitespace only
```

---

## Task 12: Project Management Endpoints

### Objectives

Implement full CRUD operations for projects with proper error handling and validation.

### Endpoints

```
POST   /api/projects              - Create project
GET    /api/projects              - List projects (paginated)
GET    /api/projects/{id}         - Get project details
PUT    /api/projects/{id}         - Update project
DELETE /api/projects/{id}         - Delete project (soft delete)
GET    /api/projects/{id}/stats   - Get project statistics
```

### Implementation (`routes/projects.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import Optional

from ..schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse
)
from ..dependencies import get_project_repo
from ..exceptions import ProjectNotFoundException
from ...db.repositories import ProjectRepository

router = APIRouter()

@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project: ProjectCreate,
    repo: ProjectRepository = Depends(get_project_repo)
):
    """Create a new project."""
    db_project = await repo.create(project.dict())
    return ProjectResponse.from_orm(db_project)

@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    repo: ProjectRepository = Depends(get_project_repo)
):
    """List all projects with pagination."""
    filters = {"status": status} if status else {}
    projects = await repo.list(
        skip=(page - 1) * page_size,
        limit=page_size,
        filters=filters
    )
    total = await repo.count(filters=filters)
    
    return ProjectListResponse(
        projects=[ProjectResponse.from_orm(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    repo: ProjectRepository = Depends(get_project_repo)
):
    """Get project by ID."""
    project = await repo.get(str(project_id))
    if not project:
        raise ProjectNotFoundException(str(project_id))
    return ProjectResponse.from_orm(project)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    updates: ProjectUpdate,
    repo: ProjectRepository = Depends(get_project_repo)
):
    """Update project."""
    project = await repo.get(str(project_id))
    if not project:
        raise ProjectNotFoundException(str(project_id))
    
    updated = await repo.update(
        str(project_id),
        updates.dict(exclude_unset=True)
    )
    return ProjectResponse.from_orm(updated)

@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    repo: ProjectRepository = Depends(get_project_repo)
):
    """Delete project (soft delete)."""
    project = await repo.get(str(project_id))
    if not project:
        raise ProjectNotFoundException(str(project_id))
    
    await repo.delete(str(project_id))
    return None
```

### Service Layer (`services/project_service.py`)

```python
from typing import Optional
from uuid import UUID

from ..db.repositories import ProjectRepository, StoryBibleRepository
from ..db.models import Project

class ProjectService:
    """Business logic for project management."""
    
    def __init__(
        self,
        project_repo: ProjectRepository,
        story_bible_repo: StoryBibleRepository
    ):
        self.project_repo = project_repo
        self.story_bible_repo = story_bible_repo
    
    async def create_project_with_bible(self, project_data: dict) -> Project:
        """Create project and initialize Story Bible."""
        # Create project
        project = await self.project_repo.create(project_data)
        
        # Initialize Story Bible
        bible_data = {
            "project_id": project.id,
            "version": 1,
            "brief": {},
            "concept": {},
            "characters": {},
            "world_rules": {},
            "locations": {},
            "timeline": {},
            "plot_threads": {},
            "terminology": {},
            "style_guide": {},
            "metadata": {}
        }
        await self.story_bible_repo.create(bible_data)
        
        return project
    
    async def get_project_stats(self, project_id: str) -> dict:
        """Get project statistics."""
        project = await self.project_repo.get(project_id)
        if not project:
            return None
        
        # Get related data counts
        bible = await self.story_bible_repo.get_latest_by_project(project_id)
        
        return {
            "project_id": project_id,
            "status": project.status,
            "word_count": 0,  # TODO: Calculate from chapters
            "chapter_count": 0,  # TODO: Count chapters
            "image_count": 0,  # TODO: Count images
            "checkpoint_count": 0,  # TODO: Count checkpoints
            "bible_version": bible.version if bible else 0
        }
```

### Acceptance Criteria

- [ ] All CRUD endpoints work
- [ ] Proper HTTP status codes returned
- [ ] Validation errors handled
- [ ] Database operations successful
- [ ] Soft delete implemented
- [ ] Tests pass

---

## Task 13: Workflow Execution Endpoints

### Objectives

Implement workflow control endpoints that dispatch Celery tasks for async execution.

### Endpoints

```
POST   /api/workflow/{project_id}/start   - Start workflow
POST   /api/workflow/{project_id}/pause   - Pause workflow
POST   /api/workflow/{project_id}/resume  - Resume workflow
GET    /api/workflow/{project_id}/status  - Get workflow status
POST   /api/workflow/{project_id}/cancel  - Cancel workflow
```

### Implementation (`routes/workflow.py`)

```python
from fastapi import APIRouter, Depends, BackgroundTasks
from uuid import UUID

from ..schemas.workflow import (
    WorkflowStartRequest,
    WorkflowPauseRequest,
    WorkflowStatusResponse
)
from ..dependencies import get_workflow_repo, get_project_repo
from ..exceptions import ProjectNotFoundException, WorkflowAlreadyRunningException
from ...workers.workflow_tasks import start_workflow_task
from ...db.repositories import WorkflowStateRepository, ProjectRepository

router = APIRouter()

@router.post("/{project_id}/start", response_model=WorkflowStatusResponse)
async def start_workflow(
    project_id: UUID,
    request: WorkflowStartRequest,
    project_repo: ProjectRepository = Depends(get_project_repo),
    workflow_repo: WorkflowStateRepository = Depends(get_workflow_repo)
):
    """Start workflow execution."""
    # Verify project exists
    project = await project_repo.get(str(project_id))
    if not project:
        raise ProjectNotFoundException(str(project_id))
    
    # Check if workflow already running
    existing = await workflow_repo.get_active_by_project(str(project_id))
    if existing:
        raise WorkflowAlreadyRunningException(str(project_id))
    
    # Create workflow state
    workflow_state = await workflow_repo.create({
        "project_id": str(project_id),
        "current_phase": "setup",
        "status": "running",
        "total_steps": 15,
        "completed_steps": 0,
        "progress_percentage": 0.0
    })
    
    # Dispatch Celery task
    task = start_workflow_task.delay(
        project_id=str(project_id),
        workflow_id=str(workflow_state.id),
        resume_from=request.resume_from_checkpoint
    )
    
    # Update workflow with task ID
    await workflow_repo.update(str(workflow_state.id), {
        "state_data": {"celery_task_id": task.id}
    })
    
    return WorkflowStatusResponse.from_orm(workflow_state)

@router.post("/{project_id}/pause", response_model=WorkflowStatusResponse)
async def pause_workflow(
    project_id: UUID,
    request: WorkflowPauseRequest,
    workflow_repo: WorkflowStateRepository = Depends(get_workflow_repo)
):
    """Pause workflow execution."""
    workflow = await workflow_repo.get_active_by_project(str(project_id))
    if not workflow:
        raise HTTPException(404, "No active workflow found")
    
    # Update status
    updated = await workflow_repo.update(str(workflow.id), {
        "status": "paused",
        "paused_at": datetime.utcnow()
    })
    
    # TODO: Signal Celery task to pause
    
    return WorkflowStatusResponse.from_orm(updated)

@router.get("/{project_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    project_id: UUID,
    workflow_repo: WorkflowStateRepository = Depends(get_workflow_repo)
):
    """Get current workflow status."""
    workflow = await workflow_repo.get_latest_by_project(str(project_id))
    if not workflow:
        raise HTTPException(404, "No workflow found")
    
    return WorkflowStatusResponse.from_orm(workflow)
```

### Acceptance Criteria

- [ ] Can start workflow via API
- [ ] Can pause/resume workflow
- [ ] Status endpoint returns current state
- [ ] Workflow state persisted to database
- [ ] Celery tasks dispatched correctly
- [ ] Tests pass

---

## Task 14: Celery Workers

### Objectives

Set up Celery for async task processing with proper error handling and progress tracking.

### File Structure

```
src/storytelling_workspace/workers/
├── __init__.py
├── celery_app.py          # Celery configuration
├── workflow_tasks.py      # Workflow orchestration tasks
├── agent_tasks.py         # Individual agent tasks
└── image_tasks.py         # Image generation tasks
```

### Implementation

#### 1. Celery App (`celery_app.py`)

```python
from celery import Celery
from kombu import Queue
import os

# Create Celery app
celery_app = Celery(
    "storytelling_workspace",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # One task at a time
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks
    task_acks_late=True,  # Acknowledge after completion
    task_reject_on_worker_lost=True,
    task_default_queue="default",
    task_queues=(
        Queue("default", routing_key="task.#"),
        Queue("workflow", routing_key="workflow.#"),
        Queue("agents", routing_key="agents.#"),
        Queue("images", routing_key="images.#"),
    ),
    task_routes={
        "storytelling_workspace.workers.workflow_tasks.*": {"queue": "workflow"},
        "storytelling_workspace.workers.agent_tasks.*": {"queue": "agents"},
        "storytelling_workspace.workers.image_tasks.*": {"queue": "images"},
    }
)

# Auto-discover tasks
celery_app.autodiscover_tasks([
    "storytelling_workspace.workers"
])
```

#### 2. Workflow Tasks (`workflow_tasks.py`)

```python
from celery import Task, group, chain
from typing import Optional
import logging

from .celery_app import celery_app
from ..orchestrator import WorkflowOrchestrator
from ..db.session import get_db_session
from ..db.repositories import WorkflowStateRepository, ProjectRepository

logger = logging.getLogger(__name__)

class WorkflowTask(Task):
    """Base task with progress tracking."""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called on task success."""
        logger.info(f"Task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure."""
        logger.error(f"Task {task_id} failed: {exc}")

@celery_app.task(base=WorkflowTask, bind=True)
def start_workflow_task(
    self,
    project_id: str,
    workflow_id: str,
    resume_from: Optional[str] = None
):
    """Execute complete workflow."""
    logger.info(f"Starting workflow for project {project_id}")
    
    try:
        # Update progress: 0%
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 15, "phase": "setup"}
        )
        
        # Execute workflow phases
        # Phase 1: Setup (agents 1-4)
        phase_1_result = execute_phase_1.delay(project_id, workflow_id)
        
        # Wait for phase 1
        phase_1_result.get()
        
        # Update progress: 27%
        self.update_state(
            state="PROGRESS",
            meta={"current": 4, "total": 15, "phase": "drafting"}
        )
        
        # Phase 2: Drafting (agents 5-7)
        phase_2_result = execute_phase_2.delay(project_id, workflow_id)
        phase_2_result.get()
        
        # Update progress: 47%
        self.update_state(
            state="PROGRESS",
            meta={"current": 7, "total": 15, "phase": "editing"}
        )
        
        # Phase 3: Editing (agents 8-12)
        phase_3_result = execute_phase_3.delay(project_id, workflow_id)
        phase_3_result.get()
        
        # Update progress: 80%
        self.update_state(
            state="PROGRESS",
            meta={"current": 12, "total": 15, "phase": "assembly"}
        )
        
        # Phase 4: Assembly (agents 13-15)
        phase_4_result = execute_phase_4.delay(project_id, workflow_id)
        phase_4_result.get()
        
        # Update progress: 100%
        self.update_state(
            state="SUCCESS",
            meta={"current": 15, "total": 15, "phase": "completed"}
        )
        
        logger.info(f"Workflow completed for project {project_id}")
        return {"status": "completed", "project_id": project_id}
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        # Update workflow state to failed
        # TODO: Update database
        raise

@celery_app.task
def execute_phase_1(project_id: str, workflow_id: str):
    """Execute Phase 1: Setup."""
    # Run agents 1-4 sequentially
    # TODO: Implement agent execution
    pass

@celery_app.task
def execute_phase_2(project_id: str, workflow_id: str):
    """Execute Phase 2: Drafting."""
    # Run agents 5-7
    # Agent 6 (chapter drafting) can run in parallel batches
    pass

@celery_app.task
def execute_phase_3(project_id: str, workflow_id: str):
    """Execute Phase 3: Editing."""
    # Run agents 8-12 sequentially
    pass

@celery_app.task
def execute_phase_4(project_id: str, workflow_id: str):
    """Execute Phase 4: Assembly."""
    # Run agents 13-15 sequentially
    pass
```

#### 3. Agent Tasks (`agent_tasks.py`)

```python
from celery import Task
import logging

from .celery_app import celery_app
from ..agents import *

logger = logging.getLogger(__name__)

@celery_app.task
def execute_agent_task(
    agent_name: str,
    project_id: str,
    story_bible_data: dict,
    **kwargs
):
    """Execute a single agent."""
    logger.info(f"Executing agent: {agent_name}")
    
    # Map agent name to class
    agent_map = {
        "intake": IntakeAgent,
        "concept": ConceptAgent,
        "worldbuilding": WorldbuildingAgent,
        "character": CharacterAgent,
        "plot_architect": PlotArchitectAgent,
        # ... etc
    }
    
    agent_class = agent_map.get(agent_name)
    if not agent_class:
        raise ValueError(f"Unknown agent: {agent_name}")
    
    # Execute agent
    agent = agent_class(**kwargs)
    result = agent.execute(story_bible_data)
    
    return result
```

### Acceptance Criteria

- [ ] Celery worker starts successfully
- [ ] Tasks can be queued and executed
- [ ] Task results stored in Redis
- [ ] Task failures handled gracefully
- [ ] Progress tracking works
- [ ] Worker logs structured
- [ ] Tests pass

---

## Task 15: WebSocket for Real-time Updates

### Objectives

Implement WebSocket connections for real-time workflow progress updates.

### Implementation

#### 1. WebSocket Manager (`websocket/manager.py`)

```python
from fastapi import WebSocket
from typing import Dict, Set
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        # project_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, project_id: str):
        """Accept new connection."""
        await websocket.accept()
        
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        
        self.active_connections[project_id].add(websocket)
        logger.info(f"Client connected to project {project_id}")
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        """Remove connection."""
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            
            # Clean up empty sets
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        
        logger.info(f"Client disconnected from project {project_id}")
    
    async def broadcast_to_project(self, project_id: str, message: dict):
        """Broadcast message to all connections for a project."""
        if project_id not in self.active_connections:
            return
        
        # Remove dead connections
        dead_connections = set()
        
        for connection in self.active_connections[project_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                dead_connections.add(connection)
        
        # Clean up dead connections
        for connection in dead_connections:
            self.disconnect(connection, project_id)

# Global manager instance
manager = ConnectionManager()
```

#### 2. WebSocket Endpoint (`main.py` addition)

```python
from fastapi import WebSocket, WebSocketDisconnect
from .websocket.manager import manager

@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket, project_id)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Echo back (for ping/pong)
            await websocket.send_json({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
```

#### 3. Progress Broadcasting (from Celery tasks)

```python
# In workflow_tasks.py
from ..api.websocket.manager import manager

async def broadcast_progress(project_id: str, progress_data: dict):
    """Broadcast progress update via WebSocket."""
    await manager.broadcast_to_project(project_id, {
        "type": "progress",
        "data": progress_data
    })
```

### Acceptance Criteria

- [ ] WebSocket connections established
- [ ] Progress updates broadcast to clients
- [ ] Multiple clients supported
- [ ] Connection cleanup on disconnect
- [ ] Reconnection handling
- [ ] Tests pass

---

## Integration & Testing

### Integration Testing Strategy

```python
# tests/integration/test_api/test_workflow_integration.py
import pytest
from httpx import AsyncClient
import asyncio

@pytest.mark.asyncio
async def test_complete_workflow(client: AsyncClient, db_session):
    """Test complete workflow from API."""
    # 1. Create project
    response = await client.post("/api/projects", json={
        "name": "Test Novel",
        "genre": "Fantasy",
        "target_length": 80000
    })
    assert response.status_code == 201
    project_id = response.json()["id"]
    
    # 2. Start workflow
    response = await client.post(f"/api/workflow/{project_id}/start")
    assert response.status_code == 200
    workflow_id = response.json()["id"]
    
    # 3. Poll status until complete
    max_attempts = 60
    for _ in range(max_attempts):
        response = await client.get(f"/api/workflow/{project_id}/status")
        status = response.json()["status"]
        
        if status in ["completed", "failed"]:
            break
        
        await asyncio.sleep(5)
    
    assert status == "completed"
    
    # 4. Verify project updated
    response = await client.get(f"/api/projects/{project_id}")
    assert response.json()["status"] == "completed"
```

### Performance Testing

```python
# tests/performance/test_api_performance.py
import pytest
from httpx import AsyncClient
import time

@pytest.mark.asyncio
async def test_project_list_performance(client: AsyncClient):
    """Test project list endpoint performance."""
    start = time.time()
    response = await client.get("/api/projects?page=1&page_size=20")
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 0.2  # <200ms
```

---

## Deployment Considerations

### Environment Variables

```bash
# .env
DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/storytelling
REDIS_URL=redis://localhost:6379/0
MISTRAL_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
```

### Docker Compose Updates

```yaml
# docker-compose.yml additions
services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - mysql
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - mysql
      - redis
    command: celery -A storytelling_workspace.workers worker --loglevel=info
```

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Long-running tasks timeout | High | Implement task checkpointing, allow resume |
| WebSocket connection drops | Medium | Implement reconnection logic, fallback to polling |
| Database connection pool exhaustion | High | Configure pool size, implement connection retry |
| Celery worker crashes | High | Use supervisor/systemd, implement health checks |
| Race conditions in workflow state | Medium | Use database transactions, optimistic locking |

---

## Success Metrics

- **API Response Time**: <200ms p95 for CRUD operations
- **Workflow Execution**: Complete 80K-word novel in <45 minutes
- **WebSocket Latency**: <100ms for progress updates
- **Test Coverage**: ≥95% for all API code
- **Error Rate**: <0.1% for API requests

---

## Next Steps After Phase 3

1. **Phase 4: Web UI** - Build Next.js frontend consuming these APIs
2. **Phase 5: Deployment** - Dockerize all services, set up CI/CD
3. **Monitoring** - Add Prometheus metrics, Grafana dashboards
4. **Documentation** - API documentation, deployment guide

---

## Appendix: API Endpoint Summary

### Projects
- `POST /api/projects` - Create project
- `GET /api/projects` - List projects
- `GET /api/projects/{id}` - Get project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Workflow
- `POST /api/workflow/{project_id}/start` - Start workflow
- `POST /api/workflow/{project_id}/pause` - Pause workflow
- `POST /api/workflow/{project_id}/resume` - Resume workflow
- `GET /api/workflow/{project_id}/status` - Get status
- `POST /api/workflow/{project_id}/cancel` - Cancel workflow

### Checkpoints
- `GET /api/checkpoints/{project_id}` - List checkpoints
- `GET /api/checkpoints/{id}` - Get checkpoint
- `POST /api/checkpoints/{id}/approve` - Approve checkpoint
- `POST /api/checkpoints/{id}/reject` - Reject checkpoint

### Images
- `GET /api/images/{project_id}` - List images
- `GET /api/images/{id}` - Get image metadata
- `GET /api/images/{id}/download` - Download image

### Story Bible
- `GET /api/story-bible/{project_id}