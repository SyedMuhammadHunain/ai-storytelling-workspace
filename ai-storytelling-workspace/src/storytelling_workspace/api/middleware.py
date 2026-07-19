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


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for basic IP-based rate limiting.
    """
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        from collections import defaultdict
        self.clients = defaultdict(list)
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Clean up requests older than 1 minute
        self.clients[client_ip] = [t for t in self.clients[client_ip] if now - t < 60]
        
        if len(self.clients[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": "Rate limit exceeded. Please try again later."
                }
            )
            
        self.clients[client_ip].append(now)
        return await call_next(request)
