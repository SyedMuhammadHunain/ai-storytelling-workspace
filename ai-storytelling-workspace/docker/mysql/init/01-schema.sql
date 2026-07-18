-- AI Storytelling Workspace Database Schema
-- MySQL 8.0
-- Created: 2026-07-18

-- Set character set and collation
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Use the database
USE storytelling_workspace;

-- ============================================================================
-- Table: projects
-- Stores project metadata and configuration
-- ============================================================================
CREATE TABLE IF NOT EXISTS projects (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    name VARCHAR(255) NOT NULL,
    description TEXT,
    genre VARCHAR(100),
    target_length INT DEFAULT 80000 COMMENT 'Target word count',
    status ENUM('draft', 'in_progress', 'paused', 'completed', 'archived') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL COMMENT 'Soft delete timestamp',
    
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Project metadata and configuration';

-- ============================================================================
-- Table: story_bibles
-- Stores the complete Story Bible state as JSON with versioning
-- ============================================================================
CREATE TABLE IF NOT EXISTS story_bibles (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    project_id CHAR(36) NOT NULL,
    version INT NOT NULL DEFAULT 1 COMMENT 'Version number for rollback',
    
    -- Core Story Bible sections (JSON)
    brief JSON COMMENT 'Book brief and high-level concept',
    concept JSON COMMENT 'Detailed concept and themes',
    world_rules JSON COMMENT 'World building rules and constraints',
    characters JSON COMMENT 'Character profiles and relationships',
    locations JSON COMMENT 'Location descriptions',
    timeline JSON COMMENT 'Story timeline and events',
    plot_threads JSON COMMENT 'Plot threads and arcs',
    
    -- Metadata
    terminology JSON COMMENT 'Custom terminology and glossary',
    style_guide JSON COMMENT 'Writing style guidelines',
    metadata JSON COMMENT 'Additional metadata',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project_version (project_id, version),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Story Bible state with versioning';

-- ============================================================================
-- Table: chapters
-- Stores individual chapter data with content and metadata
-- ============================================================================
CREATE TABLE IF NOT EXISTS chapters (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    story_bible_id CHAR(36) NOT NULL,
    chapter_number INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    
    -- Chapter content
    content LONGTEXT COMMENT 'Full chapter text',
    summary TEXT COMMENT 'Chapter summary',
    pov VARCHAR(255) COMMENT 'Point of view character',
    
    -- Metadata
    word_count INT DEFAULT 0,
    target_word_count INT DEFAULT 3000,
    status ENUM('planned', 'in_progress', 'completed', 'revised') DEFAULT 'planned',
    
    -- Story structure
    goal TEXT COMMENT 'Chapter goal',
    conflict TEXT COMMENT 'Main conflict',
    resolution TEXT COMMENT 'Conflict resolution',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (story_bible_id) REFERENCES story_bibles(id) ON DELETE CASCADE,
    UNIQUE KEY unique_chapter (story_bible_id, chapter_number),
    INDEX idx_status (status),
    INDEX idx_chapter_number (chapter_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Chapter content and metadata';

-- ============================================================================
-- Table: checkpoints
-- Stores workflow checkpoints for user review and approval
-- ============================================================================
CREATE TABLE IF NOT EXISTS checkpoints (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    project_id CHAR(36) NOT NULL,
    story_bible_id CHAR(36) NOT NULL,
    
    -- Checkpoint metadata
    checkpoint_type ENUM('concept', 'characters', 'outline', 'chapter', 'final') NOT NULL,
    phase VARCHAR(100) NOT NULL COMMENT 'Workflow phase name',
    agent_name VARCHAR(255) NOT NULL COMMENT 'Agent that created checkpoint',
    
    -- Checkpoint state
    status ENUM('pending', 'approved', 'rejected', 'skipped') DEFAULT 'pending',
    
    -- Content snapshot (JSON)
    content JSON NOT NULL COMMENT 'Checkpoint content snapshot',
    changes JSON COMMENT 'Changes made since last checkpoint',
    
    -- User feedback
    user_feedback TEXT,
    rejection_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP NULL COMMENT 'When user reviewed checkpoint',
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (story_bible_id) REFERENCES story_bibles(id) ON DELETE CASCADE,
    INDEX idx_project_status (project_id, status),
    INDEX idx_type (checkpoint_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Workflow checkpoints for user review';

-- ============================================================================
-- Table: images
-- Stores metadata for generated images (cover art, portraits, scenes)
-- ============================================================================
CREATE TABLE IF NOT EXISTS images (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    project_id CHAR(36) NOT NULL,
    story_bible_id CHAR(36) NOT NULL,
    
    -- Image metadata
    image_type ENUM('cover_art', 'character_portrait', 'scene_illustration') NOT NULL,
    file_path VARCHAR(500) NOT NULL COMMENT 'Relative path to image file',
    file_size INT NOT NULL COMMENT 'File size in bytes',
    
    -- Generation details
    prompt TEXT NOT NULL COMMENT 'Prompt used to generate image',
    model VARCHAR(100) NOT NULL COMMENT 'AI model used',
    provider VARCHAR(50) NOT NULL COMMENT 'AI provider (mistral, openai)',
    
    -- Image properties
    width INT NOT NULL,
    height INT NOT NULL,
    format VARCHAR(10) NOT NULL COMMENT 'Image format (png, jpg, webp)',
    
    -- Associated entity
    character_name VARCHAR(255) COMMENT 'For character portraits',
    chapter_number INT COMMENT 'For scene illustrations',
    
    -- Cost tracking
    generation_cost DECIMAL(10, 4) DEFAULT 0.0000 COMMENT 'Cost in USD',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (story_bible_id) REFERENCES story_bibles(id) ON DELETE CASCADE,
    INDEX idx_project_type (project_id, image_type),
    INDEX idx_character (character_name),
    INDEX idx_chapter (chapter_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Generated image metadata';

-- ============================================================================
-- Table: workflow_states
-- Tracks workflow execution state for pause/resume functionality
-- ============================================================================
CREATE TABLE IF NOT EXISTS workflow_states (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    project_id CHAR(36) NOT NULL,
    
    -- Workflow state
    current_phase VARCHAR(100) NOT NULL COMMENT 'Current workflow phase',
    current_agent VARCHAR(255) COMMENT 'Currently executing agent',
    status ENUM('running', 'paused', 'completed', 'failed', 'cancelled') DEFAULT 'running',
    
    -- Progress tracking
    total_steps INT NOT NULL COMMENT 'Total workflow steps',
    completed_steps INT DEFAULT 0,
    progress_percentage DECIMAL(5, 2) DEFAULT 0.00,
    
    -- State snapshot (JSON)
    state_data JSON COMMENT 'Workflow state for resume',
    
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Workflow execution state';

-- ============================================================================
-- Table: agent_deltas
-- Audit trail of all agent changes to Story Bible
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_deltas (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    story_bible_id CHAR(36) NOT NULL,
    
    -- Agent information
    agent_name VARCHAR(255) NOT NULL,
    agent_version VARCHAR(50) COMMENT 'Agent version for tracking',
    
    -- Change details
    changes JSON NOT NULL COMMENT 'Changes made by agent',
    summary TEXT COMMENT 'Human-readable summary',
    
    -- Metadata
    execution_time_ms INT COMMENT 'Agent execution time',
    tokens_used INT COMMENT 'Tokens consumed',
    cost DECIMAL(10, 4) DEFAULT 0.0000 COMMENT 'Cost in USD',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (story_bible_id) REFERENCES story_bibles(id) ON DELETE CASCADE,
    INDEX idx_story_bible (story_bible_id),
    INDEX idx_agent (agent_name),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Agent change audit trail';

-- ============================================================================
-- Table: api_costs
-- Tracks API usage and costs for billing and monitoring
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_costs (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    project_id CHAR(36) NOT NULL,
    
    -- API details
    provider VARCHAR(50) NOT NULL COMMENT 'mistral, openai',
    model VARCHAR(100) NOT NULL COMMENT 'Model name',
    api_type ENUM('text', 'image') NOT NULL,
    
    -- Usage metrics
    tokens_used INT COMMENT 'For text generation',
    images_generated INT COMMENT 'For image generation',
    cost DECIMAL(10, 4) NOT NULL COMMENT 'Cost in USD',
    
    -- Request details
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project_provider (project_id, provider),
    INDEX idx_created_at (created_at),
    INDEX idx_api_type (api_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='API usage and cost tracking';

-- ============================================================================
-- Initial Data (Optional)
-- ============================================================================

-- Insert a sample project for testing
-- INSERT INTO projects (id, name, description, genre, status)
-- VALUES (
--     UUID(),
--     'Sample Fantasy Novel',
--     'A test project for development',
--     'Fantasy',
--     'draft'
-- );

-- ============================================================================
-- Schema Version Tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS schema_version (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Schema version tracking';

INSERT INTO schema_version (version, description)
VALUES ('1.0.0', 'Initial schema with 8 core tables')
ON DUPLICATE KEY UPDATE applied_at = CURRENT_TIMESTAMP;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Show all tables
-- SHOW TABLES;

-- Show table structures
-- DESCRIBE projects;
-- DESCRIBE story_bibles;
-- DESCRIBE chapters;
-- DESCRIBE checkpoints;
-- DESCRIBE images;
-- DESCRIBE workflow_states;
-- DESCRIBE agent_deltas;
-- DESCRIBE api_costs;
