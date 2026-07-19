# Architecture Overview

## High-Level Architecture

The AI Storytelling Workspace uses a distributed, decoupled architecture to handle long-running AI generation tasks while maintaining a responsive user interface.

### System Components

1. **Web Frontend (Angular v22)**
   - Manages user interactions, project state, and real-time updates.
   - Communicates with the backend via REST API and WebSockets.
   - Built with Angular Material for a consistent, accessible UI.

2. **API Backend (FastAPI)**
   - Serves as the central entry point for all client requests.
   - Manages CRUD operations for Projects, Workflows, Checkpoints, and Story Bibles.
   - Enqueues heavy AI tasks to the Celery broker.
   - Pushes real-time status updates back to the UI via WebSockets.

3. **Task Workers (Celery)**
   - Orchestrates the 18 specialized AI agents.
   - Processes tasks from 4 dedicated queues (agent_tasks, workflow_tasks, image_tasks, default).
   - Manages retries, rate limiting, and state persistence during generation.

4. **Data Layer**
   - **MySQL 8.0**: Primary persistence for Projects, Workflow State, Checkpoints, and Story metadata.
   - **Redis**: Acts as the message broker for Celery and caching layer for AI responses.

## Agent Orchestration

The core value of the workspace lies in the orchestration of 18 distinct AI agents. They operate in a pipeline:

1. **Idea & Outlining Agents**: Generate the core premise, plot points, and chapter outlines.
2. **World-building Agents**: Construct the Story Bible, detailing characters, lore, and settings.
3. **Drafting Agents**: Write the actual prose chapter by chapter based on the outline and Story Bible.
4. **Review & Editing Agents**: Polish the prose, checking for consistency and tone.
5. **Visual Agents**: Generate cover art, character portraits, and scene illustrations via Pixtral.

## Data Flow

1. User initiates a "Start Workflow" request via the Angular UI.
2. FastAPI creates a Workflow record in MySQL and pushes a task to Redis.
3. Celery Worker picks up the task, invokes the necessary AI Agents.
4. AI Provider Layer handles API calls to Mistral/Pixtral (caching, rate-limiting, cost tracking).
5. Worker updates the Workflow state in MySQL and emits a WebSocket event.
6. FastAPI relays the WebSocket event to the Angular UI.
7. Angular UI updates the progress bar and displays generated content.

## Design Decisions

- **Why FastAPI?** Excellent async support, Pydantic validation, and high performance for WebSocket handling.
- **Why Celery?** AI tasks take seconds to minutes. Synchronous requests would timeout. Celery ensures durability and retry mechanisms.
- **Why Angular v22?** Offers robust state management, RxJS for seamless WebSocket handling, and a strict TypeScript environment for complex UI logic.
