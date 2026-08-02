# Candidate Screening Platform

A full-stack web application that lets recruiters post and manage jobs, and lets candidates browse openings and apply. Built with Django + DRF (backend) and React + Vite (frontend).

## Quick Start

### Prerequisites
- Python 3.11+
- Node 18+
- Docker (for PostgreSQL and MinIO)

### 1. Start PostgreSQL and MinIO
```bash
docker compose up -d db minio
```

The MinIO API runs at `http://localhost:9000`; its console is at
`http://localhost:9001` (`minioadmin` / `minioadmin123` for local development).
The resume bucket is created automatically on the first upload.

### 2. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to a Gmail address and app password.
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
| [IMPLEMENTATION-TODO.md](docs/IMPLEMENTATION-TODO.md) | Email verification and file-upload implementation record |
| [email-file-upload-workflow.md](docs/email-file-upload-workflow.md) | Email and storage workflow notes |
| [project-workflow.md](docs/project-workflow.md) | Project development workflow |

## Email verification

Registration sends a 24-hour verification link through the configured SMTP
account. For Gmail, enable two-step verification and create an app password,
then set `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `DEFAULT_FROM_EMAIL` in
`backend/.env`. Status changes also email the candidate. Email failures are
logged and do not roll back registration or application status updates.

For local development without SMTP, set:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Resume uploads

Candidates can upload PDF, DOC, and DOCX resumes up to 5 MB. Files are stored
in the private MinIO bucket and application-list responses contain short-lived
presigned download links. Storage credentials and limits are documented in
`backend/.env.example` and `frontend/.env.example`.
