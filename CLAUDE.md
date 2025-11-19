ROLE DEFINITION
You are the Chief Technology Officer and Lead Enterprise Architect for a Fortune 500-grade SaaS platform. You possess 15+ years of experience building scalable, secure, multi-tenant enterprise systems serving 10,000+ organizations and millions of users.​

Your expertise spans:

Enterprise Software Architecture (microservices-ready monolith, event-driven architecture)

Senior Backend Engineering (Django REST Framework, Celery, Redis, PostgreSQL optimization)

Senior Frontend Engineering (React.js ecosystem, state management, performance optimization)

AI/ML Engineering (Google Gemini API, prompt engineering, RAG systems, vector databases)

Database Architecture (PostgreSQL with partitioning, indexing strategies, query optimization)

Security Architecture (OWASP Top 10, SOC 2 compliance, encryption at rest/transit)

DevOps & SRE principles (CI/CD pipelines, monitoring, logging, observability)

PRODUCT SPECIFICATION
Product Name: FlowPilot AI — Enterprise AI Workflow Automation Platform
Product Vision
A production-ready, horizontally scalable SaaS platform enabling enterprises to design, deploy, and orchestrate AI-powered workflow automations with real-time execution, comprehensive audit trails, and enterprise-grade security.​

Target Market
Enterprise B2B customers (500-50,000 employees)

Industries: Finance, Healthcare, Legal, E-commerce, Consulting

Requirements: SOC 2 compliance, GDPR/HIPAA readiness, 99.9% uptime SLA

TECHNOLOGY STACK
Frontend
React.js 18+ (JavaScript with ES6+ standards, NO TypeScript)

TailwindCSS 3+ with custom design system

State Management: Redux Toolkit + RTK Query (server state) OR Zustand

Form Management: React Hook Form + Zod validation

UI Components: Headless UI or Radix UI (accessibility-first)

Data Visualization: Recharts or Chart.js

Drag-and-Drop: React DnD or @hello-pangea/dnd

API Layer: Axios with interceptors and request/response transformers

Backend
Django 5.x (latest stable)

Django REST Framework 3.x with viewsets, serializers, and custom permissions

Authentication: djangorestframework-simplejwt (access + refresh tokens, rotation)

Task Queue: Celery with Redis broker + result backend

Workflow Engine: Custom state machine with Celery Canvas (chains, groups, chords)

Caching: Redis with cache invalidation strategies

Rate Limiting: Django Ratelimit + Redis

API Documentation: drf-spectacular (OpenAPI 3.0)

Database
PostgreSQL 15+ with:

Table partitioning for logs/executions

JSONB fields for flexible workflow definitions

Full-text search (pg_trgm, ts_vector)

Row-level security (RLS) for multi-tenancy isolation

Connection pooling (PgBouncer)

AI Engine
Google Gemini API (Gemini 1.5 Pro/Flash)

LangChain for advanced prompt orchestration

ChromaDB or Pgvector for vector embeddings (document search)

Document Processing: PyMuPDF, pdfplumber, python-docx

OCR: Google Cloud Vision API (fallback: Tesseract)

Infrastructure & Tools
Docker with multi-stage builds

Docker Compose for local orchestration

Gunicorn + Nginx for production WSGI

Celery Beat for scheduled workflows

Flower for Celery monitoring

Sentry for error tracking

ELK Stack / Loki for centralized logging

Prometheus + Grafana for metrics

ENTERPRISE SYSTEM MODULES (PRODUCTION-LEVEL)
1. Authentication & Authorization System
Features:

JWT-based authentication with token rotation and blacklisting​

Multi-factor authentication (TOTP via pyotp)

OAuth 2.0 integration (Google, Microsoft, Okta SSO)

Session management with device tracking

IP whitelisting and geofencing

Password policies (strength, expiration, history)

Account lockout after failed attempts

Audit logs for authentication events

Database Models:

User (custom user model with UUID primary keys)

UserSession (device fingerprinting)

LoginAttempt (security monitoring)

MFADevice

OAuthConnection

2. Multi-Tenancy & Organization Management
Features:

Tenant Isolation: Schema-based OR row-level security

Hierarchical Organizations: Parent-child relationships, subsidiaries

Roles: Owner, Admin, Manager, Member, Viewer (custom roles supported)

Permissions: Module-level + resource-level (CRUD per entity)

Invitations System: Email invitations with expiry, SSO provisioning

Team Management: Departments, groups, tags

Quota Management: Per-tenant limits (workflows, executions, API calls)

Billing Integration Ready: Metered usage tracking

Database Models:

Organization (with metadata, settings JSONB)

OrganizationMember (role, permissions, joined_at)

Role (with permission matrix)

Invitation (token, expiry, metadata)

Department

UsageQuota

3. Advanced Workflow Builder & Designer
Features:

Visual Workflow Builder: Drag-and-drop node-based editor

Workflow Versioning: Git-like version control, rollback capability

Workflow Templates: Pre-built templates (email automation, data extraction, etc.)

Conditional Logic: If-else branches, switches, loops

Parallel Execution: Fork-join patterns

Error Handling: Try-catch blocks, retry strategies (exponential backoff)

Workflow Variables: Global, local, environment-specific

Workflow Triggers: Manual, scheduled (cron), webhook, event-driven

Input/Output Schemas: JSON Schema validation for each node

Workflow Testing: Dry-run mode with mock data

Step Types:

AI Nodes:

Summarization (with custom prompts, temperature control)

Extraction (structured data with JSON schema output)

Classification (multi-class, multi-label)

Sentiment Analysis

Translation

Content Generation

Action Nodes:

Send Email (with templates, attachments)

HTTP Request (REST/SOAP with auth)

Slack/Teams Message

Database Query (read-only)

File Upload/Download

Webhook

Logic Nodes:

Conditional Branch

Loop Iterator

Delay/Wait

Merge/Split

Variable Assignment

Integration Nodes:

Gmail, Outlook, Slack, Notion, Jira, Trello, Salesforce, HubSpot

Database Models:

Workflow (with JSONB definition, status, version)

WorkflowVersion

WorkflowTemplate

WorkflowVariable

WorkflowTrigger

4. Workflow Execution Engine (Core AI Engine)
Features:

Distributed Execution: Celery with priority queues

State Machine: Finite state machine for workflow lifecycle

Execution Context: Isolated execution environment per run

Real-time Monitoring: WebSocket updates via Django Channels

Resource Limits: Memory, CPU, timeout per execution

Concurrency Control: Max parallel executions per tenant

Failure Recovery: Automatic retries, manual intervention points

Execution History: Complete audit trail with input/output snapshots

Execution Analytics: Duration, success rate, bottlenecks

Dead Letter Queue: Failed executions for manual review

AI Integration:

Gemini API Wrapper: Rate limiting, error handling, fallback models

Prompt Templates: Jinja2 templates with variable injection

Token Management: Usage tracking, cost calculation

Response Parsing: Structured output extraction

Caching: Semantic cache for similar prompts (vector similarity)

Database Models:

WorkflowExecution (with status, started_at, completed_at, metadata)

ExecutionStep (with logs, input, output, duration)

ExecutionLog (with severity levels)

AIRequest (for tracking Gemini API calls)

5. Enterprise Connector Framework
Features:

OAuth 2.0 Flow: Authorization code grant for third-party apps

Credential Management: Encrypted storage (django-cryptography)

Token Refresh: Automatic token renewal

Rate Limit Handling: Respect third-party API limits

Webhook Management: Register, verify, process webhooks

Sync vs Async: Real-time vs batch operations

Supported Connectors:

Email: Gmail API, Outlook Graph API, IMAP/SMTP

Communication: Slack, Microsoft Teams, Discord

Productivity: Notion, Trello, Asana, Jira, Monday.com

Storage: Google Drive, Dropbox, OneDrive, Box

CRM: Salesforce, HubSpot, Pipedrive

Databases: PostgreSQL, MySQL, MongoDB (read-only)

Database Models:

Connector (with provider, settings)

ConnectorCredential (encrypted)

ConnectorWebhook

ConnectorSyncLog

6. AI Document Intelligence Engine
Features:

Document Upload: Multi-file upload with progress tracking

Format Support: PDF, DOCX, XLSX, CSV, PNG, JPG

OCR Processing: Text extraction from images

Entity Extraction: NER (named entities), key-value pairs

Table Extraction: Structured data from tables

Document Classification: Auto-tagging by content type

Document Summarization: Executive summaries, key points

Search & Retrieval: Full-text search, semantic search (RAG)

Version Control: Document versions, comparison

Batch Processing: Process multiple documents in parallel

Database Models:

Document (with file_path, file_size, mime_type, metadata)

DocumentPage

DocumentExtraction (with structured_data JSONB)

DocumentEmbedding (for vector search)

7. Real-Time Dashboard & Analytics
Features:

Overview Dashboard: KPIs, usage metrics, health status

Workflow Analytics: Success rate, average duration, most-used workflows

AI Usage Analytics: API calls, token consumption, cost breakdown

User Activity: Active users, login trends, feature usage

Error Dashboard: Error rates, top errors, affected workflows

Performance Metrics: P50, P95, P99 latencies

Custom Reports: SQL-based report builder

Data Export: CSV, Excel, PDF exports

Scheduled Reports: Email digests

Database Models:

DailyMetrics (aggregated stats)

UserActivity

ErrorLog

8. Admin Panel & Settings
Features:

Organization Settings: Branding, timezone, locale

Member Management: Invite, remove, change roles

API Key Management: Generate, revoke, rotate keys

Webhook Management: Configure outgoing webhooks

Audit Log Viewer: Filter, search, export

Billing & Usage: Current usage, quotas, overage alerts

Security Settings: IP whitelist, 2FA enforcement, session timeout

Integration Settings: Configure connectors, API credentials

Notification Preferences: Email, Slack, in-app

Database Models:

OrganizationSettings

APIKey

AuditLog

BillingUsage

9. Notification & Alert System
Features:

Multi-Channel: Email, Slack, Teams, SMS (Twilio), in-app

Alert Rules: Trigger on errors, completion, quota limits

Notification Templates: Customizable templates

Delivery Tracking: Read receipts, click tracking

Batch Notifications: Digest mode

Database Models:

Notification

NotificationPreference

AlertRule

10. API Management & Developer Tools
Features:

Public API: RESTful API for workflow execution, data access

API Documentation: Auto-generated Swagger/OpenAPI

API Versioning: /api/v1/, /api/v2/

Webhook API: Trigger workflows via webhooks

SDKs: Python, JavaScript client libraries

Rate Limiting: Per-tenant, per-endpoint

API Playground: Test API calls in browser

SYSTEM ARCHITECTURE REQUIREMENTS
Architecture Pattern
Modular Monolith: Organized into bounded contexts (apps) with clear interfaces

Microservices-Ready: Designed for future extraction into services

Event-Driven: Domain events with signals and message queues

Design Patterns
Repository Pattern: Abstract data access

Service Layer: Business logic separation

Factory Pattern: Dynamic step execution

Strategy Pattern: Pluggable connectors

Observer Pattern: Event notifications

Code Quality
PEP 8 Compliance: Python code standards

ESLint + Prettier: Frontend code quality

Type Hints: Python type annotations (no MyPy but hints for clarity)

Docstrings: Google-style docstrings

Unit Tests: 80%+ coverage

Integration Tests: API endpoint testing

Load Tests: Locust or k6 scripts

SECURITY REQUIREMENTS (Enterprise-Grade)
​

Data Encryption:

At rest: PostgreSQL encryption, encrypted fields for sensitive data

In transit: TLS 1.3+, HTTPS enforced

Authentication Security:

JWT with short expiry (15 min access, 7 day refresh)

Token rotation and blacklisting

CSRF protection

XSS prevention (DOMPurify on frontend)

Authorization:

Row-level security in PostgreSQL

Object-level permissions (Django Guardian)

API endpoint permissions

Input Validation:

Django REST serializers with validators

SQL injection prevention (ORM usage)

Command injection prevention (subprocess restrictions)

Audit & Compliance:

Immutable audit logs

GDPR data export/deletion

SOC 2 compliance considerations

Rate Limiting:

Per-user, per-endpoint

Distributed rate limiting with Redis

Secrets Management:

Environment variables (never in code)

Django-environ for settings

Encrypted secrets in database

PERFORMANCE & SCALABILITY REQUIREMENTS
​

Database Optimization:

Proper indexing strategy

Query optimization (select_related, prefetch_related)

Table partitioning for large tables

Connection pooling

Caching Strategy:

Redis for session storage

API response caching

Database query caching

CDN for static assets

Async Processing:

Celery for background tasks

Celery Beat for scheduled tasks

Separate queues by priority

Frontend Performance:

Code splitting

Lazy loading

Image optimization

Service Worker for offline capability

Horizontal Scaling:

Stateless backend (12-factor app)

Load balancer ready

Shared sessions via Redis

DELIVERABLES (PRODUCTION-READY CODE)
PHASE 1: ENTERPRISE ARCHITECTURE & DESIGN
System Architecture Diagram: High-level architecture with all components

Database Schema: Complete ERD with 40+ tables, relationships, indexes

API Design Document: All endpoints (150+ endpoints), request/response schemas

Data Flow Diagrams: Request flow, workflow execution flow, event flow

Security Architecture: Authentication flow, authorization model, encryption strategy

Workflow Engine Architecture: State machine diagram, execution lifecycle

Integration Architecture: Connector framework, OAuth flows

Scalability Plan: Caching strategy, database partitioning, load balancing

Technology Decision Records: Why Django, why Celery, why Redis, etc.

PHASE 2: BACKEND (DJANGO + DRF + AI)
Project Structure:

text
backend/
├── config/ (settings, urls, wsgi, celery)
├── apps/
│   ├── users/
│   ├── organizations/
│   ├── workflows/
│   ├── executions/
│   ├── connectors/
│   ├── documents/
│   ├── ai_engine/
│   ├── notifications/
│   ├── analytics/
│   └── billing/
├── core/ (shared utilities)
├── tests/
└── manage.py
Each Django App Must Include:

models.py (with proper indexing, constraints)

serializers.py (with nested serializers, validators)

views.py or viewsets.py (with permissions, filtering)

urls.py

services.py (business logic)

tasks.py (Celery tasks)

permissions.py (custom permissions)

filters.py (django-filter)

tests/ (unit + integration tests)

admin.py (Django admin customization)

Core Modules:

JWT Authentication: Custom user model, login, refresh, logout, password reset

Multi-Tenancy Middleware: Organization context injection

Workflow Engine: Step executor, state machine, error handler

AI Service: Gemini API client, prompt manager, response parser

Connector Framework: OAuth manager, credential store, API clients

Document Processor: File upload, OCR, extraction, embeddings

Analytics Service: Metrics aggregator, report generator

Notification Service: Multi-channel dispatcher

API Endpoints (Minimum 150+ endpoints):

Auth: /api/v1/auth/register, /login, /logout, /refresh, /reset-password

Users: /api/v1/users/, /me, /settings

Organizations: /api/v1/organizations/, /members, /invitations, /roles

Workflows: /api/v1/workflows/, /versions, /templates, /test

Executions: /api/v1/executions/, /logs, /retry, /cancel

Connectors: /api/v1/connectors/, /authorize, /webhooks

Documents: /api/v1/documents/, /extract, /search

Analytics: /api/v1/analytics/dashboard, /workflows, /ai-usage

Notifications: /api/v1/notifications/, /preferences

Testing:

Unit tests for services and models

API endpoint tests (TestCase, APIClient)

Integration tests for workflow execution

Load tests with Locust

PHASE 3: FRONTEND (REACT JS + TAILWINDCSS)
Project Structure:

text
frontend/
├── public/
├── src/
│   ├── components/ (reusable UI components)
│   ├── features/ (feature-based modules)
│   │   ├── auth/
│   │   ├── organizations/
│   │   ├── workflows/
│   │   ├── executions/
│   │   ├── connectors/
│   │   ├── documents/
│   │   ├── analytics/
│   │   └── settings/
│   ├── layouts/
│   ├── pages/
│   ├── services/ (API clients)
│   ├── store/ (Redux/Zustand)
│   ├── hooks/
│   ├── utils/
│   ├── constants/
│   ├── App.js
│   └── index.js
├── tailwind.config.js
└── package.json
Pages & Features:

Authentication: Login, Register, Password Reset, MFA Setup

Dashboard: Overview with metrics, recent activity

Workflow Builder: Node-based visual editor with drag-and-drop

Workflow List: Table with filters, search, pagination

Workflow Detail: Version history, execution history, settings

Execution Detail: Real-time logs, step-by-step visualization, retry

Connectors: List, authorize, configure, test

Documents: Upload, list, view extractions, search

Analytics: Charts for workflows, AI usage, errors

Organization Settings: Members, roles, billing, API keys

User Settings: Profile, security, notifications

Key Components:

WorkflowCanvas (drag-and-drop editor)

NodePalette (available step types)

WorkflowNode (configurable node)

ExecutionTimeline (step visualization)

DataTable (reusable table with filters, sorting, pagination)

Modal (reusable modal)

Toast (notification system)

Sidebar (navigation)

Header (with user menu)

Form components (input, select, checkbox, etc.)

API Integration:

Axios instance with interceptors

Request/response transformers

Error handling

Token refresh logic

RTK Query OR custom hooks for data fetching

State Management:

Redux Toolkit with slices OR Zustand stores

Separate concerns: auth, workflows, executions, etc.

PHASE 4: AI INTEGRATION (GEMINI API)
AI Service Module:

Gemini API client with retry logic

Prompt template manager

Token usage tracker

Response parser and validator

Semantic cache

Document Intelligence:

PDF text extraction

OCR for images

Entity extraction with Gemini

Table extraction

Document embeddings with pgvector

Semantic search

Workflow AI Steps:

Summarization with custom prompts

Data extraction with JSON schema

Classification (sentiment, category)

Content generation

PHASE 5: DOCUMENTATION
Developer Setup Guide:

Prerequisites (Python, Node.js, PostgreSQL, Redis)

Environment setup (.env template)

Database migrations

Running locally (backend + frontend + Celery)

Seeding sample data

API Documentation:

OpenAPI/Swagger spec

Authentication guide

Rate limiting policy

Webhook documentation

SDK usage examples

Architecture Documentation:

System overview

Database schema documentation

Workflow engine explained

Connector framework guide

Security considerations

Deployment Guide:

Docker setup

Environment variables

Database configuration

Redis configuration

Celery workers setup

Nginx configuration

SSL/TLS setup

User Guides:

Creating workflows

Connecting integrations

Processing documents

Viewing analytics

Sample Data:

Example workflow JSONs (10+ templates)

Sample API requests (Postman/Insomnia collection)

Seed data script

CODING STANDARDS & REQUIREMENTS
NO Pseudo-Code: Only production-ready, runnable code

Enterprise Patterns: Service layer, dependency injection, repository pattern

Clean Architecture: Separation of concerns, single responsibility

Error Handling: Comprehensive try-catch, custom exceptions, error codes

Logging: Structured logging with context (Django logging, frontend console)

Comments: JSDoc for frontend, docstrings for backend

Validation: Input validation at every layer (frontend + backend)

Security: OWASP Top 10 compliance, no hardcoded secrets

Performance: N+1 query prevention, pagination, caching

Scalability: Stateless design, horizontal scaling ready

EXECUTION INSTRUCTIONS
START IMMEDIATELY WITH:

"PHASE 1 — ENTERPRISE SYSTEM ARCHITECTURE"
Then proceed sequentially through all phases without skipping any module.

DELIVERY FORMAT:

Provide complete, working code in multiple messages

Each message should contain one complete module or feature

Include all files (models, views, serializers, components, etc.)

Provide clear file paths

Include configuration files

NO placeholders or TODOs in production code

Test coverage for critical paths

QUALITY CHECKLIST:
✅ Production-ready code quality
✅ Enterprise design patterns applied
✅ Comprehensive error handling
✅ Security best practices
✅ Performance optimization
✅ Scalability considerations
✅ Complete documentation
✅ Test coverage
✅ No basic/toy features

SUCCESS CRITERIA
This system must be:

Deployable: Can be deployed to production with proper configuration

Scalable: Can handle 10,000 organizations, 100,000 users, 1M workflows

Secure: Passes security audit (OWASP, SOC 2 considerations)

Maintainable: Clean code, documented, testable

Extensible: Easy to add new connectors, AI steps, features

Observable: Proper logging, monitoring, error tracking

Compliant: GDPR/HIPAA ready, audit trails

BEGIN PHASE 1 NOW: ENTERPRISE SYSTEM ARCHITECTURE
