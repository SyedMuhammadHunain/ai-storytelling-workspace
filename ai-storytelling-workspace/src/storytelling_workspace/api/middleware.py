"""Custom middleware for FastAPI application."""

import logging
import time
import traceback
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .exceptions import APIException

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses with timing.
    
    Logs in structured JSON format for easy parsing and analysis.
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and log details.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        # Start timer
        start_time = time.time()
        
        # Extract request details
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else None
        client_host = request.client.host if request.client else "unknown"
        
        # Log incoming request
        logger.info(
            f"Request started",
            extra={
                "method": method,
                "path": path,
                "query_params": query_params,
                "client_host": client_host
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception
            logger.error(
                f"Request failed with exception",
                extra={
                    "method": method,
                    "path": path,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            )
            raise
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log response
        logger.info(
            f"Request completed",
            extra={
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2)
            }
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
        
        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch and handle all unhandled exceptions.
    
    Converts exceptions to structured JSON responses and logs errors.
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and handle exceptions.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response or error response
        """
        try:
            return await call_next(request)
        
        except APIException as e:
            # Custom API exceptions - already structured
            logger.warning(
                f"API exception: {e.message}",
                extra={
                    "status_code": e.status_code,
                    "details": e.details,
                    "path": request.url.path
                }
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.message,
                    "details": e.details
                }
            )
        
        except ValueError as e:
            # Validation errors
            logger.warning(
                f"Validation error: {str(e)}",
                extra={"path": request.url.path}
            )
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Validation error",
                    "message": str(e)
                }
            )
        
        except Exception as e:
            # Unhandled exceptions
            logger.error(
                f"Unhandled exception: {str(e)}",
                extra={
                    "path": request.url.path,
                    "traceback": traceback.format_exc()
                }
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": str(e) if logger.level == logging.DEBUG else "An unexpected error occurred"
                }
            )


class CORSHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add CORS headers to responses.
    
    Note: This is a fallback. Prefer using FastAPI's CORSMiddleware.
    """
    
    def __init__(self, app, allowed_origins: list[str] = None):
        """
        Initialize CORS middleware.
        
        Args:
            app: FastAPI application
            allowed_origins: List of allowed origins (default: ["*"])
        """
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Add CORS headers to response.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response with CORS headers
        """
        response = await call_next(request)
        
        # Add CORS headers
        origin = request.headers.get("origin")
        if origin and (origin in self.allowed_origins or "*" in self.allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response
