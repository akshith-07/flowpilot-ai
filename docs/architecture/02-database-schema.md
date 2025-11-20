# FlowPilot AI - Complete Database Schema

## Overview

This document defines the complete database schema for FlowPilot AI, including all 40+ tables, relationships, indexes, constraints, and partitioning strategies.

**Database:** PostgreSQL 15+
**Total Tables:** 42
**Extensions Required:**
- `uuid-ossp` (UUID generation)
- `pgcrypto` (encryption functions)
- `pg_trgm` (trigram matching for fuzzy search)
- `btree_gin` (multi-column GIN indexes)
- `pgvector` (vector similarity search)

---

## Table of Contents

1. [Users & Authentication](#1-users--authentication) (5 tables)
2. [Organizations & Multi-Tenancy](#2-organizations--multi-tenancy) (6 tables)
3. [Workflows](#3-workflows) (5 tables)
4. [Executions](#4-executions) (4 tables)
5. [AI Engine](#5-ai-engine) (3 tables)
6. [Connectors](#6-connectors) (4 tables)
7. [Documents](#7-documents) (4 tables)
8. [Notifications](#8-notifications) (3 tables)
9. [Analytics](#9-analytics) (3 tables)
10. [Billing](#10-billing) (3 tables)
11. [Admin & Settings](#11-admin--settings) (2 tables)

---

## Database Configuration

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Set default timezone
SET timezone = 'UTC';
```

---

## 1. Users & Authentication

### 1.1 users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    phone_number VARCHAR(20),
    phone_verified BOOLEAN DEFAULT FALSE,
    avatar_url VARCHAR(500),
    timezone VARCHAR(50) DEFAULT 'UTC',
    locale VARCHAR(10) DEFAULT 'en',
    last_login TIMESTAMPTZ,
    password_changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT email_lowercase CHECK (email = LOWER(email))
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_email_verified ON users(email_verified) WHERE email_verified = FALSE;
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Full-text search on names
CREATE INDEX idx_users_name_fts ON users USING GIN (to_tsvector('english', first_name || ' ' || last_name));

-- Comments
COMMENT ON TABLE users IS 'Core user accounts';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password';
COMMENT ON COLUMN users.email_verification_token IS 'Token for email verification (nullable after verification)';
```

### 1.2 user_sessions

```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    device_name VARCHAR(255),
    device_type VARCHAR(50), -- 'web', 'mobile', 'desktop'
    browser VARCHAR(100),
    os VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMPTZ NOT NULL,
    last_activity TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
);

-- Indexes
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token_hash ON user_sessions(refresh_token_hash);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at) WHERE is_active = TRUE;

-- Comments
COMMENT ON TABLE user_sessions IS 'Active user sessions with refresh tokens';
COMMENT ON COLUMN user_sessions.refresh_token_hash IS 'SHA256 hash of refresh token';
```

### 1.3 login_attempts

```sql
CREATE TABLE login_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(100), -- 'invalid_password', 'account_locked', 'mfa_failed'
    attempted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT failure_reason_required CHECK (
        (success = TRUE AND failure_reason IS NULL) OR
        (success = FALSE AND failure_reason IS NOT NULL)
    )
);

-- Indexes
CREATE INDEX idx_login_attempts_email_attempted ON login_attempts(email, attempted_at DESC);
CREATE INDEX idx_login_attempts_ip_attempted ON login_attempts(ip_address, attempted_at DESC);
CREATE INDEX idx_login_attempts_attempted_at ON login_attempts(attempted_at DESC);

-- Partitioning by month (for auto-cleanup)
-- Convert to partitioned table for production
-- Partitions auto-created monthly, old partitions dropped after 6 months

COMMENT ON TABLE login_attempts IS 'Login attempt tracking for security monitoring';
```

### 1.4 mfa_devices

```sql
CREATE TABLE mfa_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(20) DEFAULT 'totp', -- 'totp', 'sms', 'backup_codes'
    secret_encrypted TEXT NOT NULL, -- Encrypted TOTP secret or backup codes
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_active_totp_per_user UNIQUE (user_id, device_type)
        WHERE device_type = 'totp' AND is_active = TRUE
);

-- Indexes
CREATE INDEX idx_mfa_devices_user_id ON mfa_devices(user_id);

COMMENT ON TABLE mfa_devices IS 'Multi-factor authentication devices';
COMMENT ON COLUMN mfa_devices.secret_encrypted IS 'Encrypted with application secret key';
```

### 1.5 oauth_connections

```sql
CREATE TABLE oauth_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'google', 'microsoft', 'github', 'okta'
    provider_user_id VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    expires_at TIMESTAMPTZ,
    scopes TEXT[], -- Array of granted scopes
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_provider_user UNIQUE (provider, provider_user_id)
);

-- Indexes
CREATE INDEX idx_oauth_connections_user_id ON oauth_connections(user_id);
CREATE INDEX idx_oauth_connections_provider ON oauth_connections(provider);

COMMENT ON TABLE oauth_connections IS 'OAuth 2.0 connections for SSO';
```

---

## 2. Organizations & Multi-Tenancy

### 2.1 organizations

```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    parent_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    logo_url VARCHAR(500),
    website VARCHAR(255),
    industry VARCHAR(100), -- 'finance', 'healthcare', 'legal', etc.
    size VARCHAR(20), -- 'small', 'medium', 'large', 'enterprise'
    timezone VARCHAR(50) DEFAULT 'UTC',
    locale VARCHAR(10) DEFAULT 'en',
    settings JSONB DEFAULT '{}', -- Branding, features, etc.
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT slug_format CHECK (slug ~ '^[a-z0-9-]+$')
);

-- Indexes
CREATE INDEX idx_organizations_slug ON organizations(slug);
CREATE INDEX idx_organizations_parent_id ON organizations(parent_id);
CREATE INDEX idx_organizations_created_at ON organizations(created_at DESC);
CREATE INDEX idx_organizations_settings_gin ON organizations USING GIN (settings);

-- Full-text search
CREATE INDEX idx_organizations_name_fts ON organizations USING GIN (to_tsvector('english', name));

COMMENT ON TABLE organizations IS 'Multi-tenant organizations';
COMMENT ON COLUMN organizations.parent_id IS 'For hierarchical organizations (subsidiaries)';
```

### 2.2 organization_members

```sql
CREATE TABLE organization_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    department_id UUID REFERENCES departments(id) ON DELETE SET NULL,
    title VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMPTZ,

    CONSTRAINT unique_org_user UNIQUE (organization_id, user_id)
);

-- Indexes
CREATE INDEX idx_org_members_organization_id ON organization_members(organization_id);
CREATE INDEX idx_org_members_user_id ON organization_members(user_id);
CREATE INDEX idx_org_members_role_id ON organization_members(role_id);
CREATE INDEX idx_org_members_department_id ON organization_members(department_id);

COMMENT ON TABLE organization_members IS 'User membership in organizations';
```

### 2.3 roles

```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '{}', -- { "workflows": { "create": true, "update": true, ... }, ... }
    is_system_role BOOLEAN DEFAULT FALSE, -- 'owner', 'admin', 'member', 'viewer'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_role_slug_per_org UNIQUE (organization_id, slug),
    CONSTRAINT system_roles_no_org CHECK (
        (is_system_role = TRUE AND organization_id IS NULL) OR
        (is_system_role = FALSE AND organization_id IS NOT NULL)
    )
);

-- Indexes
CREATE INDEX idx_roles_organization_id ON roles(organization_id);
CREATE INDEX idx_roles_permissions_gin ON roles USING GIN (permissions);

COMMENT ON TABLE roles IS 'Role-based access control (RBAC)';
COMMENT ON COLUMN roles.is_system_role IS 'System roles are organization-independent';
```

### 2.4 invitations

```sql
CREATE TABLE invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    invited_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'accepted', 'expired', 'revoked'
    expires_at TIMESTAMPTZ NOT NULL,
    accepted_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_expiry CHECK (expires_at > created_at),
    CONSTRAINT accepted_requires_accepted_at CHECK (
        (status = 'accepted' AND accepted_at IS NOT NULL) OR
        (status != 'accepted')
    )
);

-- Indexes
CREATE INDEX idx_invitations_organization_id ON invitations(organization_id);
CREATE INDEX idx_invitations_email ON invitations(email);
CREATE INDEX idx_invitations_token ON invitations(token);
CREATE INDEX idx_invitations_status ON invitations(status);
CREATE INDEX idx_invitations_expires_at ON invitations(expires_at);

COMMENT ON TABLE invitations IS 'Organization invitations';
```

### 2.5 departments

```sql
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES departments(id) ON DELETE CASCADE,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_dept_name_per_org UNIQUE (organization_id, name)
);

-- Indexes
CREATE INDEX idx_departments_organization_id ON departments(organization_id);
CREATE INDEX idx_departments_parent_id ON departments(parent_id);

COMMENT ON TABLE departments IS 'Organizational departments/teams';
```

### 2.6 usage_quotas

```sql
CREATE TABLE usage_quotas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    resource_type VARCHAR(50) NOT NULL, -- 'workflows', 'executions', 'api_calls', 'ai_tokens', 'storage_gb'
    quota_limit BIGINT NOT NULL,
    quota_used BIGINT DEFAULT 0,
    quota_period VARCHAR(20) DEFAULT 'monthly', -- 'monthly', 'annual', 'unlimited'
    reset_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_org_resource UNIQUE (organization_id, resource_type),
    CONSTRAINT non_negative_quota CHECK (quota_limit >= 0 AND quota_used >= 0)
);

-- Indexes
CREATE INDEX idx_usage_quotas_organization_id ON usage_quotas(organization_id);
CREATE INDEX idx_usage_quotas_resource_type ON usage_quotas(resource_type);

COMMENT ON TABLE usage_quotas IS 'Per-tenant resource quotas';
```

---

## 3. Workflows

### 3.1 workflows

```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    definition JSONB NOT NULL, -- Workflow DAG definition
    version INTEGER DEFAULT 1,
    current_version_id UUID, -- Self-reference to workflow_versions
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'active', 'archived'
    category VARCHAR(50), -- 'ai', 'automation', 'integration', etc.
    tags TEXT[] DEFAULT '{}',
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    is_template BOOLEAN DEFAULT FALSE,
    template_source_id UUID REFERENCES workflows(id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_status CHECK (status IN ('draft', 'active', 'archived'))
);

-- Indexes
CREATE INDEX idx_workflows_organization_id ON workflows(organization_id);
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_created_by ON workflows(created_by);
CREATE INDEX idx_workflows_category ON workflows(category);
CREATE INDEX idx_workflows_tags_gin ON workflows USING GIN (tags);
CREATE INDEX idx_workflows_definition_gin ON workflows USING GIN (definition);
CREATE INDEX idx_workflows_created_at ON workflows(created_at DESC);

-- Full-text search
CREATE INDEX idx_workflows_name_desc_fts ON workflows USING GIN (
    to_tsvector('english', name || ' ' || COALESCE(description, ''))
);

-- Row-level security for multi-tenancy
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;

CREATE POLICY workflow_isolation_policy ON workflows
    USING (organization_id = current_setting('app.current_organization_id', TRUE)::uuid);

COMMENT ON TABLE workflows IS 'Workflow definitions and metadata';
```

### 3.2 workflow_versions

```sql
CREATE TABLE workflow_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    definition JSONB NOT NULL,
    changelog TEXT,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_workflow_version UNIQUE (workflow_id, version),
    CONSTRAINT positive_version CHECK (version > 0)
);

-- Indexes
CREATE INDEX idx_workflow_versions_workflow_id ON workflow_versions(workflow_id);
CREATE INDEX idx_workflow_versions_version ON workflow_versions(workflow_id, version DESC);

COMMENT ON TABLE workflow_versions IS 'Version history for workflows (git-like)';
```

### 3.3 workflow_templates

```sql
CREATE TABLE workflow_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    definition JSONB NOT NULL,
    preview_image_url VARCHAR(500),
    tags TEXT[] DEFAULT '{}',
    is_public BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_workflow_templates_category ON workflow_templates(category);
CREATE INDEX idx_workflow_templates_is_public ON workflow_templates(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_workflow_templates_usage_count ON workflow_templates(usage_count DESC);

COMMENT ON TABLE workflow_templates IS 'Pre-built workflow templates';
```

### 3.4 workflow_variables

```sql
CREATE TABLE workflow_variables (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    key VARCHAR(100) NOT NULL,
    value_encrypted TEXT,
    value_type VARCHAR(20) DEFAULT 'string', -- 'string', 'number', 'boolean', 'secret'
    is_secret BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_workflow_variable UNIQUE (workflow_id, key),
    CONSTRAINT secret_encrypted CHECK (
        (is_secret = TRUE AND value_encrypted IS NOT NULL) OR
        (is_secret = FALSE)
    )
);

-- Indexes
CREATE INDEX idx_workflow_variables_workflow_id ON workflow_variables(workflow_id);

COMMENT ON TABLE workflow_variables IS 'Workflow-specific variables';
```

### 3.5 workflow_triggers

```sql
CREATE TABLE workflow_triggers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    trigger_type VARCHAR(50) NOT NULL, -- 'manual', 'scheduled', 'webhook', 'event'
    config JSONB NOT NULL DEFAULT '{}', -- Cron expression, webhook URL, event filters
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_workflow_triggers_workflow_id ON workflow_triggers(workflow_id);
CREATE INDEX idx_workflow_triggers_type_active ON workflow_triggers(trigger_type, is_active);

COMMENT ON TABLE workflow_triggers IS 'Workflow execution triggers';
```

---

## 4. Executions

### 4.1 workflow_executions

```sql
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE RESTRICT,
    workflow_version_id UUID REFERENCES workflow_versions(id) ON DELETE SET NULL,
    triggered_by UUID REFERENCES users(id) ON DELETE SET NULL,
    trigger_type VARCHAR(50), -- 'manual', 'scheduled', 'webhook', 'event'
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER, -- Calculated: completed_at - started_at
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    CONSTRAINT completed_requires_times CHECK (
        (status IN ('completed', 'failed') AND started_at IS NOT NULL AND completed_at IS NOT NULL) OR
        (status NOT IN ('completed', 'failed'))
    )
) PARTITION BY RANGE (created_at);

-- Create monthly partitions (auto-managed by cron job)
CREATE TABLE workflow_executions_2024_01 PARTITION OF workflow_executions
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Indexes (on each partition)
CREATE INDEX idx_executions_organization_id ON workflow_executions(organization_id);
CREATE INDEX idx_executions_workflow_id ON workflow_executions(workflow_id);
CREATE INDEX idx_executions_status ON workflow_executions(status);
CREATE INDEX idx_executions_created_at ON workflow_executions(created_at DESC);
CREATE INDEX idx_executions_org_status_created ON workflow_executions(organization_id, status, created_at DESC);

-- Row-level security
ALTER TABLE workflow_executions ENABLE ROW LEVEL SECURITY;

CREATE POLICY execution_isolation_policy ON workflow_executions
    USING (organization_id = current_setting('app.current_organization_id', TRUE)::uuid);

COMMENT ON TABLE workflow_executions IS 'Workflow execution instances (partitioned by month)';
```

### 4.2 execution_steps

```sql
CREATE TABLE execution_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    step_name VARCHAR(255) NOT NULL,
    step_type VARCHAR(50) NOT NULL, -- 'ai_summarization', 'send_email', 'conditional', etc.
    step_order INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_execution_steps_execution_id ON execution_steps(execution_id);
CREATE INDEX idx_execution_steps_status ON execution_steps(status);
CREATE INDEX idx_execution_steps_order ON execution_steps(execution_id, step_order);

COMMENT ON TABLE execution_steps IS 'Individual steps within workflow executions';
```

### 4.3 execution_logs

```sql
CREATE TABLE execution_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    step_id UUID REFERENCES execution_steps(id) ON DELETE CASCADE,
    level VARCHAR(20) DEFAULT 'info', -- 'debug', 'info', 'warning', 'error'
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    logged_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (logged_at);

-- Create monthly partitions
CREATE TABLE execution_logs_2024_01 PARTITION OF execution_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Indexes
CREATE INDEX idx_execution_logs_execution_id ON execution_logs(execution_id);
CREATE INDEX idx_execution_logs_step_id ON execution_logs(step_id);
CREATE INDEX idx_execution_logs_level ON execution_logs(level);
CREATE INDEX idx_execution_logs_logged_at ON execution_logs(logged_at DESC);

COMMENT ON TABLE execution_logs IS 'Detailed execution logs (partitioned by month)';
```

### 4.4 ai_requests

```sql
CREATE TABLE ai_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    execution_id UUID REFERENCES workflow_executions(id) ON DELETE SET NULL,
    step_id UUID REFERENCES execution_steps(id) ON DELETE SET NULL,
    model VARCHAR(50) NOT NULL, -- 'gemini-1.5-pro', 'gemini-1.5-flash'
    prompt_text TEXT NOT NULL,
    prompt_tokens INTEGER,
    completion_text TEXT,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    temperature NUMERIC(3, 2),
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    latency_ms INTEGER,
    cost_usd NUMERIC(10, 6), -- Calculated based on pricing
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_ai_requests_organization_id ON ai_requests(organization_id);
CREATE INDEX idx_ai_requests_execution_id ON ai_requests(execution_id);
CREATE INDEX idx_ai_requests_created_at ON ai_requests(created_at DESC);
CREATE INDEX idx_ai_requests_model ON ai_requests(model);

COMMENT ON TABLE ai_requests IS 'AI API request tracking for billing and analytics';
```

---

## 5. AI Engine

### 5.1 prompt_templates

```sql
CREATE TABLE prompt_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    template_text TEXT NOT NULL, -- Jinja2 template
    variables JSONB DEFAULT '[]', -- ["user_input", "context", ...]
    model VARCHAR(50) DEFAULT 'gemini-1.5-flash',
    temperature NUMERIC(3, 2) DEFAULT 0.7,
    is_system_template BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_org_template_slug UNIQUE (organization_id, slug),
    CONSTRAINT system_templates_no_org CHECK (
        (is_system_template = TRUE AND organization_id IS NULL) OR
        (is_system_template = FALSE AND organization_id IS NOT NULL)
    )
);

-- Indexes
CREATE INDEX idx_prompt_templates_organization_id ON prompt_templates(organization_id);
CREATE INDEX idx_prompt_templates_slug ON prompt_templates(slug);

COMMENT ON TABLE prompt_templates IS 'Reusable AI prompt templates';
```

### 5.2 semantic_cache

```sql
CREATE TABLE semantic_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    prompt_hash VARCHAR(64) NOT NULL, -- SHA256 of normalized prompt
    prompt_embedding vector(768), -- Embedding vector for semantic similarity
    prompt_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    model VARCHAR(50) NOT NULL,
    hit_count INTEGER DEFAULT 1,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_org_prompt_hash UNIQUE (organization_id, prompt_hash)
);

-- Indexes
CREATE INDEX idx_semantic_cache_organization_id ON semantic_cache(organization_id);
CREATE INDEX idx_semantic_cache_prompt_hash ON semantic_cache(prompt_hash);
CREATE INDEX idx_semantic_cache_expires_at ON semantic_cache(expires_at);

-- Vector similarity index for semantic search
CREATE INDEX idx_semantic_cache_embedding ON semantic_cache
    USING ivfflat (prompt_embedding vector_cosine_ops);

COMMENT ON TABLE semantic_cache IS 'Semantic cache for AI responses';
```

### 5.3 ai_fine_tuning_jobs

```sql
CREATE TABLE ai_fine_tuning_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    base_model VARCHAR(50) NOT NULL,
    fine_tuned_model VARCHAR(100),
    training_data_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    provider_job_id VARCHAR(255),
    error_message TEXT,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_ai_fine_tuning_jobs_organization_id ON ai_fine_tuning_jobs(organization_id);
CREATE INDEX idx_ai_fine_tuning_jobs_status ON ai_fine_tuning_jobs(status);

COMMENT ON TABLE ai_fine_tuning_jobs IS 'Fine-tuning jobs for custom AI models';
```

---

## 6. Connectors

### 6.1 connectors

```sql
CREATE TABLE connectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'gmail', 'slack', 'salesforce', etc.
    name VARCHAR(255) NOT NULL,
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    connected_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_org_provider_name UNIQUE (organization_id, provider, name)
);

-- Indexes
CREATE INDEX idx_connectors_organization_id ON connectors(organization_id);
CREATE INDEX idx_connectors_provider ON connectors(provider);
CREATE INDEX idx_connectors_is_active ON connectors(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE connectors IS 'Third-party integrations';
```

### 6.2 connector_credentials

```sql
CREATE TABLE connector_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connector_id UUID NOT NULL REFERENCES connectors(id) ON DELETE CASCADE,
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    expires_at TIMESTAMPTZ,
    scopes TEXT[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_connector_credentials_connector_id ON connector_credentials(connector_id);
CREATE INDEX idx_connector_credentials_expires_at ON connector_credentials(expires_at);

COMMENT ON TABLE connector_credentials IS 'Encrypted OAuth credentials';
```

### 6.3 connector_webhooks

```sql
CREATE TABLE connector_webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connector_id UUID NOT NULL REFERENCES connectors(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    webhook_url VARCHAR(500) NOT NULL,
    secret VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    provider_webhook_id VARCHAR(255), -- ID from provider
    last_triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_connector_webhooks_connector_id ON connector_webhooks(connector_id);
CREATE INDEX idx_connector_webhooks_event_type ON connector_webhooks(event_type);

COMMENT ON TABLE connector_webhooks IS 'Registered webhooks with third-party providers';
```

### 6.4 connector_sync_logs

```sql
CREATE TABLE connector_sync_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connector_id UUID NOT NULL REFERENCES connectors(id) ON DELETE CASCADE,
    sync_type VARCHAR(50) NOT NULL, -- 'full', 'incremental', 'webhook'
    status VARCHAR(20) DEFAULT 'pending',
    records_processed INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_connector_sync_logs_connector_id ON connector_sync_logs(connector_id);
CREATE INDEX idx_connector_sync_logs_started_at ON connector_sync_logs(started_at DESC);

COMMENT ON TABLE connector_sync_logs IS 'Connector sync history';
```

---

## 7. Documents

### 7.1 documents

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_hash VARCHAR(64) NOT NULL, -- SHA256 for deduplication
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    page_count INTEGER,
    uploaded_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_file_size CHECK (file_size > 0)
);

-- Indexes
CREATE INDEX idx_documents_organization_id ON documents(organization_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_file_hash ON documents(file_hash);
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

-- Full-text search on name
CREATE INDEX idx_documents_name_fts ON documents USING GIN (to_tsvector('english', name));

COMMENT ON TABLE documents IS 'Uploaded documents';
```

### 7.2 document_pages

```sql
CREATE TABLE document_pages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    content TEXT,
    ocr_confidence NUMERIC(5, 2), -- 0.00 to 100.00
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_document_page UNIQUE (document_id, page_number),
    CONSTRAINT positive_page_number CHECK (page_number > 0)
);

-- Indexes
CREATE INDEX idx_document_pages_document_id ON document_pages(document_id);
CREATE INDEX idx_document_pages_page_number ON document_pages(document_id, page_number);

-- Full-text search on content
CREATE INDEX idx_document_pages_content_fts ON document_pages USING GIN (to_tsvector('english', content));

COMMENT ON TABLE document_pages IS 'Individual pages with OCR text';
```

### 7.3 document_extractions

```sql
CREATE TABLE document_extractions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    extraction_type VARCHAR(50) NOT NULL, -- 'entities', 'tables', 'summary', 'classification'
    structured_data JSONB NOT NULL,
    confidence NUMERIC(5, 2),
    extracted_by VARCHAR(50) DEFAULT 'gemini-1.5-pro',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_document_extractions_document_id ON document_extractions(document_id);
CREATE INDEX idx_document_extractions_type ON document_extractions(extraction_type);
CREATE INDEX idx_document_extractions_data_gin ON document_extractions USING GIN (structured_data);

COMMENT ON TABLE document_extractions IS 'AI-extracted structured data';
```

### 7.4 document_embeddings

```sql
CREATE TABLE document_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_id UUID REFERENCES document_pages(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(768) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_page_chunk UNIQUE (page_id, chunk_index)
);

-- Indexes
CREATE INDEX idx_document_embeddings_document_id ON document_embeddings(document_id);
CREATE INDEX idx_document_embeddings_page_id ON document_embeddings(page_id);

-- Vector similarity index
CREATE INDEX idx_document_embeddings_vector ON document_embeddings
    USING ivfflat (embedding vector_cosine_ops);

COMMENT ON TABLE document_embeddings IS 'Vector embeddings for semantic search';
```

---

## 8. Notifications

### 8.1 notifications

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'workflow_completed', 'execution_failed', 'quota_exceeded', etc.
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    channel VARCHAR(20) NOT NULL, -- 'in_app', 'email', 'slack', 'sms'
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'sent', 'failed', 'read'
    sent_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_notifications_organization_id ON notifications(organization_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, read_at) WHERE read_at IS NULL;

COMMENT ON TABLE notifications IS 'Multi-channel notifications';
```

### 8.2 notification_preferences

```sql
CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    channels TEXT[] DEFAULT '{}', -- ['email', 'slack']
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_user_event UNIQUE (user_id, event_type)
);

-- Indexes
CREATE INDEX idx_notification_preferences_user_id ON notification_preferences(user_id);

COMMENT ON TABLE notification_preferences IS 'User notification preferences';
```

### 8.3 alert_rules

```sql
CREATE TABLE alert_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    condition JSONB NOT NULL, -- { "type": "error_rate", "threshold": 10, "window": "5m" }
    action JSONB NOT NULL, -- { "type": "notify", "channels": ["email", "slack"], "recipients": [...] }
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMPTZ,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_alert_rules_organization_id ON alert_rules(organization_id);
CREATE INDEX idx_alert_rules_is_active ON alert_rules(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE alert_rules IS 'Automated alerting rules';
```

---

## 9. Analytics

### 9.1 daily_metrics

```sql
CREATE TABLE daily_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    total_executions INTEGER DEFAULT 0,
    successful_executions INTEGER DEFAULT 0,
    failed_executions INTEGER DEFAULT 0,
    total_ai_requests INTEGER DEFAULT 0,
    total_ai_tokens INTEGER DEFAULT 0,
    total_ai_cost_usd NUMERIC(10, 2) DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    active_workflows INTEGER DEFAULT 0,
    avg_execution_duration_ms INTEGER,
    p95_execution_duration_ms INTEGER,
    total_api_calls INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_org_date UNIQUE (organization_id, metric_date)
);

-- Indexes
CREATE INDEX idx_daily_metrics_organization_id ON daily_metrics(organization_id);
CREATE INDEX idx_daily_metrics_date ON daily_metrics(metric_date DESC);
CREATE INDEX idx_daily_metrics_org_date ON daily_metrics(organization_id, metric_date DESC);

COMMENT ON TABLE daily_metrics IS 'Aggregated daily metrics';
```

### 9.2 user_activity

```sql
CREATE TABLE user_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL, -- 'workflow_created', 'execution_triggered', etc.
    resource_type VARCHAR(50),
    resource_id UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE user_activity_2024_01 PARTITION OF user_activity
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Indexes
CREATE INDEX idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX idx_user_activity_organization_id ON user_activity(organization_id);
CREATE INDEX idx_user_activity_type ON user_activity(activity_type);
CREATE INDEX idx_user_activity_created_at ON user_activity(created_at DESC);

COMMENT ON TABLE user_activity IS 'User activity tracking';
```

### 9.3 error_logs

```sql
CREATE TABLE error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    request_path VARCHAR(500),
    request_method VARCHAR(10),
    request_body TEXT,
    status_code INTEGER,
    metadata JSONB DEFAULT '{}',
    occurred_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (occurred_at);

-- Create monthly partitions
CREATE TABLE error_logs_2024_01 PARTITION OF error_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Indexes
CREATE INDEX idx_error_logs_organization_id ON error_logs(organization_id);
CREATE INDEX idx_error_logs_error_type ON error_logs(error_type);
CREATE INDEX idx_error_logs_occurred_at ON error_logs(occurred_at DESC);

COMMENT ON TABLE error_logs IS 'Application error tracking';
```

---

## 10. Billing

### 10.1 billing_usage

```sql
CREATE TABLE billing_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    billing_period_start DATE NOT NULL,
    billing_period_end DATE NOT NULL,
    total_executions INTEGER DEFAULT 0,
    total_ai_tokens INTEGER DEFAULT 0,
    total_storage_gb NUMERIC(10, 2) DEFAULT 0,
    total_api_calls INTEGER DEFAULT 0,
    total_cost_usd NUMERIC(10, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'invoiced', 'paid'
    invoice_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_org_billing_period UNIQUE (organization_id, billing_period_start),
    CONSTRAINT valid_period CHECK (billing_period_end > billing_period_start)
);

-- Indexes
CREATE INDEX idx_billing_usage_organization_id ON billing_usage(organization_id);
CREATE INDEX idx_billing_usage_period_start ON billing_usage(billing_period_start DESC);
CREATE INDEX idx_billing_usage_status ON billing_usage(status);

COMMENT ON TABLE billing_usage IS 'Monthly billing usage';
```

### 10.2 api_keys

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(64) UNIQUE NOT NULL, -- SHA256 of API key
    key_prefix VARCHAR(10) NOT NULL, -- First 8 chars for identification
    scopes TEXT[] DEFAULT '{}', -- ['workflows:read', 'workflows:write', ...]
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMPTZ,
    revoked_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_api_keys_organization_id ON api_keys(organization_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_api_keys_expires_at ON api_keys(expires_at) WHERE is_active = TRUE;

COMMENT ON TABLE api_keys IS 'API keys for programmatic access';
```

### 10.3 usage_events

```sql
CREATE TABLE usage_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- 'execution', 'ai_request', 'api_call', 'storage'
    quantity INTEGER DEFAULT 1,
    cost_usd NUMERIC(10, 6),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE usage_events_2024_01 PARTITION OF usage_events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Indexes
CREATE INDEX idx_usage_events_organization_id ON usage_events(organization_id);
CREATE INDEX idx_usage_events_event_type ON usage_events(event_type);
CREATE INDEX idx_usage_events_created_at ON usage_events(created_at DESC);

COMMENT ON TABLE usage_events IS 'Detailed usage tracking for billing';
```

---

## 11. Admin & Settings

### 11.1 organization_settings

```sql
CREATE TABLE organization_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID UNIQUE NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    branding JSONB DEFAULT '{}', -- { "logo_url", "primary_color", "secondary_color" }
    security JSONB DEFAULT '{}', -- { "require_mfa": true, "session_timeout_minutes": 120, "ip_whitelist": [...] }
    features JSONB DEFAULT '{}', -- { "advanced_ai": true, "api_access": true }
    integrations JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_organization_settings_organization_id ON organization_settings(organization_id);

COMMENT ON TABLE organization_settings IS 'Organization-specific settings';
```

### 11.2 audit_logs

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- 'workflow.create', 'user.login', 'role.update', etc.
    resource_type VARCHAR(50),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE audit_logs_2024_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Indexes
CREATE INDEX idx_audit_logs_organization_id ON audit_logs(organization_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- Immutable: Prevent updates/deletes
CREATE RULE audit_logs_immutable AS ON UPDATE TO audit_logs DO INSTEAD NOTHING;
CREATE RULE audit_logs_no_delete AS ON DELETE TO audit_logs DO INSTEAD NOTHING;

COMMENT ON TABLE audit_logs IS 'Immutable audit trail (partitioned by month)';
```

---

## Database Functions & Triggers

### Auto-update `updated_at` timestamps

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ... (repeat for all tables with updated_at)
```

### Calculate execution duration

```sql
CREATE OR REPLACE FUNCTION calculate_execution_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.completed_at IS NOT NULL AND NEW.started_at IS NOT NULL THEN
        NEW.duration_ms = EXTRACT(EPOCH FROM (NEW.completed_at - NEW.started_at)) * 1000;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_workflow_execution_duration BEFORE INSERT OR UPDATE ON workflow_executions
    FOR EACH ROW EXECUTE FUNCTION calculate_execution_duration();

CREATE TRIGGER calculate_execution_step_duration BEFORE INSERT OR UPDATE ON execution_steps
    FOR EACH ROW EXECUTE FUNCTION calculate_execution_duration();
```

### Track quota usage

```sql
CREATE OR REPLACE FUNCTION increment_quota_usage()
RETURNS TRIGGER AS $$
BEGIN
    -- Increment workflow execution quota
    UPDATE usage_quotas
    SET quota_used = quota_used + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE organization_id = NEW.organization_id
      AND resource_type = 'executions';

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER increment_execution_quota AFTER INSERT ON workflow_executions
    FOR EACH ROW EXECUTE FUNCTION increment_quota_usage();
```

---

## Database Maintenance

### Partition Management

```sql
-- Script to auto-create monthly partitions (run via cron)
CREATE OR REPLACE FUNCTION create_monthly_partitions()
RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_date TEXT;
    end_date TEXT;
BEGIN
    -- Create partitions for next 3 months
    FOR i IN 0..2 LOOP
        partition_date := DATE_TRUNC('month', CURRENT_DATE + (i || ' months')::INTERVAL);
        start_date := partition_date::TEXT;
        end_date := (partition_date + INTERVAL '1 month')::TEXT;

        -- workflow_executions
        partition_name := 'workflow_executions_' || TO_CHAR(partition_date, 'YYYY_MM');
        EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF workflow_executions FOR VALUES FROM (%L) TO (%L)',
                      partition_name, start_date, end_date);

        -- execution_logs
        partition_name := 'execution_logs_' || TO_CHAR(partition_date, 'YYYY_MM');
        EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF execution_logs FOR VALUES FROM (%L) TO (%L)',
                      partition_name, start_date, end_date);

        -- user_activity
        partition_name := 'user_activity_' || TO_CHAR(partition_date, 'YYYY_MM');
        EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF user_activity FOR VALUES FROM (%L) TO (%L)',
                      partition_name, start_date, end_date);

        -- error_logs
        partition_name := 'error_logs_' || TO_CHAR(partition_date, 'YYYY_MM');
        EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF error_logs FOR VALUES FROM (%L) TO (%L)',
                      partition_name, start_date, end_date);

        -- audit_logs
        partition_name := 'audit_logs_' || TO_CHAR(partition_date, 'YYYY_MM');
        EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF audit_logs FOR VALUES FROM (%L) TO (%L)',
                      partition_name, start_date, end_date);

        -- usage_events
        partition_name := 'usage_events_' || TO_CHAR(partition_date, 'YYYY_MM');
        EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF usage_events FOR VALUES FROM (%L) TO (%L)',
                      partition_name, start_date, end_date);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Schedule: Run monthly via cron or pg_cron extension
```

### Cleanup Old Data

```sql
-- Drop partitions older than retention period
CREATE OR REPLACE FUNCTION drop_old_partitions(retention_months INTEGER)
RETURNS void AS $$
DECLARE
    partition_record RECORD;
    cutoff_date DATE;
BEGIN
    cutoff_date := DATE_TRUNC('month', CURRENT_DATE - (retention_months || ' months')::INTERVAL);

    FOR partition_record IN
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE tablename ~ '^(execution_logs|user_activity|error_logs|usage_events)_\d{4}_\d{2}$'
          AND tablename < 'execution_logs_' || TO_CHAR(cutoff_date, 'YYYY_MM')
    LOOP
        EXECUTE format('DROP TABLE IF EXISTS %I.%I', partition_record.schemaname, partition_record.tablename);
        RAISE NOTICE 'Dropped partition: %', partition_record.tablename;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Keep audit_logs for 7 years (compliance), others for 1 year
```

---

## Performance Optimization

### Connection Pooling (PgBouncer)

```ini
[databases]
flowpilot = host=localhost port=5432 dbname=flowpilot

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
reserve_pool_size = 5
reserve_pool_timeout = 3
max_db_connections = 100
```

### Vacuum & Analyze

```sql
-- Auto-vacuum settings (postgresql.conf)
autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 30s

-- Manual vacuum for heavily updated tables
VACUUM ANALYZE users;
VACUUM ANALYZE workflow_executions;
VACUUM ANALYZE semantic_cache;
```

---

## Database Statistics

| Table | Estimated Rows (1 year) | Size | Partitioned |
|-------|-------------------------|------|-------------|
| users | 100,000 | 50 MB | No |
| organizations | 10,000 | 5 MB | No |
| workflows | 500,000 | 2 GB | No |
| workflow_executions | 100,000,000 | 50 GB | Yes (monthly) |
| execution_steps | 500,000,000 | 200 GB | No (via FK) |
| execution_logs | 2,000,000,000 | 500 GB | Yes (monthly) |
| ai_requests | 200,000,000 | 100 GB | No |
| documents | 1,000,000 | 500 MB | No |
| document_embeddings | 10,000,000 | 20 GB | No |
| audit_logs | 500,000,000 | 250 GB | Yes (monthly) |

**Total Estimated Storage (1 year):** ~1.1 TB

**Optimization Strategies:**
- Partition tables by date (workflow_executions, execution_logs, audit_logs, user_activity, error_logs, usage_events)
- Archive old data to cold storage (S3 + Parquet)
- Use table compression for large tables
- Implement data retention policies

---

## Conclusion

This database schema provides:
- **42 tables** covering all system modules
- **Multi-tenancy isolation** via row-level security
- **Scalability** via partitioning and indexing
- **Security** via encryption and audit trails
- **Performance** via optimized indexes and connection pooling
- **Compliance** via immutable audit logs and data retention policies

The schema is production-ready and designed to handle millions of workflows, executions, and users with sub-second query performance.
