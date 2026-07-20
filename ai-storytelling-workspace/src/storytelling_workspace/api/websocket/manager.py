"""WebSocket connection manager for real-time updates."""

import logging
from typing import Dict, Set
from datetime import datetime

from fastapi import WebSocket
import asyncio
import json
import redis.asyncio as aioredis
from storytelling_workspace.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    
    Supports multiple clients per project and broadcasts updates
    to all connected clients for a given project.
    """
    
    def __init__(self):
        """Initialize connection manager."""
        # Map of project_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.redis_client = None
        self.pubsub = None
        self.listener_task = None
        logger.info("WebSocket ConnectionManager initialized")
    
    async def connect(self, websocket: WebSocket, project_id: str):
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            project_id: Project UUID
        """
        await websocket.accept()
        
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        
        self.active_connections[project_id].add(websocket)
        
        logger.info(
            f"Client connected to project {project_id}. "
            f"Total connections: {len(self.active_connections[project_id])}"
        )
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "project_id": project_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to workflow updates"
        })
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            project_id: Project UUID
        """
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            
            # Clean up empty project entries
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        
        logger.info(
            f"Client disconnected from project {project_id}. "
            f"Remaining connections: {len(self.active_connections.get(project_id, []))}"
        )
    
    async def broadcast_to_project(self, project_id: str, message: dict):
        """
        Broadcast a message to all connections for a project.
        
        Args:
            project_id: Project UUID
            message: Message to broadcast (will be JSON serialized)
        """
        if project_id not in self.active_connections:
            logger.debug(f"No active connections for project {project_id}")
            return
        
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()
        
        # Track dead connections for cleanup
        dead_connections = set()
        
        for connection in self.active_connections[project_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(
                    f"Failed to send message to connection: {e}",
                    exc_info=True
                )
                dead_connections.add(connection)
        
        # Clean up dead connections
        for connection in dead_connections:
            self.disconnect(connection, project_id)
        
        logger.debug(
            f"Broadcast message to {len(self.active_connections[project_id])} "
            f"clients for project {project_id}"
        )
    
    async def send_progress_update(
        self,
        project_id: str,
        workflow_id: str,
        phase: str,
        agent: str,
        progress: float,
        message: str
    ):
        """
        Send a workflow progress update.
        
        Args:
            project_id: Project UUID
            workflow_id: Workflow UUID
            phase: Current phase name
            agent: Current agent name
            progress: Progress percentage (0-100)
            message: Progress message
        """
        await self.broadcast_to_project(project_id, {
            "type": "progress",
            "project_id": project_id,
            "workflow_id": workflow_id,
            "phase": phase,
            "agent": agent,
            "progress": progress,
            "message": message
        })
    
    async def send_checkpoint_notification(
        self,
        project_id: str,
        checkpoint_id: str,
        checkpoint_type: str,
        phase: str,
        agent: str
    ):
        """
        Send a checkpoint notification.
        
        Args:
            project_id: Project UUID
            checkpoint_id: Checkpoint UUID
            checkpoint_type: Type of checkpoint
            phase: Current phase
            agent: Agent that created checkpoint
        """
        await self.broadcast_to_project(project_id, {
            "type": "checkpoint",
            "project_id": project_id,
            "checkpoint_id": checkpoint_id,
            "checkpoint_type": checkpoint_type,
            "phase": phase,
            "agent": agent,
            "message": f"New {checkpoint_type} checkpoint ready for review"
        })
    
    async def send_workflow_status(
        self,
        project_id: str,
        workflow_id: str,
        status: str,
        message: str
    ):
        """
        Send workflow status change notification.
        
        Args:
            project_id: Project UUID
            workflow_id: Workflow UUID
            status: New status (running, paused, completed, failed, cancelled)
            message: Status message
        """
        await self.broadcast_to_project(project_id, {
            "type": "status",
            "project_id": project_id,
            "workflow_id": workflow_id,
            "status": status,
            "message": message
        })
    
    async def send_error_notification(
        self,
        project_id: str,
        workflow_id: str,
        error_message: str,
        phase: str = None,
        agent: str = None
    ):
        """
        Send error notification.
        
        Args:
            project_id: Project UUID
            workflow_id: Workflow UUID
            error_message: Error message
            phase: Phase where error occurred (optional)
            agent: Agent where error occurred (optional)
        """
        await self.broadcast_to_project(project_id, {
            "type": "error",
            "project_id": project_id,
            "workflow_id": workflow_id,
            "error_message": error_message,
            "phase": phase,
            "agent": agent
        })
    
    def get_connection_count(self, project_id: str = None) -> int:
        """
        Get number of active connections.
        
        Args:
            project_id: Optional project UUID to get count for specific project
            
        Returns:
            Number of active connections
        """
        if project_id:
            return len(self.active_connections.get(project_id, set()))
        
        return sum(len(conns) for conns in self.active_connections.values())
    
    def get_connected_projects(self) -> list[str]:
        """
        Get list of project IDs with active connections.
        
        Returns:
            List of project UUIDs
        """
        return list(self.active_connections.keys())

    async def start_redis_listener(self):
        """Start listening to Redis pub/sub channel for workflow updates."""
        try:
            self.redis_client = aioredis.from_url(settings.redis_url)
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe("workflow_updates")
            
            logger.info("Started Redis Pub/Sub listener for workflow updates")
            
            async def listen():
                try:
                    async for message in self.pubsub.listen():
                        if message["type"] == "message":
                            data = json.loads(message["data"])
                            project_id = data.get("project_id")
                            if project_id and project_id in self.active_connections:
                                await self.broadcast_to_project(project_id, data)
                except Exception as e:
                    logger.error(f"Error in Redis listener task: {e}")
            
            self.listener_task = asyncio.create_task(listen())
        except Exception as e:
            logger.error(f"Failed to start Redis listener: {e}")

    async def stop_redis_listener(self):
        """Stop the Redis listener."""
        if self.listener_task:
            self.listener_task.cancel()
        if self.pubsub:
            await self.pubsub.unsubscribe("workflow_updates")
        if self.redis_client:
            await self.redis_client.aclose()


# Global manager instance
manager = ConnectionManager()
