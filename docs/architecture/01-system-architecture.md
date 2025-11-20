# FlowPilot AI - Enterprise System Architecture

## Executive Summary

FlowPilot AI is a production-ready, horizontally scalable SaaS platform enabling enterprises to design, deploy, and orchestrate AI-powered workflow automations with real-time execution, comprehensive audit trails, and enterprise-grade security.

**Target Scale:**
- 10,000+ organizations
- 100,000+ users
- 1,000,000+ workflows
- 99.9% uptime SLA
- SOC 2, GDPR, HIPAA compliance ready

---

## 1. High-Level System Architecture

### 1.1 Architecture Pattern

**Modular Monolith with Microservices-Ready Design**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐       │
│  │   Web Browser   │    │  Mobile Apps    │    │  Third-Party    │       │
│  │   (React SPA)   │    │   (Future)      │    │    Clients      │       │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘       │
│           │                      │                       │                 │
└───────────┼──────────────────────┼───────────────────────┼─────────────────┘
            │                      │                       │
            └──────────────────────┴───────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │      CDN / CloudFlare       │
                    │   (Static Assets, DDoS)     │
                    └──────────────┬──────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────────┐
│                        LOAD BALANCER / REVERSE PROXY                        │
│                            (Nginx / HAProxy)                                │
│                    TLS Termination, Rate Limiting                           │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────────┐
│                         APPLICATION LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    DJANGO APPLICATION CLUSTER                         │ │
│  │                         (Gunicorn Workers)                            │ │
│  │                                                                       │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │ │
│  │  │   API Server │  │  API Server  │  │  API Server  │   (N nodes)  │ │
│  │  │   Instance 1 │  │  Instance 2  │  │  Instance N  │              │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │ │
│  │                                                                       │ │
│  │  Core Applications:                                                  │ │
│  │  • users           - Authentication & User Management                │ │
│  │  • organizations   - Multi-tenancy & Permissions                     │ │
│  │  • workflows       - Workflow Builder & Designer                     │ │
│  │  • executions      - Workflow Execution Engine                       │ │
│  │  • ai_engine       - AI Service & Gemini Integration                 │ │
│  │  • connectors      - Third-party Integration Framework               │ │
│  │  • documents       - Document Intelligence Engine                    │ │
│  │  • notifications   - Multi-channel Notifications                     │ │
│  │  • analytics       - Metrics & Reporting                             │ │
│  │  • billing         - Usage Tracking & Quotas                         │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    DJANGO CHANNELS (WebSocket)                        │ │
│  │                  Real-time Execution Monitoring                       │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │ │
│  │  │  WS Server 1 │  │  WS Server 2 │  │  WS Server N │              │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │
┌──────────────────────────────────▼──────────────────────────────────────────┐
│                          TASK PROCESSING LAYER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         CELERY WORKERS                                │ │
│  │                                                                       │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │ │
│  │  │  High Priority │  │ Normal Priority│  │  Low Priority  │        │ │
│  │  │     Queue      │  │     Queue      │  │     Queue      │        │ │
│  │  │                │  │                │  │                │        │ │
│  │  │ • AI Requests  │  │ • Workflows    │  │ • Reporting    │        │ │
│  │  │ • Webhooks     │  │ • Notifications│  │ • Cleanup      │        │ │
│  │  └────────────────┘  └────────────────┘  └────────────────┘        │ │
│  │                                                                       │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │ │
│  │  │  Worker Pool 1 │  │  Worker Pool 2 │  │  Worker Pool N │        │ │
│  │  │  (4 workers)   │  │  (4 workers)   │  │  (4 workers)   │        │ │
│  │  └────────────────┘  └────────────────┘  └────────────────┘        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         CELERY BEAT                                   │ │
│  │                   Scheduled Workflow Execution                        │ │
│  │          • Cron-based triggers  • Metric aggregation                 │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │
┌──────────────────────────────────▼──────────────────────────────────────────┐
│                           DATA LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │              PRIMARY DATABASE (PostgreSQL 15+)             │            │
│  │                                                            │            │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │            │
│  │  │   Primary    │  │   Replica 1  │  │   Replica N  │   │            │
│  │  │  (Read/Write)│  │  (Read Only) │  │  (Read Only) │   │            │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │            │
│  │                                                            │            │
│  │  Features:                                                 │            │
│  │  • Row-level security (RLS) for multi-tenancy             │            │
│  │  • JSONB fields for workflow definitions                  │            │
│  │  • Table partitioning (executions, logs by date)          │            │
│  │  • Full-text search (pg_trgm, tsvector)                   │            │
│  │  • pgvector extension for embeddings                      │            │
│  │  • Connection pooling via PgBouncer                       │            │
│  └────────────────────────────────────────────────────────────┘            │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │                  REDIS CLUSTER                             │            │
│  │                                                            │            │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │            │
│  │  │   Master 1   │  │   Master 2   │  │   Master 3   │   │            │
│  │  │  + Replica   │  │  + Replica   │  │  + Replica   │   │            │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │            │
│  │                                                            │            │
│  │  Use Cases:                                                │            │
│  │  • Celery broker & result backend                         │            │
│  │  • Session storage                                         │            │
│  │  • API response caching                                    │            │
│  │  • Rate limiting counters                                  │            │
│  │  • WebSocket pub/sub                                       │            │
│  │  • Semantic cache for AI prompts                           │            │
│  └────────────────────────────────────────────────────────────┘            │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │              OBJECT STORAGE (S3-Compatible)                │            │
│  │                                                            │            │
│  │  • Uploaded documents (PDF, DOCX, images)                  │            │
│  │  • Execution artifacts                                     │            │
│  │  • Export files (CSV, Excel)                               │            │
│  │  • Static assets (production)                              │            │
│  └────────────────────────────────────────────────────────────┘            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │
┌──────────────────────────────────▼──────────────────────────────────────────┐
│                      EXTERNAL SERVICES LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │                    GOOGLE GEMINI API                       │            │
│  │  • Gemini 1.5 Pro (complex tasks)                          │            │
│  │  • Gemini 1.5 Flash (fast tasks)                           │            │
│  │  • Rate limiting & retry logic                             │            │
│  │  • Token usage tracking                                    │            │
│  └────────────────────────────────────────────────────────────┘            │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │                 THIRD-PARTY INTEGRATIONS                   │            │
│  │  • Email: Gmail API, Outlook Graph API                     │            │
│  │  • Communication: Slack, Microsoft Teams                   │            │
│  │  • Productivity: Notion, Jira, Trello, Asana              │            │
│  │  • Storage: Google Drive, Dropbox, OneDrive                │            │
│  │  • CRM: Salesforce, HubSpot, Pipedrive                     │            │
│  └────────────────────────────────────────────────────────────┘            │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │                   SUPPORTING SERVICES                      │            │
│  │  • Email Provider: SendGrid / AWS SES                      │            │
│  │  • SMS: Twilio                                             │            │
│  │  • OCR: Google Cloud Vision API                            │            │
│  │  • Error Tracking: Sentry                                  │            │
│  └────────────────────────────────────────────────────────────┘            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │
┌──────────────────────────────────▼──────────────────────────────────────────┐
│                    OBSERVABILITY & MONITORING LAYER                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐              │
│  │   Prometheus   │  │    Grafana     │  │     Sentry     │              │
│  │   (Metrics)    │  │ (Visualization)│  │ (Error Track)  │              │
│  └────────────────┘  └────────────────┘  └────────────────┘              │
│                                                                             │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐              │
│  │      Loki      │  │     Flower     │  │   CloudWatch   │              │
│  │    (Logs)      │  │ (Celery Monitor│  │   (AWS Logs)   │              │
│  └────────────────┘  └────────────────┘  └────────────────┘              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Application Layer Architecture

### 2.1 Django Application Structure

```
backend/
├── config/                          # Project configuration
│   ├── settings/
│   │   ├── base.py                  # Base settings
│   │   ├── development.py           # Development settings
│   │   ├── production.py            # Production settings
│   │   └── test.py                  # Test settings
│   ├── urls.py                      # Root URL configuration
│   ├── wsgi.py                      # WSGI entry point
│   ├── asgi.py                      # ASGI entry point (WebSockets)
│   └── celery.py                    # Celery configuration
│
├── apps/                            # Django applications (bounded contexts)
│   ├── users/                       # User & Authentication
│   │   ├── models.py                # User, UserSession, LoginAttempt, MFADevice, OAuthConnection
│   │   ├── serializers.py           # User serializers with validation
│   │   ├── viewsets.py              # User CRUD, profile management
│   │   ├── services.py              # Authentication business logic
│   │   ├── tasks.py                 # User-related async tasks
│   │   ├── permissions.py           # Custom permissions
│   │   ├── filters.py               # User filtering
│   │   ├── admin.py                 # Django admin customization
│   │   └── tests/                   # Unit and integration tests
│   │
│   ├── organizations/               # Multi-tenancy & Organizations
│   │   ├── models.py                # Organization, OrganizationMember, Role, Invitation, Department, UsageQuota
│   │   ├── serializers.py           # Organization serializers
│   │   ├── viewsets.py              # Organization CRUD, member management
│   │   ├── services.py              # Multi-tenancy logic, quota enforcement
│   │   ├── middleware.py            # Organization context injection
│   │   ├── tasks.py                 # Invitation emails, quota calculation
│   │   ├── permissions.py           # Role-based permissions
│   │   └── tests/
│   │
│   ├── workflows/                   # Workflow Builder & Management
│   │   ├── models.py                # Workflow, WorkflowVersion, WorkflowTemplate, WorkflowVariable, WorkflowTrigger
│   │   ├── serializers.py           # Workflow serializers with JSON schema validation
│   │   ├── viewsets.py              # Workflow CRUD, versioning, templates
│   │   ├── services.py              # Workflow validation, versioning logic
│   │   ├── validators.py            # Workflow definition validators
│   │   ├── tasks.py                 # Scheduled workflow triggers
│   │   └── tests/
│   │
│   ├── executions/                  # Workflow Execution Engine
│   │   ├── models.py                # WorkflowExecution, ExecutionStep, ExecutionLog, AIRequest
│   │   ├── serializers.py           # Execution serializers
│   │   ├── viewsets.py              # Execution viewing, retry, cancel
│   │   ├── services.py              # Execution orchestration
│   │   ├── engine/                  # Execution engine core
│   │   │   ├── state_machine.py     # Workflow state machine
│   │   │   ├── executor.py          # Step executor (Factory pattern)
│   │   │   ├── context.py           # Execution context management
│   │   │   └── steps/               # Step implementations
│   │   │       ├── ai_steps.py      # AI node implementations
│   │   │       ├── action_steps.py  # Action node implementations
│   │   │       ├── logic_steps.py   # Logic node implementations
│   │   │       └── integration_steps.py
│   │   ├── tasks.py                 # Celery tasks for execution
│   │   ├── consumers.py             # WebSocket consumers for real-time updates
│   │   └── tests/
│   │
│   ├── ai_engine/                   # AI Service Layer
│   │   ├── models.py                # AIRequest, PromptTemplate, SemanticCache
│   │   ├── services/
│   │   │   ├── gemini_client.py     # Gemini API wrapper
│   │   │   ├── prompt_manager.py    # Prompt template management
│   │   │   ├── token_tracker.py     # Token usage tracking
│   │   │   ├── response_parser.py   # Response parsing & validation
│   │   │   └── semantic_cache.py    # Prompt caching with vector similarity
│   │   ├── tasks.py                 # AI processing tasks
│   │   └── tests/
│   │
│   ├── connectors/                  # Enterprise Connector Framework
│   │   ├── models.py                # Connector, ConnectorCredential, ConnectorWebhook, ConnectorSyncLog
│   │   ├── serializers.py           # Connector serializers
│   │   ├── viewsets.py              # Connector management, OAuth flows
│   │   ├── services/
│   │   │   ├── oauth_manager.py     # OAuth 2.0 flow orchestration
│   │   │   ├── credential_store.py  # Encrypted credential management
│   │   │   └── webhook_processor.py # Webhook verification & processing
│   │   ├── integrations/            # Connector implementations (Strategy pattern)
│   │   │   ├── base.py              # Base connector interface
│   │   │   ├── gmail.py             # Gmail connector
│   │   │   ├── slack.py             # Slack connector
│   │   │   ├── notion.py            # Notion connector
│   │   │   ├── salesforce.py        # Salesforce connector
│   │   │   └── ... (more connectors)
│   │   ├── tasks.py                 # Token refresh, sync tasks
│   │   └── tests/
│   │
│   ├── documents/                   # Document Intelligence Engine
│   │   ├── models.py                # Document, DocumentPage, DocumentExtraction, DocumentEmbedding
│   │   ├── serializers.py           # Document serializers
│   │   ├── viewsets.py              # Document upload, extraction, search
│   │   ├── services/
│   │   │   ├── document_processor.py # File upload & processing orchestration
│   │   │   ├── ocr_service.py       # OCR with Google Vision API
│   │   │   ├── extraction_service.py # Entity & table extraction
│   │   │   ├── embedding_service.py # Document embedding generation
│   │   │   └── search_service.py    # Semantic search with pgvector
│   │   ├── tasks.py                 # Document processing tasks
│   │   └── tests/
│   │
│   ├── notifications/               # Notification System
│   │   ├── models.py                # Notification, NotificationPreference, AlertRule
│   │   ├── serializers.py           # Notification serializers
│   │   ├── viewsets.py              # Notification viewing, preferences
│   │   ├── services/
│   │   │   ├── dispatcher.py        # Multi-channel dispatch (Observer pattern)
│   │   │   ├── email_sender.py      # Email notifications
│   │   │   ├── slack_sender.py      # Slack notifications
│   │   │   └── sms_sender.py        # SMS notifications
│   │   ├── tasks.py                 # Notification sending tasks
│   │   └── tests/
│   │
│   ├── analytics/                   # Analytics & Reporting
│   │   ├── models.py                # DailyMetrics, UserActivity, ErrorLog
│   │   ├── serializers.py           # Analytics serializers
│   │   ├── viewsets.py              # Dashboard data, reports
│   │   ├── services/
│   │   │   ├── metrics_aggregator.py # Metrics calculation
│   │   │   └── report_generator.py  # Custom report generation
│   │   ├── tasks.py                 # Metric aggregation tasks
│   │   └── tests/
│   │
│   └── billing/                     # Usage Tracking & Quotas
│       ├── models.py                # BillingUsage, UsageQuota, APIKey
│       ├── serializers.py           # Billing serializers
│       ├── viewsets.py              # Usage viewing, API key management
│       ├── services/
│       │   ├── usage_tracker.py     # Track API calls, executions, etc.
│       │   └── quota_enforcer.py    # Enforce tenant quotas
│       ├── middleware.py            # API key authentication, quota checks
│       ├── tasks.py                 # Usage calculation tasks
│       └── tests/
│
├── core/                            # Shared utilities
│   ├── exceptions.py                # Custom exception classes
│   ├── permissions.py               # Base permission classes
│   ├── pagination.py                # Custom pagination classes
│   ├── validators.py                # Reusable validators
│   ├── utils.py                     # Helper functions
│   ├── encryption.py                # Encryption utilities
│   └── decorators.py                # Custom decorators
│
├── tests/                           # Integration tests
│   ├── integration/
│   ├── load/                        # Load tests (Locust)
│   └── fixtures/                    # Test fixtures
│
├── manage.py                        # Django management script
├── requirements/                    # Python dependencies
│   ├── base.txt
│   ├── development.txt
│   ├── production.txt
│   └── test.txt
└── docker-compose.yml               # Local development orchestration
```

### 2.2 Bounded Context Integration

Each Django app represents a **bounded context** with clear interfaces:

**Communication Patterns:**
1. **Direct Imports:** For same-transaction operations (e.g., organizations -> users)
2. **Service Layer:** Business logic encapsulated in `services.py`
3. **Django Signals:** For decoupled event handling (e.g., workflow execution triggers notification)
4. **Celery Tasks:** For async operations (e.g., document processing, AI requests)

**Dependency Flow:**
```
users (foundation)
  ↓
organizations (multi-tenancy)
  ↓
workflows, connectors, documents (core features)
  ↓
executions (orchestration)
  ↓
ai_engine (AI processing)
  ↓
notifications, analytics, billing (supporting services)
```

---

## 3. Data Flow Architecture

### 3.1 Typical API Request Flow

```
1. Client Request
   │
   ▼
2. Load Balancer (Nginx)
   │ - SSL termination
   │ - Rate limiting (basic)
   ▼
3. Django Application Server
   │
   ├─> Middleware Stack
   │   ├─> CORS middleware
   │   ├─> Authentication middleware (JWT validation)
   │   ├─> Organization context middleware (inject tenant context)
   │   ├─> Rate limiting middleware (Redis-backed)
   │   └─> Request logging middleware
   │
   ├─> URL Routing
   │
   ├─> View/ViewSet
   │   ├─> Permission check (IsAuthenticated, HasOrganizationAccess, etc.)
   │   ├─> Input validation (Serializer)
   │   │
   │   ├─> Service Layer (Business Logic)
   │   │   ├─> Database query (PostgreSQL with ORM)
   │   │   ├─> Cache check/update (Redis)
   │   │   ├─> Trigger async task (Celery)
   │   │   └─> Emit domain event (Django signals)
   │   │
   │   └─> Response serialization
   │
   └─> Response
       │
       ▼
4. Client receives response
```

### 3.2 Workflow Execution Flow

```
1. User triggers workflow execution
   │ (via UI, API, or scheduled trigger)
   ▼
2. POST /api/v1/executions/
   │
   ├─> Create WorkflowExecution record (status: PENDING)
   ├─> Enqueue Celery task: execute_workflow.delay(execution_id)
   └─> Return execution_id to client
   │
   ▼
3. Celery Worker picks up task
   │
   ├─> Fetch WorkflowExecution and Workflow definition
   ├─> Update status: RUNNING
   ├─> Notify via WebSocket (Django Channels)
   │
   ├─> For each step in workflow:
   │   │
   │   ├─> Create ExecutionStep record
   │   ├─> Execute step (via Factory pattern)
   │   │   │
   │   │   ├─> AI Step: Call ai_engine.services.gemini_client
   │   │   │   ├─> Check semantic cache (Redis + pgvector)
   │   │   │   ├─> Call Gemini API if cache miss
   │   │   │   ├─> Store result in cache
   │   │   │   └─> Track token usage (AIRequest record)
   │   │   │
   │   │   ├─> Action Step: Call connector integration
   │   │   │   ├─> Fetch connector credentials (encrypted)
   │   │   │   ├─> Call third-party API (Gmail, Slack, etc.)
   │   │   │   └─> Log API call (ConnectorSyncLog)
   │   │   │
   │   │   └─> Logic Step: Conditional, loop, merge/split
   │   │
   │   ├─> Update ExecutionStep (status, output, duration)
   │   ├─> Create ExecutionLog entries
   │   └─> Notify via WebSocket (real-time progress)
   │
   ├─> Handle errors:
   │   ├─> Retry logic (exponential backoff)
   │   ├─> Try-catch blocks
   │   └─> Move to dead letter queue if max retries exceeded
   │
   ├─> Update WorkflowExecution status: COMPLETED / FAILED
   ├─> Emit completion event (Django signal)
   │   ├─> Trigger notification (email, Slack)
   │   └─> Update analytics (DailyMetrics)
   │
   └─> Notify via WebSocket (final status)
   │
   ▼
4. User sees real-time updates in UI
```

### 3.3 Authentication Flow

```
1. User Login Request
   │ POST /api/v1/auth/login { email, password, mfa_code? }
   ▼
2. Authenticate credentials
   │
   ├─> Check account lockout (LoginAttempt records)
   ├─> Validate password (bcrypt hash)
   ├─> Validate MFA if enabled (TOTP via pyotp)
   │
   ├─> Success:
   │   ├─> Create UserSession record (device tracking)
   │   ├─> Generate JWT tokens (access + refresh)
   │   ├─> Store refresh token in Redis (with TTL)
   │   ├─> Log successful login (AuditLog)
   │   └─> Return tokens to client
   │
   └─> Failure:
       ├─> Increment LoginAttempt counter
       ├─> Lock account if max attempts exceeded
       ├─> Log failed attempt (AuditLog)
       └─> Return error

3. Subsequent API Requests
   │ Authorization: Bearer <access_token>
   ▼
4. JWT Middleware
   │
   ├─> Verify JWT signature
   ├─> Check token expiry (15 min)
   ├─> Check token blacklist (Redis)
   ├─> Extract user_id and organization_id
   ├─> Load user and organization into request context
   └─> Continue to view

5. Token Refresh
   │ POST /api/v1/auth/refresh { refresh_token }
   ▼
6. Validate refresh token
   │
   ├─> Check token in Redis
   ├─> Verify signature and expiry (7 days)
   ├─> Issue new access token
   ├─> Rotate refresh token (security best practice)
   │   ├─> Invalidate old refresh token
   │   └─> Issue new refresh token
   └─> Return new tokens
```

---

## 4. Multi-Tenancy Architecture

### 4.1 Tenant Isolation Strategy

**Row-Level Security (RLS) Approach**

All tenant-scoped data includes an `organization_id` foreign key. PostgreSQL Row-Level Security policies enforce data isolation at the database level.

**Implementation:**

```sql
-- Example RLS policy for Workflow model
CREATE POLICY workflow_isolation_policy ON workflows
    USING (organization_id = current_setting('app.current_organization_id')::uuid);

ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
```

**Middleware Integration:**

```python
# organizations/middleware.py
class OrganizationContextMiddleware:
    """
    Injects organization context into request and database session.
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            # Get organization from JWT claims or user's default org
            organization = get_current_organization(request.user)
            request.organization = organization

            # Set PostgreSQL session variable for RLS
            with connection.cursor() as cursor:
                cursor.execute(
                    "SET app.current_organization_id = %s",
                    [str(organization.id)]
                )
```

**Benefits:**
- Database-level enforcement (cannot be bypassed by application bugs)
- Simplified queries (no need to filter by organization_id in every query)
- Security in depth

### 4.2 Hierarchical Organizations

```
Root Organization (Parent)
├── Subsidiary A
│   ├── Department 1
│   └── Department 2
└── Subsidiary B
    └── Department 3
```

**Model Structure:**
```python
class Organization(models.Model):
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    # ... other fields

    def get_all_children(self):
        """Recursively get all child organizations."""
        # Implementation with recursive CTE
```

**Use Cases:**
- Consolidated billing for parent organization
- Shared templates across subsidiaries
- Cross-organization reporting (with explicit permission)

---

## 5. Scalability & Performance Architecture

### 5.1 Horizontal Scaling

**Stateless Application Design:**
- No in-memory session storage (uses Redis)
- No local file storage (uses S3)
- No server-specific state

**Scaling Components:**

| Component | Scaling Strategy | Trigger |
|-----------|-----------------|---------|
| Django API Servers | Horizontal (add instances) | CPU > 70%, Response time > 500ms |
| Celery Workers | Horizontal (add workers) | Queue depth > 1000, Wait time > 60s |
| PostgreSQL | Vertical + Read replicas | CPU > 60%, Connections > 80% |
| Redis | Cluster mode (sharding) | Memory > 80%, Ops/sec > 100k |
| Django Channels | Horizontal (add WS servers) | Concurrent connections > 5000/server |

### 5.2 Caching Strategy

**Multi-Layer Cache:**

```
1. Browser Cache (static assets)
   ↓
2. CDN Cache (CloudFlare)
   ↓
3. Redis Cache (API responses, queries)
   ↓
4. PostgreSQL (source of truth)
```

**Cache Patterns:**

| Data Type | Cache Duration | Invalidation Strategy |
|-----------|----------------|----------------------|
| User profile | 15 minutes | On update (explicit invalidation) |
| Organization settings | 1 hour | On update |
| Workflow definitions | 5 minutes | Version-based (new version = new cache key) |
| Execution results | 24 hours | Time-based expiration |
| AI responses (semantic) | 7 days | Similarity-based lookup |
| Static assets | 1 year | Versioned URLs |

**Cache Key Strategy:**
```
{resource_type}:{organization_id}:{resource_id}:{version}

Examples:
workflow:123e4567-e89b:456f-789a:v2
user:123e4567-e89b:profile
ai_cache:semantic_hash_abc123
```

### 5.3 Database Optimization

**Table Partitioning:**

```sql
-- Partition WorkflowExecution by date (monthly partitions)
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    -- other fields
) PARTITION BY RANGE (created_at);

CREATE TABLE workflow_executions_2024_01 PARTITION OF workflow_executions
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Auto-create new partitions monthly (via cron/script)
```

**Indexing Strategy:**

```sql
-- Composite indexes for common queries
CREATE INDEX idx_executions_org_status_created
    ON workflow_executions(organization_id, status, created_at DESC);

-- GIN indexes for JSONB columns
CREATE INDEX idx_workflows_definition_gin
    ON workflows USING GIN (definition);

-- Full-text search indexes
CREATE INDEX idx_documents_content_fts
    ON documents USING GIN (to_tsvector('english', content));

-- pgvector indexes for embeddings
CREATE INDEX idx_document_embeddings_vector
    ON document_embeddings USING ivfflat (embedding vector_cosine_ops);
```

**Query Optimization:**
- Use `select_related()` for foreign keys (SQL JOIN)
- Use `prefetch_related()` for reverse foreign keys (separate query + Python join)
- Implement pagination (limit/offset or cursor-based)
- Use `only()` to fetch subset of fields
- Database connection pooling via PgBouncer (max 500 connections)

### 5.4 Celery Queue Architecture

**Queue Priority System:**

```python
CELERY_TASK_ROUTES = {
    # High priority (near real-time)
    'executions.tasks.execute_workflow_step': {'queue': 'high_priority'},
    'connectors.tasks.process_webhook': {'queue': 'high_priority'},

    # Normal priority (standard async)
    'notifications.tasks.send_notification': {'queue': 'default'},
    'ai_engine.tasks.process_ai_request': {'queue': 'default'},

    # Low priority (batch/background)
    'analytics.tasks.aggregate_daily_metrics': {'queue': 'low_priority'},
    'billing.tasks.calculate_monthly_usage': {'queue': 'low_priority'},
}

# Worker allocation
# high_priority: 8 workers (concurrency 4 each = 32 concurrent tasks)
# default: 4 workers (concurrency 4 each = 16 concurrent tasks)
# low_priority: 2 workers (concurrency 2 each = 4 concurrent tasks)
```

**Task Retry Strategy:**

```python
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute
    retry_backoff=True,      # Exponential: 60s, 120s, 240s
    retry_jitter=True        # Add randomness to prevent thundering herd
)
def execute_workflow_step(self, execution_id, step_id):
    try:
        # Execute step
        pass
    except RecoverableError as exc:
        # Retry on recoverable errors (network, rate limit)
        raise self.retry(exc=exc)
    except NonRecoverableError:
        # Don't retry (invalid input, auth failure)
        # Move to dead letter queue
        move_to_dlq(execution_id, step_id)
```

---

## 6. Security Architecture

### 6.1 Defense in Depth

**Layer 1: Network Security**
- CloudFlare DDoS protection
- WAF (Web Application Firewall)
- IP whitelisting (optional, per organization)

**Layer 2: Application Security**
- TLS 1.3 for all connections
- JWT authentication with short expiry
- CSRF protection (Django middleware)
- XSS prevention (DOMPurify on frontend, Django auto-escaping)
- SQL injection prevention (ORM usage, parameterized queries)
- Rate limiting (per-user, per-endpoint)

**Layer 3: Data Security**
- Encryption at rest (PostgreSQL, S3 server-side encryption)
- Field-level encryption for sensitive data (credentials, API keys)
- Row-level security (multi-tenancy isolation)

**Layer 4: Authentication & Authorization**
- Multi-factor authentication (TOTP)
- OAuth 2.0 for third-party integrations
- Role-based access control (RBAC)
- Object-level permissions (Django Guardian)

**Layer 5: Audit & Monitoring**
- Immutable audit logs
- Real-time error tracking (Sentry)
- Security event monitoring
- GDPR compliance (data export/deletion)

### 6.2 Secrets Management

**Environment-Based Configuration:**

```bash
# .env file (never committed to version control)
SECRET_KEY=...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
GEMINI_API_KEY=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

**Encrypted Secrets in Database:**

```python
from django_cryptography.fields import encrypt

class ConnectorCredential(models.Model):
    access_token = encrypt(models.TextField())  # Encrypted at rest
    refresh_token = encrypt(models.TextField())
    # Auto-decrypt on access, auto-encrypt on save
```

**Secrets Rotation:**
- API keys: 90-day expiration with email alerts
- Database credentials: Quarterly rotation
- JWT signing keys: Annual rotation with grace period

---

## 7. Deployment Architecture

### 7.1 Production Deployment (AWS Example)

```
┌─────────────────────────────────────────────────────────────────┐
│                           ROUTE 53                              │
│                      (DNS Management)                           │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                       CLOUDFLARE                                │
│              (CDN, DDoS Protection, WAF)                        │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                   APPLICATION LOAD BALANCER                     │
│          (ALB with SSL/TLS termination, health checks)          │
└──────────┬─────────────────────────┬────────────────────────────┘
           │                         │
┌──────────▼──────────┐   ┌──────────▼──────────┐
│   ECS/Fargate       │   │   ECS/Fargate       │
│   API Cluster       │   │   WebSocket Cluster │
│                     │   │                     │
│  ┌──────────────┐   │   │  ┌──────────────┐   │
│  │  Django API  │   │   │  │   Channels   │   │
│  │  (Gunicorn)  │   │   │  │  (Daphne)    │   │
│  └──────────────┘   │   │  └──────────────┘   │
│  Auto-scaling:      │   │  Auto-scaling:      │
│  2-10 tasks         │   │  1-5 tasks          │
└─────────────────────┘   └─────────────────────┘
           │                         │
           └────────────┬────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼─────┐  ┌──────▼──────┐  ┌────▼────────┐
│  RDS Aurora │  │    Redis    │  │     S3      │
│ (PostgreSQL)│  │  ElastiCache│  │   Bucket    │
│             │  │   Cluster   │  │             │
│ Primary +   │  │             │  │ • Documents │
│ 2 Replicas  │  │ 3 nodes +   │  │ • Static    │
│             │  │ replicas    │  │ • Exports   │
└─────────────┘  └─────────────┘  └─────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      ECS/Fargate Celery Workers                 │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ High Priority│  │    Default   │  │ Low Priority │         │
│  │   Workers    │  │   Workers    │  │   Workers    │         │
│  │  (8 tasks)   │  │  (4 tasks)   │  │  (2 tasks)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐                                              │
│  │ Celery Beat  │  (Scheduled tasks)                           │
│  │  (1 task)    │                                              │
│  └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING & LOGGING                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  CloudWatch  │  │   Prometheus │  │    Sentry    │         │
│  │   (Logs)     │  │  (Metrics)   │  │   (Errors)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐                           │
│  │   Grafana    │  │    Flower    │                           │
│  │ (Dashboards) │  │ (Celery UI)  │                           │
│  └──────────────┘  └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Infrastructure as Code

**Terraform for provisioning:**
- VPC, subnets, security groups
- RDS Aurora cluster
- ElastiCache Redis cluster
- ECS cluster, task definitions
- ALB, target groups
- S3 buckets with lifecycle policies
- IAM roles and policies

**Docker Compose for local development:**
- Django API service
- Django Channels service
- Celery workers (high, default, low priority)
- Celery Beat
- PostgreSQL
- Redis
- Flower (Celery monitoring)

### 7.3 CI/CD Pipeline

```
Developer Push
      │
      ▼
GitHub Actions Trigger
      │
      ├─> Run linters (flake8, black, isort)
      ├─> Run tests (pytest with coverage)
      ├─> Build Docker images
      ├─> Push to ECR (Elastic Container Registry)
      │
      ▼
Deployment (if tests pass)
      │
      ├─> Staging Environment
      │   ├─> Deploy to ECS staging cluster
      │   ├─> Run smoke tests
      │   └─> Manual approval gate
      │
      ├─> Production Environment
      │   ├─> Blue/Green deployment
      │   ├─> Deploy to ECS production cluster
      │   ├─> Run health checks
      │   ├─> Monitor error rates (Sentry)
      │   └─> Auto-rollback if error spike detected
      │
      └─> Notify team (Slack notification)
```

---

## 8. Event-Driven Architecture

### 8.1 Domain Events

**Django Signals for Intra-Application Events:**

```python
# Example: When workflow execution completes
from django.dispatch import Signal

workflow_execution_completed = Signal()  # providing_args=['execution']

# Sender (executions app)
workflow_execution_completed.send(
    sender=WorkflowExecution,
    execution=execution_instance
)

# Receivers
@receiver(workflow_execution_completed)
def send_completion_notification(sender, execution, **kwargs):
    """Trigger notification when execution completes."""
    # notifications.tasks.send_notification.delay(...)

@receiver(workflow_execution_completed)
def update_analytics(sender, execution, **kwargs):
    """Update analytics metrics."""
    # analytics.tasks.update_execution_metrics.delay(...)
```

**Benefits:**
- Decoupling (apps don't directly depend on each other)
- Extensibility (easy to add new event handlers)
- Observability (centralized event logging)

### 8.2 Webhook Events for External Consumers

**Outgoing Webhooks:**

Organizations can register webhook URLs to receive events:
- `workflow.execution.completed`
- `workflow.execution.failed`
- `document.processing.completed`
- `connector.sync.completed`

**Implementation:**
```python
# Send webhook when execution completes
@receiver(workflow_execution_completed)
def trigger_outgoing_webhooks(sender, execution, **kwargs):
    webhooks = execution.organization.webhooks.filter(
        event_type='workflow.execution.completed',
        is_active=True
    )
    for webhook in webhooks:
        tasks.send_webhook.delay(webhook.id, execution.id)
```

**Incoming Webhooks:**

Third-party services can trigger workflow executions via webhooks:
- Unique webhook URL per workflow: `/api/v1/webhooks/{workflow_id}/{secret_token}`
- Signature verification (HMAC)
- Idempotency (deduplicate based on event ID)

---

## 9. Disaster Recovery & Business Continuity

### 9.1 Backup Strategy

| Resource | Backup Frequency | Retention | Recovery Time Objective (RTO) |
|----------|------------------|-----------|-------------------------------|
| PostgreSQL | Continuous (WAL archiving) + Daily snapshots | 30 days | < 1 hour |
| Redis | Daily snapshots | 7 days | < 15 minutes (acceptable data loss) |
| S3 (Documents) | Cross-region replication | Indefinite | < 5 minutes |
| Configuration | Version controlled (Git) | Indefinite | < 5 minutes |

### 9.2 High Availability

- **API Servers:** Multi-AZ deployment, auto-scaling
- **Database:** Aurora with multi-AZ, automatic failover (< 30s)
- **Redis:** Cluster mode with replicas, automatic failover
- **Load Balancer:** Multi-AZ with health checks

**Uptime Target:** 99.9% (< 8.76 hours downtime/year)

---

## 10. Compliance & Audit

### 10.1 Audit Logging

**Immutable Audit Trail:**

All critical actions logged to `AuditLog` table:
- User authentication (login, logout, failed attempts)
- Resource creation/update/deletion (workflows, connectors, documents)
- Permission changes (role assignments, invitations)
- Data access (viewing sensitive documents)

**Log Structure:**
```python
class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    organization = models.ForeignKey(Organization)
    user = models.ForeignKey(User, null=True)  # null if system action
    action = models.CharField(max_length=100)  # 'workflow.create', 'user.login'
    resource_type = models.CharField(max_length=50)
    resource_id = models.UUIDField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    metadata = models.JSONField()  # Additional context

    class Meta:
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['organization', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
        # Prevent deletion/update
        permissions = [('view_audit_log', 'Can view audit log')]
```

### 10.2 GDPR Compliance

**Data Subject Rights:**
- **Right to Access:** API endpoint to export all user data (JSON/CSV)
- **Right to Deletion:** Anonymize user data (replace with `[DELETED]`, keep audit trail)
- **Right to Portability:** Export data in machine-readable format
- **Right to Rectification:** Allow users to update their data

**Data Retention:**
- Active user data: Indefinite (while account active)
- Deleted user data (anonymized): 90 days
- Audit logs: 7 years (compliance requirement)
- Execution logs: 1 year (configurable per organization)

---

## 11. Technology Selection Rationale

### 11.1 Why Django?

**Pros:**
- Mature ecosystem (10+ years)
- Batteries included (ORM, admin, auth)
- Django REST Framework (world-class API framework)
- Strong security defaults (CSRF, XSS protection)
- Large talent pool
- Excellent for rapid development

**Cons:**
- Monolithic (mitigated by modular design)
- Python GIL (mitigated by async workers)

**Decision:** Django's maturity, security, and rapid development capabilities outweigh drawbacks. Modular monolith design allows future microservices extraction if needed.

### 11.2 Why PostgreSQL?

**Pros:**
- ACID compliance (data integrity)
- Advanced features (JSONB, full-text search, partitioning, RLS)
- pgvector extension (vector embeddings)
- Excellent performance at scale
- Open source

**Cons:**
- Vertical scaling limits (mitigated by read replicas, partitioning)

**Decision:** PostgreSQL's advanced features (JSONB for workflow definitions, pgvector for semantic search, RLS for multi-tenancy) make it ideal for this use case.

### 11.3 Why Celery?

**Pros:**
- De facto standard for Django async tasks
- Supports multiple brokers (Redis, RabbitMQ)
- Advanced features (chains, groups, chords)
- Built-in retry logic
- Flower for monitoring

**Cons:**
- Complex configuration
- Potential for message loss (mitigated by persistent broker)

**Decision:** Celery's maturity and deep Django integration make it the best choice for distributed task processing.

### 11.4 Why Redis?

**Pros:**
- In-memory performance (sub-millisecond latency)
- Versatile (cache, session store, message broker, pub/sub)
- Cluster mode for horizontal scaling
- Persistence options (RDB, AOF)

**Cons:**
- Memory-bound (mitigated by eviction policies, partitioning)

**Decision:** Redis's versatility and performance make it ideal for caching, sessions, and Celery broker.

### 11.5 Why Google Gemini?

**Pros:**
- State-of-the-art language understanding
- Multimodal (text, images)
- Competitive pricing
- Gemini 1.5 Flash for speed, Pro for quality

**Cons:**
- Vendor lock-in (mitigated by abstraction layer)

**Decision:** Gemini's capabilities and pricing are competitive. Abstraction layer allows future model swapping.

### 11.6 Why React (JavaScript, not TypeScript)?

**Pros:**
- Large ecosystem and community
- JavaScript allows faster development for experienced teams
- Easier to find developers
- Less build complexity

**Cons:**
- No compile-time type checking (mitigated by prop-types, comprehensive testing)

**Decision:** Per requirements, React with JavaScript provides rapid development. Strict ESLint rules and testing compensate for lack of TypeScript.

---

## 12. Future Considerations

### 12.1 Potential Microservices Extraction

As system scales, consider extracting:
- **AI Engine Service:** Isolate AI processing, scale independently
- **Execution Engine Service:** Dedicated service for workflow execution
- **Connector Service:** Isolate third-party API calls

**Migration Path:**
1. Define clear service boundaries (already done via Django apps)
2. Introduce API gateways
3. Extract one service at a time
4. Use event bus (Kafka, RabbitMQ) for inter-service communication

### 12.2 Global Distribution

For global customers:
- Multi-region deployment (US, EU, APAC)
- Data residency compliance (GDPR, data localization laws)
- Global load balancing (Route 53, CloudFlare)
- Regional database replicas

### 12.3 Advanced AI Capabilities

- Fine-tuned models for specific industries
- On-premise model deployment (for sensitive data)
- Multi-model orchestration (ensemble techniques)
- Reinforcement learning from user feedback

---

## Conclusion

This architecture provides a solid foundation for FlowPilot AI to achieve:
- **Scalability:** Handle 10,000+ organizations, 100,000+ users, 1M+ workflows
- **Security:** Enterprise-grade security with defense in depth
- **Performance:** Sub-second API responses, real-time execution monitoring
- **Reliability:** 99.9% uptime with automated failover
- **Maintainability:** Clean code, comprehensive testing, observability
- **Extensibility:** Easy to add new features, connectors, and AI capabilities

The modular monolith approach provides immediate time-to-market benefits while maintaining a clear path to microservices if needed.
