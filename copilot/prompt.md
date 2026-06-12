# Project Objective and Change Summary
### used by copilot

## Objective
Build a beginner-friendly Django backend learning playground with copy-pasteable features. Each feature is small, documented, and focused on secure, consistent, and efficient backend patterns.

## Current Status (as of June 2026)
**Completed Chunks:** 0, 1, 2
**Chunks In Progress:** None
**Next Planned Chunks:** 3 (Data Modeling), 4 (Error Handling), 5+ (Async, Caching, Security, Deployment)

## What Exists Now
- A minimal Django project in `boilerplate/` with a `learning` app.
- **Chunk 0:** A small Notes API (CRUD, validation, transactions, pagination).
- **Chunk 1:** User registration, login, logout, and session auth with custom backends.
- **Chunk 2:** Safe filtering, sorting, and cursor-based pagination.
- Comprehensive tests for all chunks.
- Roadmap-driven documentation for future learning chunks.

## Key Additions and Updates (Chunks 1 & 2)

### New Files (Chunk 1 & 2)
- **`learning/auth_backends.py`:** Custom authentication backends.
  - `SimpleEmailBackend`: Email-based login (alternative to username).
  - `TokenBackend`: Token-based auth (API keys, JWT patterns).
- **`learning/permissions.py`:** Permission helpers and authorization patterns.
  - `is_authenticated()`, `is_owner()`, `is_staff()`, `has_group()`.
  - `PermissionMixin` for class-based permission checks.
  - Pre-defined permission sets.
- **`learning/serializers.py`:** API design patterns.
  - `NoteSerializer`: Versioned output and field filtering.
  - `AllowlistValidator`: Safe filtering and sorting (prevents SQL injection).
  - API versioning constants and helpers.

### Updated Files (Chunk 1 & 2)
- **`learning/views.py`:** Added 7 new endpoints.
  - Chunk 1: `login_view`, `logout_view`, `current_user_view`, `create_user_view`.
  - Chunk 2: `notes_collection` (enhanced with filters/sorting), `notes_with_cursor_pagination`, `my_notes_view`.
  - All endpoints have extensive block-level comments and flow diagrams.
- **`learning/urls.py`:** Added routes for all new endpoints.
  - Organized by chunk for clarity.
- **`learning/tests.py`:** Added 30+ new test cases.
  - `AuthenticationTests`: Registration, login, logout, session auth, protected endpoints.
  - `NotesFilteringAndSortingTests`: Filtering, sorting, pagination, cursor pagination, SQL injection prevention.
- **`boilerplate/settings.py`:** Registered custom authentication backends.
  - `AUTHENTICATION_BACKENDS` configuration.

## Current Learning Chunks Implemented

### Chunk 0 (Request & Consistency Basics)
✅ **COMPLETED**
- CRUD endpoints with safe JSON parsing and CSRF protection.
- Model validation and transactional writes.
- Bounded pagination and narrow querysets.
- Tests with CSRF checks.

### Chunk 1 (Authentication and Authorization)
✅ **COMPLETED**
- Custom email-based and token-based auth backends.
- User registration with password validation.
- Login, logout, and session management.
- Protected endpoints requiring authentication.
- Permission helpers for access control.
- Tests covering all auth scenarios (valid/invalid credentials, registration, logout).

### Chunk 2 (API Design Fundamentals)
✅ **COMPLETED**
- Safe filtering by title and archive status (allowlist pattern).
- Sorting by title and created_at (prevents SQL injection).
- Offset pagination with bounds checking and capped limits.
- Cursor-based pagination for stable scrolling.
- API versioning headers and deprecated version tracking.
- Tests covering filters, sorts, pagination edge cases, SQL injection attempts.

## Next Chunks (Planned)
3. **Data Modeling and Migrations** – Indexes, constraints, soft deletes, relationships.
4. **Error Handling and Observability** – Structured logging, request IDs, health checks.
5. **Background Jobs and Async Work** – Task queues, retries, idempotency.
6. **Performance and Caching** – Query profiling, caching layers, invalidation.
7. **Security Hardening** – Security headers, rate limiting, secrets management.
8. **Deployment and Operations** – Environments, CI/CD, monitoring, incident response.

## API Endpoints (Current)

### Chunk 0: CRUD & Consistency
- `GET /api/health/` – Health check for load balancers.
- `GET /api/notes/` – List all non-archived notes (supports limit, offset, title filter, sort, include_archived).
- `POST /api/notes/` – Create a new note (requires CSRF token, validated JSON).
- `POST /api/notes/<id>/archive/` – Archive a note (requires CSRF token).
- `POST /api/transactions/` – Transactional forwarding with idempotency.

### Chunk 1: Auth
- `POST /api/register/` – Register new user (email, password, first_name).
- `POST /api/login/` – Login via email and password (creates session).
- `POST /api/logout/` – Logout and clear session.
- `GET /api/me/` – Get current authenticated user.

### Chunk 2: Filtering & Pagination
- `GET /api/notes/` – Enhanced with ?title=X&sort=field&limit=10&offset=0.
- `GET /api/notes-cursor/` – Cursor-based pagination with ?cursor=X&limit=10.
- `GET /api/my-notes/` – List authenticated user's notes (protected endpoint).

## How to Run (Minimal)
```powershell
cd C:\Users\praty\PycharmProjects\django-backend\boilerplate
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r ..\requirements.txt
python manage.py migrate
python manage.py runserver
```

## How to Run Tests
```powershell
cd C:\Users\praty\PycharmProjects\django-backend\boilerplate
python manage.py test learning
```

## Documentation for Developers
- **`roadmap.md`:** Detailed chunk-by-chunk roadmap with feature overviews, key files, and control flow diagrams.
- **`django-init.txt`:** Concise file descriptions for the entire project.
- **Code Comments:** Every file has block-level comments explaining purpose, flow, and patterns.


