"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from ..config import settings
from ..db.session import init_db, close_db
from .exceptions import APIException
from .middleware import LoggingMiddleware, ErrorHandlerMiddleware, RateLimitMiddleware
from .websocket.manager import manager

# Configure structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting AI Storytelling Workspace API...")
    logger.info(f"Environment: {'development' if settings.DEBUG else 'production'}")
    logger.info(f"Database: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")
    
    # Initialize database connection pool
    # Note: Tables should be created via Alembic migrations, not init_db()
    # await init_db()  # Only use in development/testing
    
    # Start Redis Pub/Sub listener for workflow updates from Celery
    await manager.start_redis_listener()
    
    logger.info("API server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API server...")
    await manager.stop_redis_listener()
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="AI Storytelling Workspace API",
    description="Production API for AI-powered novel generation with 15 specialized agents",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# Middleware stack (order matters - first added = outermost layer)
# 1. GZIP compression for responses > 1KB
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000
)

# 2. CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
    expose_headers=["X-Process-Time"],
)

# 2.5 Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# 3. Rate Limiting (100 requests per minute by default)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# 4. Request/response logging
app.add_middleware(LoggingMiddleware)

# 4. Error handling (innermost - catches all exceptions)
app.add_middleware(ErrorHandlerMiddleware)


# Exception handlers
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """
    Handle custom API exceptions.
    
    Args:
        request: HTTP request
        exc: API exception
        
    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Handle ValueError exceptions (validation errors).
    
    Args:
        request: HTTP request
        exc: ValueError exception
        
    Returns:
        JSON error response
    """
    logger.warning(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation error",
            "message": str(exc)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions.
    
    Args:
        request: HTTP request
        exc: Exception
        
    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        API metadata
    """
    return {
        "name": "AI Storytelling Workspace API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/api/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for Docker/Kubernetes.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "ai-storytelling-workspace-api",
        "version": "2.0.0"
    }


# WebSocket endpoint for real-time updates
from fastapi import WebSocket, WebSocketDisconnect


@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint for real-time workflow updates.
    
    Args:
        websocket: WebSocket connection
        project_id: Project UUID to subscribe to
    """
    await manager.connect(websocket, project_id)
    
    try:
        while True:
            # Keep connection alive and handle ping/pong
            data = await websocket.receive_text()
            
            # Echo back for ping/pong
            if data == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
        logger.info(f"WebSocket disconnected for project {project_id}")


# Include routers
from .routes import projects, workflow, checkpoints, images, story_bible

app.include_router(
    projects.router,
    prefix="/api/projects",
    tags=["Projects"]
)

app.include_router(
    workflow.router,
    prefix="/api/workflow",
    tags=["Workflow"]
)

app.include_router(
    checkpoints.router,
    prefix="/api/checkpoints",
    tags=["Checkpoints"]
)

app.include_router(
    images.router,
    prefix="/api/images",
    tags=["Images"]
)

app.include_router(
    story_bible.router,
    prefix="/api/story-bible",
    tags=["Story Bible"]
)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "storytelling_workspace.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )