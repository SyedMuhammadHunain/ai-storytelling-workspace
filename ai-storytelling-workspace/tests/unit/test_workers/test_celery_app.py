"""Unit tests for Celery app configuration."""

import pytest
from celery import Celery

from storytelling_workspace.workers.celery_app import celery_app, BaseTask, WorkflowTask


def test_celery_app_exists():
    """Test that Celery app is properly configured."""
    assert isinstance(celery_app, Celery)
    assert celery_app.main == "storytelling_workspace"


def test_celery_app_configuration():
    """Test Celery app configuration."""
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.accept_content == ["json"]
    assert celery_app.conf.result_serializer == "json"
    assert celery_app.conf.timezone == "UTC"
    assert celery_app.conf.enable_utc is True


def test_celery_queues_configured():
    """Test that queues are properly configured."""
    queue_names = [q.name for q in celery_app.conf.task_queues]
    assert "default" in queue_names
    assert "workflow" in queue_names
    assert "agents" in queue_names
    assert "images" in queue_names


def test_celery_task_routes():
    """Test that task routes are configured."""
    routes = celery_app.conf.task_routes
    assert "storytelling_workspace.workers.workflow_tasks.*" in routes
    assert "storytelling_workspace.workers.agent_tasks.*" in routes
    assert "storytelling_workspace.workers.image_tasks.*" in routes


def test_base_task_class():
    """Test BaseTask class configuration."""
    assert BaseTask.autoretry_for == (Exception,)
    assert BaseTask.retry_kwargs == {"max_retries": 3}
    assert BaseTask.retry_backoff is True
    assert BaseTask.retry_jitter is True


def test_workflow_task_class():
    """Test WorkflowTask class."""
    assert issubclass(WorkflowTask, BaseTask)
    assert hasattr(WorkflowTask, "update_workflow_progress")
    assert hasattr(WorkflowTask, "handle_workflow_error")


def test_celery_worker_configuration():
    """Test worker-specific configuration."""
    assert celery_app.conf.worker_prefetch_multiplier == 1
    assert celery_app.conf.worker_max_tasks_per_child == 10
    assert celery_app.conf.task_acks_late is True
    assert celery_app.conf.task_reject_on_worker_lost is True


def test_celery_task_limits():
    """Test task time limits."""
    assert celery_app.conf.task_time_limit == 3600  # 1 hour
    assert celery_app.conf.task_soft_time_limit == 3300  # 55 minutes


def test_celery_result_backend():
    """Test result backend configuration."""
    assert celery_app.conf.result_expires == 3600
    assert celery_app.conf.result_persistent is True
