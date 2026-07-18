# Spec: AI Storytelling Workspace v2.0 - Production System

## ASSUMPTIONS I'M MAKING

1. **Deployment**: Self-hosted Docker-based application (not SaaS)
2. **Database**: MySQL 8.0+ with phpMyAdmin for management
3. **AI Provider**: Mistral AI (text + Pixtral for images), OpenAI as fallback
4. **Users**: Single-user per instance for v2.0
5. **Frontend**: Next.js 14+ Web UI + enhanced CLI
6. **Real-time**: WebSocket for progress updates
7. **Storage**: MySQL for structured data, filesystem for images/manuscripts
8. **Docker**: All services containerized (API, Worker, Web, MySQL, phpMyAdmin, Redis, Nginx)

→ **Correct me now or I'll proceed with these assumptions.**

---

## Objective

Transform the MVP into a **production-ready AI-assisted book writing platform** that generates complete novels with real AI content, including text and visual elements (cover art, character portraits, scene illustrations).

### Target Users
- **Fiction Authors**: Writing 50K-150K word novels
- **Content Creators**: Producing long-form narratives with visuals
- **Power Users**: CLI automation and scripting

### User Stories

**As an author, I want to:**
1. Generate a complete 80K-word novel with AI assistance
2. See AI-generated cover art, character portraits, and scene illustrations
3. Edit and refine content at checkpoints
4. Pause and resume my workflow anytime
5. Export manuscripts in professional formats (TXT, DOCX, PDF)
6. Visualize my story structure (characters, plot, timeline)
7. Access phpMyAdmin to view/manage my story data

**As a power user, I want to:**
1. Use CLI for automated workflows
2. Customize AI prompts and agent behavior
3. Access raw Story Bible data
4. Monitor AI usage and costs
5. Query MySQL database directly

### Success Criteria

**Functional Requirements:**
- [ ] Generate complete 80K-word novels with Mistral AI
- [ ] Generate cover art using Mistral Pixtral Large
- [ ] Generate character portraits (3-5 main characters)
- [ ] Generate scene illustrations (1 per chapter)
- [ ] Support checkpoint editing (not just approve/abort)
- [ ] Enable workflow pause/resume with MySQL persistence
- [ ] Provide CLI and Web UI interfaces
- [ ] Export to TXT, DOCX, PDF formats
- [ ] Support concurrent chapter generation
- [ ] Access phpMyAdmin at http://localhost:8080

**Performance Requirements:**
- [ ] Agent execution: <5s (cached), <30s (fresh AI calls)
- [ ] Chapter generation: <60s per chapter
- [ ] Image generation: <30s per image (512x512)
- [ ] Full workflow: <45 minutes (10 chapters + images)
- [ ] API response: <200ms (p95, excluding AI)
- [ ] Web UI load: <2s (LCP)

**Quality Requirements:**
- [ ] Test coverage: 95%+
- [ ] Zero critical security vulnerabilities
- [ ] All AI calls logged with tokens/cost
- [ ] Error rate: <0.1%
- [ ] Graceful degradation on AI failures

---

## Tech Stack

### Core Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI 0.104+ (async API)
- **Database**: MySQL 8.0+ (InnoDB engine)
- **DB Management**: phpMyAdmin 5.2+
- **Cache**: Redis 7+ (AI responses, rate limiting)
- **Task Queue**: Celery 5+ with Redis backend
- **ORM**: SQLAlchemy 2.0+ (async) with aiomysql
- **Migrations**: Alembic

### AI Integration
- **Primary**: Mistral AI (1B tokens/month free)
  - Text: `mistral-large-latest`, `mistral-medium-latest`, `mistral-small-latest`
  - Image: `pixtral-large-latest` (multimodal)
  - Rate: ~1 RPS, 500K TPM
  - Context: 256K tokens
- **Fallback**: OpenAI (GPT-4o, DALL-E 3)

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **UI**: shadcn/ui + Tailwind CSS 3+
- **State**: Zustand 4+
- **Real-time**: Socket.IO (WebSocket)
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts (Story Bible viz)

### Infrastructure
- **Containers**: Docker 24+ + Docker Compose
- **Reverse Proxy**: Nginx (API + Web + phpMyAdmin)
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured JSON logs

---

## Commands

### Development

```bash
# Setup
make setup                    # Initial setup (venv, deps, Docker)
make dev                      # Start all services
make dev-api                  # Start API only
make dev-web                  # Start Web UI only
make dev-worker               # Start Celery worker

# Testing
make test                     # All tests with coverage
make test-unit                # Unit tests
make test-integration         # Integration tests
make test-e2e                 # End-to-end tests

# Code Quality
make lint                     # Run linters
make format                   # Auto-format
make typecheck                # Type checking
make security                 # Security audit

# Database
make db-migrate               # Run migrations
make db-rollback              # Rollback migration
make db-seed                  # Seed sample data
make db-reset                 # Reset database
make db-shell                 # MySQL shell
make db-admin                 # Open phpMyAdmin

# Docker
make docker-build             # Build containers
make docker-up                # Start containers
make docker-down              # Stop containers
make docker-logs              # View logs
make docker-shell             # Shell into API

# CLI
python -m storytelling_workspace \
  --project "My Novel" \
  --output ./output \
  --provider mistral \
  --generate-images

# API Server
uvicorn storytelling_workspace.api.main:app \
  --reload --host 0.0.0.0 --port 8000

# Web UI
cd web && npm run dev         # Dev server (port 3000)

# Workers
celery -A storytelling_workspace.workers worker \
  --loglevel=info --concurrency=4

# Production
make deploy                   # Deploy
make backup                   # Backup DB + images
make restore                  # Restore backup
```

---

## Project Structure

```
ai-storytelling-workspace/
├── src/storytelling_workspace/
│   ├── agents/                        # 15 AI agents
│   │   ├── base.py                    # Base with AI integration
│   │   ├── image_generator.py         # NEW: Pixtral image gen
│   │   └── ...                        # All 15 agents
│   ├── api/                           # FastAPI backend (NEW)
│   │   ├── main.py
│   │   ├── routes/                    # API endpoints
│   │   ├── schemas/                   # Pydantic models
│   │   └── websocket/                 # WebSocket handlers
│   ├── core/                          # Core logic (NEW)
│   │   ├── ai_provider.py             # AI abstraction
│   │   ├── image_provider.py          # Image generation
│   │   ├── rate_limiter.py
│   │   ├── cache.py
│   │   └── cost_tracker.py
│   ├── db/                            # Database layer (NEW)
│   │   ├── models/                    # SQLAlchemy models
│   │   ├── repositories/              # Data access
│   │   └── migrations/                # Alembic migrations
│   ├── workers/                       # Celery tasks (NEW)
│   │   ├── agent_tasks.py
│   │   ├── workflow_tasks.py
│   │   └── image_tasks.py
│   ├── services/                      # Business logic (NEW)
│   │   ├── project_service.py
│   │   ├── workflow_service.py
│   │   └── image_service.py
│   └── utils/                         # Utilities (NEW)
│       ├── prompts.py
│       └── image_prompts.py
├── web/                               # Next.js UI (NEW)
│   ├── app/                           # App router
│   │   ├── projects/
│   │   └── workflow/
│   ├── components/                    # React components
│   │   ├── ui/                        # shadcn/ui
│   │   ├── workflow/
│   │   ├── checkpoint/
│   │   └── images/
│   └── lib/                           # Utilities
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.worker
│   ├── Dockerfile.web
│   ├── Dockerfile.nginx
│   ├── docker-compose.yml             # Development
│   └── docker-compose.prod.yml        # Production
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── AI_INTEGRATION.md
├── scripts/
│   ├── setup.sh
│   ├── migrate.sh
│   └── backup.sh
├── .env.example
├── Makefile
├── pyproject.toml
└── README.md
```

---

## Code Style

### Python (Backend)

```python
"""Image Generator Agent using Mistral Pixtral."""

from typing import Dict, Any
from pathlib import Path
import structlog
from openai import OpenAI

from ..core.image_provider import ImageProvider
from ..core.retry import with_retry
from ..story_bible import StoryBible
from .base import BaseAgent

logger = structlog.get_logger()


class ImageGeneratorAgent(BaseAgent):
    """
    Generates visual assets using Mistral Pixtral Large.
    
    Creates:
    - Cover art (1024x1024)
    - Character portraits (512x512)
    - Scene illustrations (1024x512)
    """
    
    def __init__(self, image_provider: ImageProvider, output_dir: Path):
        super().__init__(name="Image Generator")
        self.image_provider = image_provider
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    @with_retry(max_attempts=3, backoff_factor=2)
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """Generate all story images."""
        self.log_start()
        
        images = {
            "cover_art": await self._generate_cover(bible),
            "portraits": await self._generate_portraits(bible),
            "scenes": await self._generate_scenes(bible)
        }
        
        bible.metadata["images"] = images
        self.record_changes(bible, images, "Generated all images")
        self.log_end(success=True)
        
        return {"success": True, "images": images}
    
    async def _generate_cover(self, bible: StoryBible) -> str:
        """Generate cover art."""
        prompt = f"""Professional book cover for {bible.brief.genre} novel.
        
Title: {bible.metadata.get('title', 'Untitled')}
Logline: {bible.concept.logline}
Theme: {bible.concept.theme}
Tone: {bible.brief.tone}

Style: Epic, cinematic, professional quality, dramatic lighting.
No text on cover."""
        
        response = await self.image_provider.generate(
            prompt=prompt,
            model="pixtral-large-latest",
            size="1024x1024"
        )
        
        path = self.output_dir / "cover_art.png"
        path.write_bytes(response.image_data)
        logger.info("cover_generated", path=str(path))
        
        return str(path)
```

### TypeScript (Frontend)

```typescript
// components/images/ImageGallery.tsx
"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Download, ZoomIn } from "lucide-react"

interface ImageGalleryProps {
  projectId: string
}

export function ImageGallery({ projectId }: ImageGalleryProps) {
  const [images, setImages] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchImages()
  }, [projectId])
  
  const fetchImages = async () => {
    const res = await fetch(`/api/projects/${projectId}/images`)
    const data = await res.json()
    setImages(data)
    setLoading(false)
  }
  
  if (loading) return <div>Loading...</div>
  
  return (
    <div className="space-y-8">
      {/* Cover Art */}
      {images.coverArt && (
        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4">Cover Art</h3>
          <div className="relative aspect-[2/3] max-w-md mx-auto">
            <Image
              src={images.coverArt}
              alt="Cover"
              fill
              className="object-cover rounded-lg"
            />
          </div>
        </Card>
      )}
      
      {/* Character Portraits */}
      <Card className="p-6">
        <h3 className="text-xl font-bold mb-4">Characters</h3>
        <div className="grid grid-cols-3 gap-4">
          {images.portraits.map((p: any) => (
            <div key={p.name} className="space-y-2">
              <div className="relative aspect-square">
                <Image
                  src={p.url}
                  alt={p.name}
                  fill
                  className="object-cover rounded-lg"
                />
              </div>
              <p className="text-sm text-center">{p.name}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
```

**Conventions:**
- Python: PEP 8, type hints, Google docstrings
- TypeScript: Prettier, ESLint, functional components
- Naming: snake_case (Python), camelCase (TS)
- Async: `async/await` everywhere
- Logging: Structured JSON with correlation IDs

---

## Testing Strategy

### Framework
- **Python**: pytest + pytest-asyncio + pytest-cov
- **TypeScript**: Vitest + React Testing Library
- **E2E**: Playwright

### Coverage
- **Overall**: 95%+
- **Critical**: 100% (AI, image gen, orchestrator)
- **UI**: 80%+

### Test Levels
- **Unit**: Pure functions, mocked AI
- **Integration**: Real AI (rate-limited), DB operations
- **E2E**: Full workflows (CLI + Web)

---

## Boundaries

### Always Do ✅
- Run tests before commits
- Use type hints everywhere
- Log all AI calls with cost
- Validate inputs at boundaries
- Cache AI responses (24h text, 7d images)
- Rate limit per-user
- Structured logging (JSON)
- Handle AI failures gracefully
- Version Story Bible changes
- Save checkpoints to MySQL
- Compress images before storage

### Ask First ⚠️
- Adding AI providers
- Database schema changes
- New dependencies
- Modifying agent prompts
- Changing rate limits
- Production deployment
- Checkpoint logic changes
- Image generation parameters

### Never Do ❌
- Commit secrets
- Skip tests
- Sync AI calls in API routes
- Store sensitive data in logs
- Bypass rate limiting
- Remove error handling
- Deploy without backup
- Modify Story Bible without versioning
- Generate images without consent
- Store uncompressed images

---

## Docker Architecture

### Services

```yaml
# docker-compose.yml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: storytelling-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: storytelling_workspace
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./docker/mysql/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - storytelling-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  phpmyadmin:
    image: phpmyadmin:5.2
    container_name: storytelling-phpmyadmin
    environment:
      PMA_HOST: mysql
      PMA_PORT: 3306
      PMA_USER: ${MYSQL_USER}
      PMA_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "8080:80"
    depends_on:
      mysql:
        condition: service_healthy
    networks:
      - storytelling-network

  redis:
    image: redis:7-alpine
    container_name: storytelling-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - storytelling-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    container_name: storytelling-api
    environment:
      DATABASE_URL: mysql+aiomysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mysql:3306/storytelling_workspace
      REDIS_URL: redis://redis:6379/0
      MISTRAL_API_KEY: ${MISTRAL_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
      - ./output:/app/output
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - storytelling-network
    command: uvicorn storytelling_workspace.api.main:app --host 0.0.0.0 --port 8000 --reload

  worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    container_name: storytelling-worker
    environment:
      DATABASE_URL: mysql+aiomysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mysql:3306/storytelling_workspace
      REDIS_URL: redis://redis:6379/0
      MISTRAL_API_KEY: ${MISTRAL_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    volumes:
      - ./src:/app/src
      - ./output:/app/output
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - storytelling-network
    command: celery -A storytelling_workspace.workers worker --loglevel=info --concurrency=4

  web:
    build:
      context: ./web
      dockerfile: ../docker/Dockerfile.web
    container_name: storytelling-web
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      - ./web:/app
      - /app/node_modules
    networks:
      - storytelling-network
    command: npm run dev

  nginx:
    image: nginx:alpine
    container_name: storytelling-nginx
    ports:
      - "80:80"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
      - web
      - phpmyadmin
    networks:
      - storytelling-network

volumes:
  mysql_data:
  redis_data:

networks:
  storytelling-network:
    driver: bridge
```

### Environment Variables

```bash
# .env.example
# MySQL
MYSQL_ROOT_PASSWORD=root_password_change_me
MYSQL_USER=storytelling_user
MYSQL_PASSWORD=storytelling_password_change_me
MYSQL_DATABASE=storytelling_workspace

# Redis
REDIS_URL=redis://redis:6379/0

# AI Providers
MISTRAL_API_KEY=your_mistral_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Application
SECRET_KEY=your_secret_key_change_me
ENVIRONMENT=development
LOG_LEVEL=INFO

# URLs
API_URL=http://localhost:8000
WEB_URL=http://localhost:3000
PHPMYADMIN_URL=http://localhost:8080
```

---

## Success Criteria

### Phase 1: AI Integration (Week 1-2)
- [ ] Mistral AI text generation working
- [ ] Mistral Pixtral image generation working
- [ ] OpenAI fallback functional
- [ ] Response caching implemented
- [ ] Cost tracking operational
- [ ] All 15 agents using real AI
- [ ] 95%+ test coverage maintained

### Phase 2: Database & Docker (Week 2-3)
- [ ] MySQL 8.0 container running
- [ ] phpMyAdmin accessible at :8080
- [ ] SQLAlchemy models created
- [ ] Alembic migrations working
- [ ] Redis cache operational
- [ ] All services in Docker Compose
- [ ] Health checks passing

### Phase 3: API & Workers (Week 3-4)
- [ ] FastAPI backend functional
- [ ] Celery workers processing tasks
- [ ] WebSocket real-time updates
- [ ] Project CRUD endpoints
- [ ] Workflow execution API
- [ ] Image generation API
- [ ] API tests passing

### Phase 4: Web UI (Week 4-5)
- [ ] Next.js app running
- [ ] Project management UI
- [ ] Workflow execution UI
- [ ] Checkpoint editing UI
- [ ] Image gallery functional
- [ ] Story Bible visualization
- [ ] Export functionality

### Phase 5: Integration & Testing (Week 5-6)
- [ ] End-to-end workflows working
- [ ] CLI + Web UI both functional
- [ ] All 154+ tests passing
- [ ] 97%+ code coverage
- [ ] Performance targets met
- [ ] Security audit passed
- [ ] Documentation complete

---

## Open Questions

1. **Image Generation Scope**: Cover + portraits + scenes (15-20 images)?
2. **Checkpoint Editing**: Text-only or full Story Bible editing?
3. **Parallel Execution**: Chapters + images in parallel?
4. **Export Priority**: DOCX first, then PDF?
5. **Cost Management**: Free tier only or user API keys?

**Recommendations**: Standard images, guided editing, parallel where safe, DOCX priority, free tier for v2.0

---

## Implementation Phases

### Phase 1: AI Integration (Week 1-2)
- Implement AI provider abstraction
- Integrate Mistral (text + Pixtral)
- Add OpenAI fallback
- Implement caching & rate limiting
- Update all 15 agents
- Add cost tracking
- Write AI integration tests

### Phase 2: Database & Docker (Week 2-3)
- Set up MySQL + phpMyAdmin containers
- Design database schema
- Create SQLAlchemy models
- Write Alembic migrations
- Set up Redis container
- Create Docker Compose config
- Test all services

### Phase 3: API & Workers (Week 3-4)
- Build FastAPI backend
- Implement Celery workers
- Add WebSocket support
- Create API endpoints
- Implement workflow orchestration
- Add image generation tasks
- Write API tests

### Phase 4: Web UI (Week 4-5)
- Set up Next.js project
- Build project management UI
- Create workflow execution UI
- Implement checkpoint editing
- Build image gallery
- Add Story Bible visualization
- Write UI tests

### Phase 5: Integration & Polish (Week 5-6)
- End-to-end testing
- Performance optimization
- Security hardening
- Documentation
- Deployment guide
- User guide

---

**Estimated Timeline**: 6 weeks
**Estimated Effort**: 200-250 hours
**Risk Level**: Medium (AI integration, async orchestration)

**Next Step**: Review spec → Create implementation plan → Begin Phase 1
