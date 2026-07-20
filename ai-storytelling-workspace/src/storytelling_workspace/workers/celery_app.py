"""Celery application configuration for async task processing."""

import os
from celery import Celery
from kombu import Queue

# Create Celery app
celery_app = Celery(
    "storytelling_workspace",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

# Configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # 55 minutes soft limit
    task_acks_late=True,  # Acknowledge after completion (for reliability)
    task_reject_on_worker_lost=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,  # One task at a time per worker
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks (prevent memory leaks)
    worker_disable_rate_limits=False,
    
    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,
    
    # Queues
    task_default_queue="default",
    task_queues=(
        Queue("default", routing_key="task.#"),
        Queue("workflow", routing_key="workflow.#"),
        Queue("agents", routing_key="agents.#"),
        Queue("images", routing_key="images.#"),
    ),
    
    # Task routing
    task_routes={
        "storytelling_workspace.workers.workflow_tasks.*": {"queue": "workflow"},
        "storytelling_workspace.workers.agent_tasks.*": {"queue": "agents"},
        "storytelling_workspace.workers.image_tasks.*": {"queue": "images"},
    },
    
    # Retry policy
    task_default_retry_delay=60,  # Retry after 60 seconds
    task_max_retries=3,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Auto-discover tasks
celery_app.conf.imports = (
    "storytelling_workspace.workers.workflow_tasks",
    "storytelling_workspace.workers.agent_tasks",
    "storytelling_workspace.workers.image_tasks"
)


# Task base classes for common functionality
class BaseTask(celery_app.Task):
    """Base task with common functionality."""
    
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds."""
        pass
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails."""
        pass
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried."""
        pass


class WorkflowTask(BaseTask):
    """Base task for workflow operations with progress tracking."""
    
    def update_workflow_progress(self, workflow_id: str, progress: float, message: str):
        """Update workflow progress in database."""
        # TODO: Implement database update
        pass
    
    def handle_workflow_error(self, workflow_id: str, error: str):
        """Handle workflow error."""
        # TODO: Implement error handling
        pass
