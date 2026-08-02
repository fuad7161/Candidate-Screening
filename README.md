# Candidate Screening Platform

A hiring platform that brings recruiters and job seekers together in one place.
Recruiters can publish jobs, review applicants, and move candidates through the
hiring process. Candidates can discover opportunities, upload a resume, apply,
and follow the progress of their applications.

## Key Features

- Separate accounts and experiences for recruiters and candidates
- Email verification during account registration
- Public job browsing with detailed job information
- Recruiter dashboard for creating, editing, and closing job posts
- Simple resume uploads for PDF, DOC, and DOCX files
- Quick job applications with an optional cover note
- Personal application tracker for candidates
- Applicant review area for recruiters
- Clear application stages: Applied, Shortlisted, Interview, Hired, or Rejected
- Email notifications when an application status changes
- Secure access so users only see and manage information relevant to them
- Mobile-friendly interface with clear loading, success, and error messages

For a complete manual testing checklist, see
[FEATURE-LIST.md](docs/FEATURE-LIST.md).

## Technology

Built with Django and Django REST Framework for the backend, React and Vite for
the frontend, PostgreSQL for application data, and MinIO for resume storage.

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
| [FEATURE-LIST.md](docs/FEATURE-LIST.md) | Complete feature and manual testing checklist |
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
