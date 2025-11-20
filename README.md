# FlowPilot AI - Enterprise AI Workflow Automation Platform

A production-ready, horizontally scalable SaaS platform enabling enterprises to design, deploy, and orchestrate AI-powered workflow automations with real-time execution, comprehensive audit trails, and enterprise-grade security.

## Features

- **Advanced Workflow Builder**: Visual drag-and-drop workflow designer with versioning
- **AI-Powered Automation**: Google Gemini API integration for intelligent document processing
- **Multi-Tenancy**: Enterprise-grade organization management with role-based access control
- **Real-time Execution**: WebSocket-based real-time workflow execution monitoring
- **Enterprise Connectors**: OAuth 2.0 integrations with Gmail, Slack, Salesforce, and more
- **Document Intelligence**: OCR, entity extraction, semantic search with pgvector
- **Comprehensive Analytics**: Real-time dashboards and usage metrics
- **SOC 2 Ready**: Audit logs, encryption, and compliance features

## Tech Stack

### Backend
- Django 5.x + Django REST Framework
- PostgreSQL 15+ with pgvector
- Redis (caching, sessions, Celery broker)
- Celery + Celery Beat
- Django Channels (WebSockets)
- Google Gemini API

### Frontend
- React.js 18+
- TailwindCSS 3+
- Redux Toolkit / Zustand
- React Hook Form + Zod

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (recommended)

### Local Development with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/flowpilot-ai.git
   cd flowpilot-ai
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys and configuration
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Run migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

6. **Access the application**
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - API Docs: http://localhost:8000/api/docs
   - Flower (Celery): http://localhost:5555

## Project Structure

```
flowpilot-ai/
├── backend/
│   ├── config/              # Django settings and configuration
│   ├── apps/                # Django applications
│   │   ├── users/           # User authentication and management
│   │   ├── organizations/   # Multi-tenancy and organizations
│   │   ├── workflows/       # Workflow builder and management
│   │   ├── executions/      # Workflow execution engine
│   │   ├── ai_engine/       # AI service integration
│   │   ├── connectors/      # Third-party integrations
│   │   ├── documents/       # Document intelligence engine
│   │   ├── notifications/   # Multi-channel notifications
│   │   ├── analytics/       # Analytics and reporting
│   │   └── billing/         # Usage tracking and quotas
│   ├── core/                # Shared utilities
│   └── tests/               # Integration and load tests
├── frontend/                # React.js frontend (to be implemented)
├── docs/                    # Documentation
├── docker-compose.yml       # Docker Compose configuration
└── README.md
```

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **OpenAPI Schema**: http://localhost:8000/api/schema

## License

This project is proprietary software. All rights reserved.