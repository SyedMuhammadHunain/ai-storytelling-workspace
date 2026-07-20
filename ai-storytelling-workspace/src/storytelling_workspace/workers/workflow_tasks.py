"""Celery tasks for workflow orchestration."""

import logging
from typing import Optional
import asyncio
import json
import redis.asyncio as aioredis

from .celery_app import celery_app, WorkflowTask, run_async
from ..config import settings
from ..db.worker_session import worker_session
from ..db.repositories.workflow_state import WorkflowStateRepository

logger = logging.getLogger(__name__)


@celery_app.task(base=WorkflowTask, bind=True, name="workflow.start")
def start_workflow_task(
    self,
    project_id: str,
    workflow_id: str,
    resume_from_checkpoint: Optional[str] = None
):
    """
    Start workflow execution for a project.
    
    This is the main orchestration task that coordinates all workflow phases.
    """
    logger.info(f"Starting workflow {workflow_id} for project {project_id}")
    
    try:
        self.update_state(
            state="PROGRESS",
            meta={
                "current": 0,
                "total": 15,
                "phase": "initialization",
                "message": "Initializing workflow..."
            }
        )
        
        # Phase 1: Setup (4 agents)
        logger.info(f"Executing Phase 1: Setup for workflow {workflow_id}")
        execute_phase_1.apply_async(
            args=[project_id, workflow_id],
            link=phase_1_complete.s(project_id, workflow_id)
        )
        
        return {
            "status": "started",
            "project_id": project_id,
            "workflow_id": workflow_id,
            "message": "Workflow execution started"
        }
        
    except Exception as e:
        logger.error(f"Failed to start workflow {workflow_id}: {e}", exc_info=True)
        mark_workflow_failed.delay(workflow_id, str(e))
        raise


@celery_app.task(name="workflow.phase_1")
def execute_phase_1(project_id: str, workflow_id: str):
    """Execute Phase 1: Setup."""
    logger.info(f"Phase 1 (Setup) started for workflow {workflow_id}")
    
    try:
        from .agent_tasks import AgentTask
        task = AgentTask()
        
        update_workflow_progress.delay(workflow_id, 1, 15, "setup", "Running Intake Agent...")
        task.execute_agent("intake", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 2, 15, "setup", "Running Concept Agent...")
        task.execute_agent("concept", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 3, 15, "setup", "Running Worldbuilding Agent...")
        task.execute_agent("worldbuilding", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 4, 15, "setup", "Running Character Agent...")
        task.execute_agent("character", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 4, 15, "setup", "Phase 1 (Setup) completed")
        
        return {
            "phase": 1,
            "status": "completed",
            "agents_executed": 4
        }
        
    except Exception as e:
        logger.error(f"Phase 1 failed for workflow {workflow_id}: {e}", exc_info=True)
        mark_workflow_failed.delay(workflow_id, f"Phase 1 failed: {e}")
        raise


@celery_app.task(name="workflow.phase_1_complete")
def phase_1_complete(phase_result, project_id: str, workflow_id: str):
    """Callback after Phase 1 completion."""
    logger.info(f"Phase 1 completed for workflow {workflow_id}, starting Phase 2")
    
    execute_phase_2.apply_async(
        args=[project_id, workflow_id],
        link=phase_2_complete.s(project_id, workflow_id)
    )


@celery_app.task(name="workflow.phase_2")
def execute_phase_2(project_id: str, workflow_id: str):
    """Execute Phase 2: Drafting."""
    logger.info(f"Phase 2 (Drafting) started for workflow {workflow_id}")
    
    try:
        from .agent_tasks import AgentTask
        task = AgentTask()
        
        update_workflow_progress.delay(workflow_id, 5, 15, "drafting", "Running Outline Agent...")
        task.execute_agent("outline", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 6, 15, "drafting", "Running Chapter Drafting Agent...")
        task.execute_agent("chapter_drafting", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 7, 15, "drafting", "Running Continuity Agent...")
        task.execute_agent("continuity", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 7, 15, "drafting", "Phase 2 (Drafting) completed")
        
        return {
            "phase": 2,
            "status": "completed",
            "agents_executed": 3
        }
        
    except Exception as e:
        logger.error(f"Phase 2 failed for workflow {workflow_id}: {e}", exc_info=True)
        mark_workflow_failed.delay(workflow_id, f"Phase 2 failed: {e}")
        raise


@celery_app.task(name="workflow.phase_2_complete")
def phase_2_complete(phase_result, project_id: str, workflow_id: str):
    """Callback after Phase 2 completion."""
    logger.info(f"Phase 2 completed for workflow {workflow_id}, starting Phase 3")
    
    execute_phase_3.apply_async(
        args=[project_id, workflow_id],
        link=phase_3_complete.s(project_id, workflow_id)
    )


@celery_app.task(name="workflow.phase_3")
def execute_phase_3(project_id: str, workflow_id: str):
    """Execute Phase 3: Editing."""
    logger.info(f"Phase 3 (Editing) started for workflow {workflow_id}")
    
    try:
        from .agent_tasks import AgentTask
        task = AgentTask()
        
        update_workflow_progress.delay(workflow_id, 8, 15, "editing", "Running Developmental Editor...")
        task.execute_agent("developmental_editor", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 9, 15, "editing", "Running Line Editor...")
        task.execute_agent("line_editor", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 10, 15, "editing", "Running Copy Editor...")
        task.execute_agent("copy_editor", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 11, 15, "editing", "Running Proofreader...")
        task.execute_agent("proofreader", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 12, 15, "editing", "Running Sensitivity Reader...")
        task.execute_agent("sensitivity_reader", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 12, 15, "editing", "Phase 3 (Editing) completed")
        
        return {
            "phase": 3,
            "status": "completed",
            "agents_executed": 5
        }
        
    except Exception as e:
        logger.error(f"Phase 3 failed for workflow {workflow_id}: {e}", exc_info=True)
        mark_workflow_failed.delay(workflow_id, f"Phase 3 failed: {e}")
        raise


@celery_app.task(name="workflow.phase_3_complete")
def phase_3_complete(phase_result, project_id: str, workflow_id: str):
    """Callback after Phase 3 completion."""
    logger.info(f"Phase 3 completed for workflow {workflow_id}, starting Phase 4")
    
    execute_phase_4.apply_async(
        args=[project_id, workflow_id],
        link=workflow_complete.s(project_id, workflow_id)
    )


@celery_app.task(name="workflow.phase_4")
def execute_phase_4(project_id: str, workflow_id: str):
    """Execute Phase 4: Assembly."""
    logger.info(f"Phase 4 (Assembly) started for workflow {workflow_id}")
    
    try:
        from .agent_tasks import AgentTask
        task = AgentTask()
        
        update_workflow_progress.delay(workflow_id, 13, 15, "assembly", "Running Formatter...")
        task.execute_agent("formatter", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 14, 15, "assembly", "Running Cover Designer...")
        task.execute_agent("cover_designer", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 15, 15, "assembly", "Running Metadata Generator...")
        task.execute_agent("metadata_generator", project_id, workflow_id, {})
        
        update_workflow_progress.delay(workflow_id, 15, 15, "assembly", "Phase 4 (Assembly) completed")
        
        return {
            "phase": 4,
            "status": "completed",
            "agents_executed": 3
        }
        
    except Exception as e:
        logger.error(f"Phase 4 failed for workflow {workflow_id}: {e}", exc_info=True)
        mark_workflow_failed.delay(workflow_id, f"Phase 4 failed: {e}")
        raise


@celery_app.task(name="workflow.complete")
def workflow_complete(phase_result, project_id: str, workflow_id: str):
    """Mark workflow as completed."""
    logger.info(f"Workflow {workflow_id} completed successfully")
    
    try:
        async def _complete():
            async with worker_session() as session:
                repo = WorkflowStateRepository(session)
                await repo.update(
                    workflow_id,
                    status="completed",
                    progress_percentage=100.0,
                    current_phase="completed"
                )
                await session.commit()
                
            redis = aioredis.from_url(settings.CELERY_BROKER_URL)
            payload = json.dumps({
                "type": "status",
                "project_id": project_id,
                "workflow_id": workflow_id,
                "status": "completed",
                "message": "Workflow completed successfully"
            })
            await redis.publish("workflow_updates", payload)
            await redis.aclose()

        run_async(_complete())
        
        return {
            "status": "completed",
            "project_id": project_id,
            "workflow_id": workflow_id,
            "message": "Workflow completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to mark workflow as complete: {e}", exc_info=True)
        raise


@celery_app.task(name="workflow.update_progress")
def update_workflow_progress(
    workflow_id: str,
    current_step: int,
    total_steps: int,
    phase: str,
    message: str
):
    """Update workflow progress in database."""
    logger.info(f"Updating workflow {workflow_id} progress: {current_step}/{total_steps} - {message}")
    
    try:
        async def _update():
            project_id = None
            progress = (current_step / total_steps) * 100.0 if total_steps > 0 else 0.0
            
            async with worker_session() as session:
                repo = WorkflowStateRepository(session)
                state = await repo.get_by_id(workflow_id)
                if state:
                    project_id = str(state.project_id)
                    await repo.update(
                        workflow_id,
                        current_phase=phase,
                        current_agent=message,
                        progress_percentage=progress,
                        completed_steps=current_step,
                        total_steps=total_steps,
                        status="running"
                    )
                    await session.commit()
            
            # Publish WebSocket update
            if project_id:
                try:
                    redis = aioredis.from_url(settings.CELERY_BROKER_URL)
                    payload = json.dumps({
                        "type": "progress",
                        "project_id": project_id,
                        "workflow_id": workflow_id,
                        "status": "running",
                        "current_step": current_step,
                        "total_steps": total_steps,
                        "phase": phase,
                        "message": message,
                        "progress": progress
                    })
                    await redis.publish("workflow_updates", payload)
                    await redis.aclose()
                except Exception as redis_err:
                    logger.warning(f"Failed to publish progress to Redis: {redis_err}")

        run_async(_update())
        
    except Exception as e:
        logger.error(f"Failed to update workflow progress: {e}", exc_info=True)


@celery_app.task(name="workflow.mark_failed")
def mark_workflow_failed(workflow_id: str, error_message: str):
    """Mark workflow as failed."""
    logger.error(f"Marking workflow {workflow_id} as failed: {error_message}")
    
    try:
        async def _fail():
            project_id = None
            async with worker_session() as session:
                repo = WorkflowStateRepository(session)
                state = await repo.get_by_id(workflow_id)
                if state:
                    project_id = str(state.project_id)
                    await repo.update(
                        workflow_id,
                        status="failed",
                        error_message=error_message
                    )
                    await session.commit()
            
            # Publish failure via WebSocket
            if project_id:
                try:
                    redis = aioredis.from_url(settings.CELERY_BROKER_URL)
                    status_payload = json.dumps({
                        "type": "error",
                        "project_id": project_id,
                        "workflow_id": workflow_id,
                        "status": "failed",
                        "message": error_message
                    })
                    await redis.publish("workflow_updates", status_payload)
                    await redis.aclose()
                except Exception as redis_err:
                    logger.warning(f"Failed to publish failure to Redis: {redis_err}")

        run_async(_fail())
        
    except Exception as e:
        logger.error(f"Failed to mark workflow as failed: {e}", exc_info=True)


@celery_app.task(name="workflow.pause")
def pause_workflow_task(workflow_id: str):
    """Pause workflow execution."""
    logger.info(f"Pausing workflow {workflow_id}")
    
    try:
        async def _pause():
            async with worker_session() as session:
                repo = WorkflowStateRepository(session)
                state = await repo.get_by_id(workflow_id)
                if state:
                    project_id = str(state.project_id)
                    await repo.update(
                        workflow_id,
                        status="paused"
                    )
                    await session.commit()
                    
                    # Publish pause via WebSocket
                    try:
                        redis = aioredis.from_url(settings.CELERY_BROKER_URL)
                        payload = json.dumps({
                            "type": "status",
                            "project_id": project_id,
                            "workflow_id": workflow_id,
                            "status": "paused",
                            "message": "Workflow paused"
                        })
                        await redis.publish("workflow_updates", payload)
                        await redis.aclose()
                    except Exception as redis_err:
                        logger.warning(f"Failed to publish pause to Redis: {redis_err}")
                        
        run_async(_pause())
        
    except Exception as e:
        logger.error(f"Failed to pause workflow: {e}", exc_info=True)
        raise


@celery_app.task(name="workflow.cancel")
def cancel_workflow_task(workflow_id: str):
    """Cancel workflow execution."""
    logger.info(f"Cancelling workflow {workflow_id}")
    
    try:
        async def _cancel():
            async with worker_session() as session:
                repo = WorkflowStateRepository(session)
                state = await repo.get_by_id(workflow_id)
                if state:
                    project_id = str(state.project_id)
                    await repo.update(
                        workflow_id,
                        status="cancelled"
                    )
                    await session.commit()
                    
                    try:
                        redis = aioredis.from_url(settings.CELERY_BROKER_URL)
                        payload = json.dumps({
                            "type": "status",
                            "project_id": project_id,
                            "workflow_id": workflow_id,
                            "status": "cancelled",
                            "message": "Workflow cancelled"
                        })
                        await redis.publish("workflow_updates", payload)
                        await redis.aclose()
                    except Exception as redis_err:
                        logger.warning(f"Failed to publish cancel to Redis: {redis_err}")
        
        run_async(_cancel())
        
    except Exception as e:
        logger.error(f"Failed to cancel workflow: {e}", exc_info=True)
        raise

@celery_app.task(name="workflow.resume")
def resume_workflow_task(workflow_id: str):
    """Resume workflow execution."""
    logger.info(f"Resuming workflow {workflow_id}")
    
    try:
        async def _resume():
            async with worker_session() as session:
                repo = WorkflowStateRepository(session)
                state = await repo.get_by_id(workflow_id)
                if state:
                    project_id = str(state.project_id)
                    current_phase = state.current_phase or "setup"
                    await repo.update(
                        workflow_id,
                        status="running"
                    )
                    await session.commit()
                    
                    try:
                        redis = aioredis.from_url(settings.CELERY_BROKER_URL)
                        payload = json.dumps({
                            "type": "status",
                            "project_id": project_id,
                            "workflow_id": workflow_id,
                            "status": "running",
                            "message": f"Workflow resumed from phase: {current_phase}"
                        })
                        await redis.publish("workflow_updates", payload)
                        await redis.aclose()
                    except Exception as redis_err:
                        logger.warning(f"Failed to publish resume to Redis: {redis_err}")
                        
        run_async(_resume())
        
    except Exception as e:
        logger.error(f"Failed to resume workflow: {e}", exc_info=True)
        raise
