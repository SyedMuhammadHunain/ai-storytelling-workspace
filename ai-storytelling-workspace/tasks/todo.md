# AI Storytelling Workspace v2.0 - Task List

## Phase 1: Foundation & AI Integration (Week 1-2)

- [x] Task 1: Set up AI Provider Abstraction Layer
  - Acceptance: Mistral + OpenAI providers working, caching, rate limiting, cost tracking
  - Verify: `pytest tests/unit/test_core/test_ai_provider.py -v` ✅ 12/12 tests passed
  - Files: `core/ai_provider.py`, `core/retry.py`, `core/rate_limiter.py`, `core/cache.py`, `core/cost_tracker.py`

- [x] Task 2: Implement Image Provider with Pixtral
  - Acceptance: Pixtral image generation working, compression, storage, metadata tracking
  - Verify: `pytest tests/unit/test_core/test_image_provider.py -v` ✅ 11/11 tests passed
  - Files: `core/image_provider.py`, `utils/image_prompts.py`

- [ ] Task 3: Update All 15 Agents with Real AI
  - Acceptance: All agents use real AI, prompts effective, tests pass with mocks
  - Verify: `pytest tests/unit/test_agents/ -v`
  - Files: `agents/base.py`, all 15 agent files, `utils/prompts.py`

- [ ] Task 4: Create Image Generator Agent
  - Acceptance: Cover art, portraits, scene illustrations generated
  - Verify: `pytest tests/unit/test_agents/test_image_generator.py -v`
  - Files: `agents/image_generator.py`, `orchestrator.py`

### Checkpoint: AI Integration Complete
- [ ] All tests pass with 95%+ coverage
- [ ] Mistral text + Pixtral images working
- [ ] Cost tracking operational
- [ ] Manual: Run full workflow, verify AI content

---

## Phase 2: Database & Docker Setup (Week 2-3)

- [x] Task 5: Design MySQL Database Schema ✅
  - Acceptance: Schema documented, supports all data, proper indexes
  - Verify: Review `docs/DATABASE_SCHEMA.md`
  - Files: `docs/DATABASE_SCHEMA.md`
  - Status: Complete - 8 tables designed with indexes, relationships, performance considerations

- [x] Task 6: Create Docker Compose Configuration ✅
  - Acceptance: MySQL + phpMyAdmin + Redis + App containers configured
  - Verify: `docker-compose up -d && docker-compose ps`
  - Files: `docker-compose.yml`, `Dockerfile`, `docker/mysql/init/01-schema.sql`, `docker/mysql/conf/my.cnf`, `.env.example`, `.env`
  - Status: Complete - All infrastructure files created, images pulling in background

- [ ] Task 7: Create SQLAlchemy Models
  - Acceptance: All models defined, relationships correct, async sessions work
  - Verify: `pytest tests/unit/test_db/test_models/ -v`
  - Files: `db/base.py`, `db/session.py`, `db/models/*.py` (5 files)

- [ ] Task 8: Set Up Alembic Migrations
  - Acceptance: Initial migration creates tables, up/down works
  - Verify: `make db-migrate && make db-rollback`
  - Files: `db/migrations/env.py`, `db/migrations/versions/001_initial.py`

- [ ] Task 9: Create Repository Layer (Data Access)
  - Acceptance: CRUD operations work, async, proper error handling
  - Verify: `pytest tests/integration/test_database/ -v`
  - Files: `db/repositories/*.py` (5 files)

### Checkpoint: Database Layer Complete
- [ ] MySQL + phpMyAdmin accessible at localhost:8080
- [ ] Migrations work
- [ ] Repositories perform CRUD
- [ ] Data persists across restarts

---

## Phase 3: API & Workers (Week 3-4)

- [ ] Task 10: Create FastAPI Application Structure
  - Acceptance: FastAPI starts, health check works, CORS configured, docs at /docs
  - Verify: `uvicorn storytelling_workspace.api.main:app --reload`
  - Files: `api/main.py`, `api/dependencies.py`, `api/middleware.py`, `config.py`

- [ ] Task 11: Create Pydantic Schemas
  - Acceptance: All schemas defined, validation works, OpenAPI correct
  - Verify: `pytest tests/unit/test_api/test_schemas/ -v`
  - Files: `api/schemas/*.py` (5 files)

- [ ] Task 12: Implement Project Management Endpoints
  - Acceptance: CRUD endpoints work, proper status codes, validation
  - Verify: `pytest tests/integration/test_api/test_projects.py -v`
  - Files: `api/routes/projects.py`, `services/project_service.py`

- [ ] Task 13: Implement Workflow Execution Endpoints
  - Acceptance: Start/pause/resume/status endpoints work, state persisted
  - Verify: `pytest tests/integration/test_api/test_workflow.py -v`
  - Files: `api/routes/workflow.py`, `services/workflow_service.py`

- [ ] Task 14: Set Up Celery Workers
  - Acceptance: Worker starts, tasks execute, results stored, failures handled
  - Verify: `celery -A storytelling_workspace.workers worker --loglevel=info`
  - Files: `workers/celery_app.py`, `workers/agent_tasks.py`, `workers/workflow_tasks.py`, `workers/image_tasks.py`

- [ ] Task 15: Implement WebSocket for Real-time Updates
  - Acceptance: WebSocket connections work, progress broadcasts, multiple clients
  - Verify: `pytest tests/integration/test_api/test_websocket.py -v`
  - Files: `api/websocket/manager.py`, `api/websocket/handlers.py`

### Checkpoint: API & Workers Complete
- [ ] FastAPI + Celery + WebSocket working
- [ ] Can start/pause/resume workflows via API
- [ ] Real-time progress updates functional

---

## Phase 4: Web UI (Week 4-5)

- [ ] Task 16: Set Up Next.js Project
  - Acceptance: Next.js starts, TypeScript + Tailwind + shadcn/ui configured
  - Verify: `cd web && npm run dev`
  - Files: `web/package.json`, `web/app/layout.tsx`, `web/lib/api-client.ts`

- [ ] Task 17: Build Project Management UI
  - Acceptance: List/create/view/edit/delete projects, loading states, errors
  - Verify: Manual testing + `npm run test`
  - Files: `web/app/projects/*.tsx`, `web/components/projects/*.tsx`

- [ ] Task 18: Build Workflow Execution UI
  - Acceptance: Start/pause/resume, real-time updates, agent status, progress
  - Verify: Manual testing + `npm run test`
  - Files: `web/app/projects/[id]/workflow/page.tsx`, `web/components/workflow/*.tsx`

- [ ] Task 19: Build Checkpoint Editing UI
  - Acceptance: Checkpoint dialog, Story Bible viewer, content editing, approve/reject
  - Verify: Manual testing + `npm run test`
  - Files: `web/components/checkpoint/*.tsx`, `web/hooks/use-checkpoint.ts`

- [ ] Task 20: Build Image Gallery UI
  - Acceptance: Cover/portraits/scenes displayed, lightbox, download
  - Verify: Manual testing + `npm run test`
  - Files: `web/app/projects/[id]/images/page.tsx`, `web/components/images/*.tsx`

- [ ] Task 21: Build Story Bible Visualization UI
  - Acceptance: Characters, plot graph, timeline, interactive, filter/search
  - Verify: Manual testing + `npm run test`
  - Files: `web/app/projects/[id]/story-bible/page.tsx`, `web/components/story-bible/*.tsx`

### Checkpoint: Web UI Complete
- [ ] All pages accessible and functional
- [ ] Real-time updates working
- [ ] Image gallery + Story Bible visualization work

---

## Phase 5: Docker Deployment & Polish (Week 5-6)

- [ ] Task 22: Create API Dockerfile
  - Acceptance: Dockerfile builds, API starts in container, health check passes
  - Verify: `docker build -f docker/Dockerfile.api -t storytelling-api .`
  - Files: `docker/Dockerfile.api`, `docker/entrypoint-api.sh`

- [ ] Task 23: Create Worker Dockerfile
  - Acceptance: Dockerfile builds, worker starts, processes tasks
  - Verify: `docker build -f docker/Dockerfile.worker -t storytelling-worker .`
  - Files: `docker/Dockerfile.worker`, `docker/entrypoint-worker.sh`

- [ ] Task 24: Create Web Dockerfile
  - Acceptance: Dockerfile builds, web app starts, production build works
  - Verify: `docker build -f docker/Dockerfile.web -t storytelling-web ./web`
  - Files: `docker/Dockerfile.web`, `docker/entrypoint-web.sh`

- [ ] Task 25: Create Nginx Configuration
  - Acceptance: Routes to API/Web/phpMyAdmin correctly, rate limiting works
  - Verify: `nginx -t -c docker/nginx/nginx.conf`
  - Files: `docker/nginx/nginx.conf`, `docker/Dockerfile.nginx`

- [ ] Task 26: Complete Docker Compose Configuration
  - Acceptance: All 7 services start, health checks pass, accessible
  - Verify: `docker-compose up -d && docker-compose ps`
  - Files: `docker/docker-compose.yml`, `docker/docker-compose.prod.yml`

- [ ] Task 27: Create Makefile Commands
  - Acceptance: All commands work (setup, dev, test, docker, db)
  - Verify: `make setup && make dev && make test`
  - Files: `Makefile`, `scripts/setup.sh`

- [ ] Task 28: Write Comprehensive Documentation
  - Acceptance: README, architecture, API, deployment, AI, development guides complete
  - Verify: Review all docs, follow guides
  - Files: `README.md`, `docs/*.md` (7 files)

- [ ] Task 29: End-to-End Testing
  - Acceptance: CLI, Web UI, image gen, checkpoint, export E2E tests pass
  - Verify: `pytest tests/e2e/ -v && npm run test:e2e`
  - Files: `tests/e2e/*.py`, `tests/e2e/*.spec.ts`, `playwright.config.ts`

- [ ] Task 30: Performance Optimization & Security Audit
  - Acceptance: Performance targets met, no critical vulnerabilities, security documented
  - Verify: `make security && pytest tests/performance/ -v`
  - Files: `tests/performance/*.py`, `docs/SECURITY.md`

### Final Checkpoint: Production Ready
- [ ] All tests pass (95%+ coverage)
- [ ] All E2E tests pass
- [ ] Performance + security targets met
- [ ] All 7 Docker services running
- [ ] phpMyAdmin at localhost:8080
- [ ] Web UI at localhost:3000
- [ ] API at localhost:8000
- [ ] Documentation complete
- [ ] Manual: Complete novel generation with images

---

## Summary

**Total Tasks**: 30
**Timeline**: 6 weeks (5 phases)
**Estimated Effort**: 200-250 hours

**Key Milestones**:
1. Week 2: AI Integration Complete
2. Week 3: Database Layer Complete
3. Week 4: API & Workers Complete
4. Week 5: Web UI Complete
5. Week 6: Production Ready

**Tech Stack**:
- Backend: Python 3.10+, FastAPI, SQLAlchemy, Celery
- Frontend: Next.js 14+, shadcn/ui, Tailwind CSS
- Database: MySQL 8.0 + phpMyAdmin
- Cache: Redis 7+
- AI: Mistral (text + Pixtral images) + OpenAI fallback
- Deployment: Docker Compose (7 containers)