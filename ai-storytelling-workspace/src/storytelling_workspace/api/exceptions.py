"""Custom API exceptions for structured error handling."""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class APIException(HTTPException):
    """
    Base API exception with structured error response.
    
    All custom exceptions should inherit from this class.
    """
    
    def __init__(
        self,
        status_code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize API exception.
        
        Args:
            status_code: HTTP status code
            message: Human-readable error message
            details: Additional error details (optional)
        """
        self.message = message
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message)


class ProjectNotFoundException(APIException):
    """Project not found in database."""
    
    def __init__(self, project_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Project not found: {project_id}",
            details={"project_id": project_id}
        )


class StoryBibleNotFoundException(APIException):
    """Story Bible not found in database."""
    
    def __init__(self, story_bible_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Story Bible not found: {story_bible_id}",
            details={"story_bible_id": story_bible_id}
        )


class CheckpointNotFoundException(APIException):
    """Checkpoint not found in database."""
    
    def __init__(self, checkpoint_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Checkpoint not found: {checkpoint_id}",
            details={"checkpoint_id": checkpoint_id}
        )


class ImageNotFoundException(APIException):
    """Image not found in database."""
    
    def __init__(self, image_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Image not found: {image_id}",
            details={"image_id": image_id}
        )


class WorkflowNotFoundException(APIException):
    """Workflow state not found in database."""
    
    def __init__(self, workflow_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Workflow not found: {workflow_id}",
            details={"workflow_id": workflow_id}
        )


class WorkflowAlreadyRunningException(APIException):
    """Workflow is already running for this project."""
    
    def __init__(self, project_id: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=f"Workflow already running for project: {project_id}",
            details={"project_id": project_id}
        )


class WorkflowNotRunningException(APIException):
    """No active workflow found for this project."""
    
    def __init__(self, project_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"No active workflow found for project: {project_id}",
            details={"project_id": project_id}
        )


class CheckpointAlreadyReviewedException(APIException):
    """Checkpoint has already been reviewed."""
    
    def __init__(self, checkpoint_id: str, status: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=f"Checkpoint already reviewed with status: {status}",
            details={"checkpoint_id": checkpoint_id, "status": status}
        )


class InvalidProjectStatusException(APIException):
    """Invalid project status transition."""
    
    def __init__(self, current_status: str, requested_status: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Cannot transition from {current_status} to {requested_status}",
            details={
                "current_status": current_status,
                "requested_status": requested_status
            }
        )


class DatabaseOperationException(APIException):
    """Database operation failed."""
    
    def __init__(self, operation: str, error: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database operation failed: {operation}",
            details={"operation": operation, "error": error}
        )


class ValidationException(APIException):
    """Request validation failed."""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=f"Validation error: {message}",
            details={"field": field, "message": message}
        )
