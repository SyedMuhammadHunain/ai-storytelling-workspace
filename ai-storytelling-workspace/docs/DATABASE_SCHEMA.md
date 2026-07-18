# Database Schema Design

## Overview

MySQL 8.0 database schema for AI Storytelling Workspace v2.0. Supports full workflow state persistence, Story Bible data, checkpoint management, and image metadata tracking.

## Design Principles

1. **Normalization**: 3NF for data integrity
2. **Performance**: Indexes on foreign keys and frequently queried columns
3. **Scalability**: Prepared for horizontal scaling with proper indexing
4. **Audit Trail**: Created/updated timestamps on all tables
5. **Soft Deletes**: Logical deletion with `deleted_at` column where needed

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│  projects   │──────<│ story_bibles │>──────│ checkpoints │
└─────────────┘       └──────────────┘       └─────────────┘
                             │
                    ┌────────┼────────┐
                    │        │        │
              ┌─────▼──┐ ┌──▼────┐ ┌─▼──────┐
              │chapters│ │images │ │workflow│
              └────────┘ └───────┘ └────────┘
```

## Tables

### 1. projects

Stores project metadata and configuration.

```sql
CREATE TABLE projects (
    id CHAR(36) PRIMARY KEY,  -- UUID
    name VARCHAR(255) NOT NULL,
    description TEXT,
    genre VARCHAR(100),
    target_length INT DEFAULT 80000,
    status ENUM('draft', 'in_progress', 'paused', 'completed', 'archived') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Indexes:**
- `idx_status`: Fast filtering by project status
- `idx_created_at`: Chronological sorting
- `idx_deleted_at`: Soft delete filtering

---

### 2. story_bibles

Stores the complete Story Bible state as JSON with versioning.

```sql
CREATE TABLE story_bibles (
    id CHAR(36) PRIMARY KEY,  -- UUID
    project_id CHAR(36) NOT NULL,
    version INT NOT NULL DEFAULT 1,
    
    -- Core Story Bible sections (JSON)
    brief JSON,
    concept JSON,
    world_rules JSON,
    characters JSON,
    locations JSON,
    timeline JSON,
    plot_threads JSON,
    
    -- Metadata
    terminology JSON,
    style_guide JSON,
    metadata JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project_version (project_id, version),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Design Notes:**
- JSON columns for flexible schema evolution
- Version tracking for rollback capability
- Cascade delete when project is deleted

---

### 3. chapters

Stores individual chapter data with content and metadata.

```sql
CREATE TABLE chapters (
    id CHAR(36) PRIMARY KEY,  -- UUID
    story_bible_id CHAR(36) NOT NULL,
    chapter_number INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    
    -- Chapter content
    content LONGTEXT,
    summary TEXT,
    pov VARCHAR(255),
    
    -- Metadata
    word_count INT DEFAULT 0,
    target_word_count INT DEFAULT 3000,
    status ENUM('planned', 'in_progress', 'completed', 'revised') DEFAULT 'planned',
    
    -- Story structure
    goal TEXT,
    conflict TEXT,
    resolution TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (story_bible_id) REFERENCES story_bibles(id) ON DELETE CASCADE,
    UNIQUE KEY unique_chapter (story_bible_id, chapter_number),
    INDEX idx_status (status),
    INDEX idx_chapter_number (chapter_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Indexes:**
- `unique_chapter`: Prevent duplicate chapter numbers per story bible
- `idx_status`: Filter by completion status
- `idx_chapter_number`: Ordered retrieval

---

### 4. checkpoints

Stores workflow checkpoints for user review and approval.

```sql
CREATE TABLE checkpoints (
    id CHAR(36) PRIMARY KEY,  -- UUID
    project_id CHAR(36) NOT NULL,
    story_bible_id CHAR(36) NOT NULL,
    
    -- Checkpoint metadata
    checkpoint_type ENUM('concept', 'characters', 'outline', 'chapter', 'final') NOT NULL,
    phase VARCHAR(100) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    
    -- Checkpoint state
    status ENUM('pending', 'approved', 'rejected', 'skipped') DEFAULT 'pending',
    
    -- Content snapshot (JSON)
    content JSON NOT NULL,
    changes JSON,
    
    -- User feedback
    user_feedback TEXT,
    rejection_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP NULL,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (story_bible_id) REFERENCES story_bibles(id) ON DELETE CASCADE,
    INDEX idx_project_status (project_id, status),
    INDEX idx_type (checkpoint_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Design Notes:**
- Captures state at critical workflow points
- Stores user feedback for rejected checkpoints
- JSON content for flexibility

---

### 5. images

Stores metadata for generated images (cover art, portraits, scenes).

```sql
CREATE TABLE images (
    id CHAR(36) PRIMARY KEY,  -- UUID
    project_id CHAR(36) NOT NULL,
    story_bible_id CHAR(36) NOT NULL,
    
    -- Image metadata
    image_type ENUM('cover_art', 'character_portrait', 'scene_illustration') NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT NOT NULL,  -- bytes
    
    -- Generation details
    prompt TEXT NOT NULL,
    model VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    
    -- Image properties
    width INT NOT NULL,
    height INT NOT NULL,
    format VARCHAR(10) NOT NULL,  -- png, jpg, webp
    
    -- Associated entity
    character_name VARCHAR(255),  -- for portraits
    chapter_number INT,  -- for scene illustrations
    
    -- Cost tracking
    generation_cost DECIMAL(10, 4) DEFAULT 0.0000,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (story_bible_id) REFERENCES story_bibles(id) ON DELETE CASCADE,
    INDEX idx_project_type (project_id, image_type),
    INDEX idx_character (character_name),
    INDEX idx_chapter (chapter_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Indexes:**
- `idx_project_type`: Fast filtering by image type
- `idx_character`: Quick lookup of character portraits
- `idx_chapter`: Quick lookup of scene illustrations

---

### 6. workflow_states

Tracks workflow execution state for pause/resume functionality.

```sql
CREATE TABLE workflow_states (
    id CHAR(36) PRIMARY KEY,  -- UUID
    project_id CHAR(36) NOT NULL,
    
    -- Workflow state
    current_phase VARCHAR(100) NOT NULL,
    current_agent VARCHAR(255),
    status ENUM('running', 'paused', 'completed', 'failed', 'cancelled') DEFAULT 'running',
    
    -- Progress tracking
    total_steps INT NOT NULL,
    completed_steps INT DEFAULT 0,
    progress_percentage DECIMAL(5, 2) DEFAULT 0.00,
    
    -- State snapshot (JSON)
    state_data JSON,
    
    -- Error tracking
    error_message TEXT,
    error_stack TEXT,
    
    -- Timing
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paused_at TIMESTAMP NULL,
    resumed_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project_status (project_id, status),
    INDEX idx_started_at (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Design Notes:**
- Enables pause/resume of long-running workflows
- Tracks progress for UI updates
- Stores error information for debugging

---

### 7. agent_deltas

Audit trail of all agent changes to Story Bible.

```sql
CREATE TABLE agent_deltas (
    id CHAR(36) PRIMARY KEY,  -- UUID
    story_bible_id CHAR(36) NOT NULL,
    
    -- Agent information
    agent_name VARCHAR(255) NOT NULL,
    agent_version VARCHAR(50),
    
    -- Change details
    changes JSON NOT NULL,
    summary TEXT,
    
    -- Metadata
    execution_time_ms INT,
    tokens_used INT,
    cost DECIMAL(10, 4) DEFAULT 0.0000,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (story_bible_id) REFERENCES story_bibles(id) ON DELETE CASCADE,
    INDEX idx_story_bible (story_bible_id),
    INDEX idx_agent (agent_name),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Design Notes:**
- Complete audit trail of AI agent actions
- Cost tracking per agent execution
- Performance metrics for optimization

---

### 8. api_costs

Tracks API usage and costs for billing and monitoring.

```sql
CREATE TABLE api_costs (
    id CHAR(36) PRIMARY KEY,  -- UUID
    project_id CHAR(36) NOT NULL,
    
    -- API details
    provider VARCHAR(50) NOT NULL,  -- mistral, openai
    model VARCHAR(100) NOT NULL,
    api_type ENUM('text', 'image') NOT NULL,
    
    -- Usage metrics
    tokens_used INT,
    images_generated INT,
    cost DECIMAL(10, 4) NOT NULL,
    
    -- Request details
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project_provider (project_id, provider),
    INDEX idx_created_at (created_at),
    INDEX idx_api_type (api_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Design Notes:**
- Granular cost tracking per API call
- Supports billing and usage analytics
- Error tracking for failed requests

---

## Relationships

1. **projects → story_bibles**: One-to-Many (versioned)
2. **story_bibles → chapters**: One-to-Many
3. **projects → checkpoints**: One-to-Many
4. **projects → images**: One-to-Many
5. **projects → workflow_states**: One-to-Many
6. **story_bibles → agent_deltas**: One-to-Many
7. **projects → api_costs**: One-to-Many

## Data Types

- **CHAR(36)**: UUID primary keys for distributed systems
- **JSON**: Flexible schema for evolving data structures
- **ENUM**: Type-safe status fields
- **DECIMAL(10,4)**: Precise cost tracking (up to $999,999.9999)
- **LONGTEXT**: Chapter content (up to 4GB)
- **TIMESTAMP**: UTC timestamps with automatic updates

## Performance Considerations

### Indexes

All foreign keys are indexed for join performance. Additional indexes on:
- Status fields for filtering
- Timestamp fields for sorting
- Composite indexes for common query patterns

### Query Optimization

1. **Story Bible Retrieval**: Single query with JSON columns
2. **Chapter Listing**: Indexed by chapter_number
3. **Checkpoint Filtering**: Composite index on (project_id, status)
4. **Image Lookup**: Composite index on (project_id, image_type)

### Scaling Strategy

1. **Read Replicas**: For analytics and reporting
2. **Partitioning**: By project_id for large deployments
3. **Caching**: Redis for frequently accessed Story Bibles
4. **Archive**: Move completed projects to cold storage

## Migration Strategy

1. **Initial Schema**: Create all tables with indexes
2. **Seed Data**: Insert default values and test data
3. **Versioning**: Alembic migrations for schema changes
4. **Rollback**: Down migrations for each change

## Security

1. **No Sensitive Data**: API keys stored in environment variables
2. **Soft Deletes**: Preserve data for audit trail
3. **Foreign Key Constraints**: Maintain referential integrity
4. **UTF-8 Support**: Full Unicode support for international content

## Backup Strategy

1. **Daily Backups**: Full database backup
2. **Point-in-Time Recovery**: Binary log enabled
3. **Retention**: 30 days for production
4. **Testing**: Regular restore testing

## Monitoring

Track these metrics:
- Table sizes and growth rate
- Query performance (slow query log)
- Index usage statistics
- Connection pool utilization
- Replication lag (if using replicas)
