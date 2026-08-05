-- 001_init.sql — initial schema for GrowthPilot memory layer (T7)
--
-- Run once against an empty database:
--   psql "$DATABASE_URL" -f migrations/001_init.sql
--
-- Vector indexes are disabled by default in CockroachDB and must be
-- enabled at the cluster level before any VECTOR INDEX will build.
-- Requires admin privileges; safe to re-run.

SET CLUSTER SETTING feature.vector_index.enabled = true;

-- One row per founder/company. Every other table scopes to this.
CREATE TABLE IF NOT EXISTS companies (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        STRING NOT NULL,
    website     STRING,
    industry    STRING,
    description STRING,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- The memory layer. Five memory types share one table (see metadata JSONB
-- for type-specific fields). Vector index MUST be declared inline here —
-- adding one to a non-empty table blocks writes during backfill.
CREATE TABLE IF NOT EXISTS memories(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    memory_type STRING NOT NULL,
    content STRING NOT NULL,
    content_hash STRING NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    embedding VECTOR(1024),
    importance FLOAT NOT NULL DEFAULT 0.5,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_accessed_at TIMESTAMPTZ,
    access_count INT NOT NULL DEFAULT 0,

    VECTOR INDEX (company_id, embedding vector_cosine_ops),
    INDEX idx_company_type_time (company_id, memory_type, created_at DESC),
    UNIQUE INDEX idx_dedup (company_id, content_hash),
    CONSTRAINT chk_memory_type CHECK(
        memory_type IN ('episodic', 'semantic', 'user', 'task', 'reflection')
    ),
    CONSTRAINT chk_importance CHECK (importance >= 0.0 AND importance <= 1.0)
);

-- Agent-facing tables. Column sets are provisional pending Larry's input
-- on what the Planner / Content / Analytics agents actually read and write.
CREATE TABLE IF NOT EXISTS campaigns(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id  UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name        STRING NOT NULL,
    channel     STRING,
    status      STRING NOT NULL DEFAULT 'draft',
    started_at  TIMESTAMPTZ,
    ended_at    TIMESTAMPTZ,
    metadata    JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

    INDEX idx_campaigns_company_time (company_id, created_at DESC),

    CONSTRAINT chk_campaign_status CHECK (
        status IN ('draft', 'active', 'paused', 'completed')
    )
);

CREATE TABLE IF NOT EXISTS tasks (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    campaign_id  UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    agent        STRING,
    description  STRING NOT NULL,
    status       STRING NOT NULL DEFAULT 'pending',
    result       JSONB,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,

    INDEX idx_tasks_company_status (company_id, status, created_at DESC),

    CONSTRAINT chk_task_status CHECK (
        status IN ('pending', 'running', 'done', 'failed')
    )
);