# Candidate Screening Platform

A full-stack web application that lets recruiters post and manage jobs, and lets candidates browse openings and apply. Built with Django + DRF (backend) and React + Vite (frontend).

## Quick Start

### Prerequisites
- Python 3.11+
- Node 18+
- Docker (for PostgreSQL)

### 1. Start the database
```bash
docker compose up -d db
```

### 2. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver   # http://localhost:8000
```

### 3. Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev                  # http://localhost:5173
```

## Documentation

See the [docs/](docs/) folder for detailed documentation:

| File | Purpose |
|------|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, request flow, design decisions |
| [DATABASE.md](docs/DATABASE.md) | ER model, table schemas, relationships |
| [API.md](docs/API.md) | REST endpoint reference (routes, payloads, status codes) |
| [FRONTEND.md](docs/FRONTEND.md) | Pages, components, routing, state management plan |
| [WORKFLOW.md](docs/WORKFLOW.md) | Git workflow, environment setup, dev process |
| [SUBMISSION.md](docs/SUBMISSION.md) | Architecture overview + write-up template |
