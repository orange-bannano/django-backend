# Project Objective and Change Summary
### used by copilot
## Objective
Build a beginner-friendly Django backend learning playground with copy-pasteable features. Each feature is small, documented, and focused on secure, consistent, and efficient backend patterns.

## What Exists Now
- A minimal Django project in `boilerplate/` with a `learning` app.
- A small Notes API that demonstrates safe JSON handling, CSRF-protected POSTs, model validation, transactions, pagination, and tests.
- Roadmap-driven documentation for future learning chunks.

## Key Additions and Updates
- **New `learning` app** under `boilerplate/learning/` with clear separation of concerns:
  - `models.py`: `Note` model with timestamps and archive flag.
  - `views.py`: JSON endpoints with CSRF protection and input validation.
  - `services.py`: transactional write logic and row locking for consistency.
  - `validators.py`: explicit payload validation.
  - `utils.py`: safe JSON parsing and pagination helpers.
  - `urls.py`: app-level routing.
  - `tests.py`: CSRF-aware API tests.
  - `admin.py`: admin registration for notes.
  - `migrations/0001_initial.py`: schema creation.

- **Project wiring**:
  - `boilerplate/boilerplate/settings.py`: registers the `learning` app.
  - `boilerplate/boilerplate/urls.py`: routes `/api/` to the learning app.

- **Docs and guidance**:
  - `roadmap.md`: updated with chunk-by-chunk flow order (control/data flow per chunk).
  - `README.md`: quickstart and endpoint summary for the learning app.
  - `django-init.txt`: expanded with concise file descriptions for the project.

## Current Learning Chunk (Chunk 0)
- Request lifecycle basics (routing, views, JSON responses).
- Security basics (CSRF, safe JSON parsing).
- Consistency (model validation, transactions).
- Efficiency basics (bounded pagination, narrow querysets).
- Testing (CSRF-aware API tests).

## Next Chunks (Planned)
1. Authentication and Authorization.
2. API Design Fundamentals.
3. Data Modeling and Migrations.
4. Error Handling and Observability.
5. Background Jobs and Async Work.
6. Performance and Caching.
7. Security Hardening.
8. Deployment and Operations.

## How to Run (Minimal)
```powershell
cd C:\Users\praty\PycharmProjects\django-backend\boilerplate
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r ..\requirements.txt
python manage.py migrate
python manage.py runserver
```

## API Endpoints
- `GET /api/health/`
- `GET /api/notes/`
- `POST /api/notes/`
- `POST /api/notes/<id>/archive/`

