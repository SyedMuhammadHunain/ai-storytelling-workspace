"""Celery tasks for individual agent execution."""

import logging
from typing import Dict, Any, Optional

from .celery_app import celery_app, BaseTask

logger = logging.getLogger(__name__)


class AgentTask(BaseTask):
    """Base task for agent execution."""
    
    def execute_agent(
        self,
        agent_name: str,
        project_id: str,
        workflow_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an agent with given context.
        """
        logger.info(f"Executing agent {agent_name} for project {project_id}")
        
        import asyncio
        import importlib
        from storytelling_workspace.db.worker_session import worker_session
        from storytelling_workspace.db.repositories.story_bible import StoryBibleRepository
        from storytelling_workspace.core.ai_provider import AIProviderFactory
        from storytelling_workspace.story_bible import StoryBible
        
        async def fetch_bible():
            async with worker_session() as session:
                repo = StoryBibleRepository(session)
                db_bible = await repo.get_latest_by_project(project_id)
                if not db_bible:
                    return None
                return {
                    "version": db_bible.version,
                    "created_at": db_bible.created_at.isoformat() if db_bible.created_at else None,
                    "brief": db_bible.brief or {},
                    "concept": db_bible.concept or {},
                    "world_rules": db_bible.world_rules or {},
                    "characters": db_bible.characters or {},
                    "locations": db_bible.locations or {},
                    "timeline": db_bible.timeline or [],
                    "plot_threads": db_bible.plot_threads or {},
                    "terminology": db_bible.terminology or {},
                    "style_guide": db_bible.style_guide or {},
                    "metadata": db_bible.story_metadata or {}
                }

        async def save_bible(updated_bible):
            async with worker_session() as session:
                repo = StoryBibleRepository(session)
                db_bible = await repo.get_latest_by_project(project_id)
                domain_dict = updated_bible.to_dict()
                
                if not db_bible:
                    from storytelling_workspace.db.models.story_bible import StoryBible as DBStoryBible
                    db_bible = DBStoryBible(
                        project_id=str(project_id),
                        brief=domain_dict.get("brief"),
                        concept=domain_dict.get("concept"),
                        world_rules=domain_dict.get("world_rules"),
                        characters=domain_dict.get("characters"),
                        locations=domain_dict.get("locations"),
                        timeline=domain_dict.get("timeline"),
                        plot_threads=domain_dict.get("plot_threads"),
                        terminology=domain_dict.get("terminology"),
                        style_guide=domain_dict.get("style_guide"),
                        story_metadata=domain_dict.get("metadata")
                    )
                    session.add(db_bible)
                else:
                    db_bible.brief = domain_dict.get("brief")
                    db_bible.concept = domain_dict.get("concept")
                    db_bible.world_rules = domain_dict.get("world_rules")
                    db_bible.characters = domain_dict.get("characters")
                    db_bible.locations = domain_dict.get("locations")
                    db_bible.timeline = domain_dict.get("timeline")
                    db_bible.plot_threads = domain_dict.get("plot_threads")
                    db_bible.terminology = domain_dict.get("terminology")
                    db_bible.style_guide = domain_dict.get("style_guide")
                    db_bible.story_metadata = domain_dict.get("metadata")
                    db_bible.increment_version()
                await session.commit()

        async def run_all():
            db_data = await fetch_bible()
            if db_data:
                domain_bible = StoryBible.from_dict(db_data)
            else:
                domain_bible = StoryBible(project_name=str(project_id))
            
            factory = AIProviderFactory()
            ai_provider = factory.primary
            agent_map = {
                "intake": ("storytelling_workspace.agents.intake", "IntakeAgent"),
                "concept": ("storytelling_workspace.agents.concept", "ConceptAgent"),
                "worldbuilding": ("storytelling_workspace.agents.worldbuilding", "WorldbuildingAgent"),
                "character": ("storytelling_workspace.agents.character", "CharacterAgent"),
                "outline": ("storytelling_workspace.agents.plot_architect", "PlotArchitectAgent"),
                "chapter_drafting": ("storytelling_workspace.agents.chapter_drafting", "ChapterDraftingAgent"),
                "continuity": ("storytelling_workspace.agents.continuity", "ContinuityAgent"),
                "developmental_editor": ("storytelling_workspace.agents.dev_editor", "DevelopmentalEditorAgent"),
                "line_editor": ("storytelling_workspace.agents.line_editor", "LineEditorAgent"),
                "copy_editor": ("storytelling_workspace.agents.copy_editor", "CopyEditorAgent"),
                "proofreader": ("storytelling_workspace.agents.proofreader", "ProofreaderAgent"),
                "sensitivity_reader": ("storytelling_workspace.agents.qa", "QAAgent"),
                "formatter": ("storytelling_workspace.agents.compilation", "CompilationAgent"),
                "cover_designer": ("storytelling_workspace.agents.ai_image_generator", "AIImageGeneratorAgent"),
                "metadata_generator": ("storytelling_workspace.agents.export", "ExportAgent"),
            }
            
            if agent_name in agent_map:
                mod_name, cls_name = agent_map[agent_name]
                module = importlib.import_module(mod_name)
                agent_cls = getattr(module, cls_name)
                try:
                    agent = agent_cls(ai_provider=ai_provider)
                except TypeError:
                    agent = agent_cls()
            else:
                raise ValueError(f"Unknown agent: {agent_name}")
                
            # Execute asynchronously since agents are now async
            result = await agent.execute(domain_bible)
            
            await save_bible(domain_bible)
            
            return {
                "agent": agent_name,
                "status": "completed",
                "output": result,
                "checkpoint_created": False
            }

        try:
            from storytelling_workspace.workers.celery_app import run_async
            return run_async(run_all())
        except Exception as e:
            logger.error(f"Agent {agent_name} failed: {e}", exc_info=True)
            raise


# Phase 1: Setup Agents

@celery_app.task(base=AgentTask, bind=True, name="agents.intake")
def intake_agent_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 1: Intake Agent.
    
    Processes user brief and extracts key requirements.
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with extracted requirements
    """
    return self.execute_agent("intake", project_id, workflow_id, context)


@celery_app.task(base=AgentTask, bind=True, name="agents.concept")
def concept_agent_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 2: Concept Agent.
    
    Develops story concept from requirements.
    Creates checkpoint for user approval.
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with story concept
    """
    return self.execute_agent("concept", project_id, workflow_id, context)


@celery_app.task(base=AgentTask, bind=True, name="agents.worldbuilding")
def worldbuilding_agent_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 3: Worldbuilding Agent.
    
    Creates world rules, magic systems, technology, etc.
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with world rules
    """
    return self.execute_agent("worldbuilding", project_id, workflow_id, context)


@celery_app.task(base=AgentTask, bind=True, name="agents.character")
def character_agent_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 4: Character Agent.
    
    Designs main and supporting characters.
    Creates checkpoint for character approval.
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with character designs
    """
    return self.execute_agent("character", project_id, workflow_id, context)


# Phase 2: Drafting Agents

@celery_app.task(base=AgentTask, bind=True, name="agents.outline")
def outline_agent_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 5: Outline Agent.
    
    Creates detailed chapter-by-chapter outline.
    Creates checkpoint for outline approval.
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with chapter outline
    """
    return self.execute_agent("outline", project_id, workflow_id, context)


@celery_app.task(base=AgentTask, bind=True, name="agents.chapter_drafting")
def chapter_drafting_agent_task(
    self,
    project_id: str,
    workflow_id: str,
    context: Dict[str, Any],
    chapter_number: int
):
    """
    Agent 6: Chapter Drafting Agent.
    
    Drafts a single chapter. Can run in parallel for multiple chapters.
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        chapter_number: Chapter number to draft
        
    Returns:
        dict: Agent result with drafted chapter
    """
    logger.info(f"Drafting chapter {chapter_number} for project {project_id}")
    
    context["chapter_number"] = chapter_number
    return self.execute_agent("chapter_drafting", project_id, workflow_id, context)


@celery_app.task(base=AgentTask, bind=True, name="agents.continuity")
def continuity_agent_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 7: Continuity Agent.
    
    Checks consistency across all chapters.
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with continuity report
    """
    return self.execute_agent("continuity", project_id, workflow_id, context)


# Phase 3: Editing Agents

@celery_app.task(base=AgentTask, bind=True, name="agents.developmental_editor")
def developmental_editor_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 8: Developmental Editor.
    
    Performs structural editing (plot, pacing, character arcs).
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with structural edits
    """
    return self.execute_agent("developmental_editor", project_id, workflow_id, context)


@celery_app.task(base=AgentTask, bind=True, name="agents.line_editor")
def line_editor_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 9: Line Editor.
    
    Performs sentence-level editing (clarity, flow, style).
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with line edits
    """
    return self.execute_agent("line_editor", project_id, workflow_id, context)


@celery_app.task(base=AgentTask, bind=True, name="agents.copy_editor")
def copy_editor_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 10: Copy Editor.
    
    Performs copy editing (grammar, punctuation, consistency).
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with copy edits
    """
    return self.execute_agent("copy_editor", project_id, workflow_id, context)


@celery_app.task(base=AgentTask, bind=True, name="agents.proofreader")
def proofreader_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 11: Proofreader.
    
    Final proofreading pass for typos and errors.
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with proofreading corrections
    """
    return self.execute_agent("proofreader", project_id, workflow_id, context)


@celery_app.task(base=AgentTask, bind=True, name="agents.sensitivity_reader")
def sensitivity_reader_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 12: Sensitivity Reader.
    
    Reviews content for cultural sensitivity and representation.
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with sensitivity review
    """
    return self.execute_agent("sensitivity_reader", project_id, workflow_id, context)


# Phase 4: Assembly Agents

@celery_app.task(base=AgentTask, bind=True, name="agents.formatter")
def formatter_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 13: Formatter.
    
    Formats manuscript for publication (EPUB, PDF, etc.).
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with formatted files
    """
    return self.execute_agent("formatter", project_id, workflow_id, context)


@celery_app.task(base=AgentTask, bind=True, name="agents.cover_designer")
def cover_designer_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 14: Cover Designer.
    
    Generates cover art using image generation API.
    Creates checkpoint for cover approval.
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with cover art
    """
    return self.execute_agent("cover_designer", project_id, workflow_id, context)


@celery_app.task(base=AgentTask, bind=True, name="agents.metadata_generator")
def metadata_generator_task(self, project_id: str, workflow_id: str, context: Dict[str, Any]):
    """
    Agent 15: Metadata Generator.
    
    Generates publication metadata (blurb, keywords, categories).
    
    Args:
        self: Task instance
        project_id: Project UUID
        workflow_id: Workflow state UUID
        context: Execution context
        
    Returns:
        dict: Agent result with metadata
    """
    return self.execute_agent("metadata_generator", project_id, workflow_id, context)


# Utility tasks

@celery_app.task(name="agents.create_checkpoint")
def create_checkpoint_task(
    project_id: str,
    workflow_id: str,
    checkpoint_type: str,
    phase: str,
    agent_name: str,
    content: Dict[str, Any]
):
    """
    Create a checkpoint for user review.
    
    Args:
        project_id: Project UUID
        workflow_id: Workflow state UUID
        checkpoint_type: Type of checkpoint
        phase: Current phase
        agent_name: Agent that created the checkpoint
        content: Checkpoint content
        
    Returns:
        dict: Created checkpoint info
    """
    logger.info(f"Creating {checkpoint_type} checkpoint for project {project_id}")
    
    try:
        # TODO: Create checkpoint in database
        # TODO: Send notification via WebSocket
        
        return {
            "checkpoint_id": "placeholder",
            "status": "pending",
            "type": checkpoint_type
        }
        
    except Exception as e:
        logger.error(f"Failed to create checkpoint: {e}", exc_info=True)
        raise


@celery_app.task(name="agents.wait_for_checkpoint_approval")
def wait_for_checkpoint_approval_task(checkpoint_id: str, timeout_seconds: int = 86400):
    """
    Wait for checkpoint approval (blocking).
    
    Args:
        checkpoint_id: Checkpoint UUID
        timeout_seconds: Maximum wait time (default 24 hours)
        
    Returns:
        dict: Approval result
    """
    logger.info(f"Waiting for checkpoint {checkpoint_id} approval")
    
    try:
        # TODO: Implement polling or event-based waiting
        # This would check the checkpoint status periodically
        # or use a message queue for approval events
        
        return {
            "checkpoint_id": checkpoint_id,
            "status": "approved",
            "feedback": None
        }
        
    except Exception as e:
        logger.error(f"Failed to wait for checkpoint approval: {e}", exc_info=True)
        raise
