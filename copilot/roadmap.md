### used by copilot
# Django Backend Learning Roadmap

This roadmap grows the `learning` app into a set of copy-paste friendly features.
Each chunk is intentionally small so you can lift it into another project.

## 0. COMPLETED - Request & Consistency Basics
**Overview:** Build a simple safe CRUD API with validation and transactions.

**Features:**
- Request lifecycle basics: URL routing, views, and JSON responses.
- Security basics: CSRF protection and safe JSON parsing.
- Data consistency: model validation with `full_clean()` and transactional writes.
- Efficiency basics: bounded pagination and narrow querysets.
- Testing: CSRF-aware API tests for JSON endpoints.

**Key Files:**
- `learning/models.py`: Note model with timestamps.
- `learning/views.py`: REST endpoints (list, create, archive).
- `learning/services.py`: Business logic and transactions.
- `learning/validators.py`: Input validation.
- `learning/utils.py`: Helper functions (JSON parsing, pagination).
- `learning/urls.py`: Chunk 0 routes.
- `learning/tests.py`: Chunk 0 tests.

**Flow Order (Read):** URL -> view (parse GET params) -> filter/sort -> paginate -> serialize -> response.
**Flow Order (Write):** URL -> view (parse JSON) -> validate -> service (transaction) -> model -> response.

**Control Flow:**
```
CHUNK 0 READ:
GET /api/notes/ -> notes_collection() -> list_notes() -> paginate_queryset() -> serialize_note() -> JsonResponse

CHUNK 0 WRITE:
POST /api/notes/ -> notes_collection() -> parse_json_body() -> validate_note_payload() ->
  create_note() [transaction] -> model.save() -> serialize_note() -> JsonResponse
```

---

## 1. COMPLETED - Authentication and Authorization
**Overview:** Implement user login, registration, and permission checks.

**Features:**
- Custom email-based authentication backend (SimpleEmailBackend).
- Token-based authentication backend (TokenBackend).
- User registration with password validation.
- Login and logout with session creation.
- Protected endpoints that check authentication.
- Permission helpers: `is_authenticated()`, `is_owner()`, `is_staff()`.
- Object-level access control mixin.

**Key Files:**
- `learning/auth_backends.py`: Custom auth backends.
- `learning/permissions.py`: Permission helpers and checks.
- `learning/views.py`: Chunk 1 endpoints (login, logout, register, current_user).
- `boilerplate/settings.py`: AUTHENTICATION_BACKENDS configuration.
- `learning/tests.py`: Chunk 1 tests (registration, login, logout, auth checks).
- `learning/urls.py`: Chunk 1 routes.

**Flow Order:** URL -> middleware -> CSRF check -> parse JSON -> authenticate() -> login()/view -> permission check -> response.

**Control Flow:**
```
CHUNK 1 REGISTER:
POST /api/register/ -> CSRF -> create_user_view() -> validate email/password ->
  User.objects.create_user() -> login(request, user) -> JsonResponse

CHUNK 1 LOGIN:
POST /api/login/ -> CSRF -> login_view() -> parse JSON -> authenticate(email, password) [runs auth backends] ->
  SimpleEmailBackend.authenticate() -> User check -> login(request, user) -> JsonResponse

CHUNK 1 PROTECTED:
GET /api/my-notes/ -> my_notes_view() -> is_authenticated(request.user) -> return notes or 401
```

---

## 2. COMPLETED - API Design Fundamentals
**Overview:** Add safe filtering, sorting, and pagination improvements.

**Features:**
- Safe filtering with allowlist pattern (prevents SQL injection).
- Sorting by specific fields (prevents malicious SQL).
- Improved offset pagination with bounds checking.
- Cursor-based pagination for stable scrolling.
- API versioning with version headers.
- Serializers for schema transformation and field filtering.
- Deprecated version tracking.

**Key Files:**
- `learning/serializers.py`: NoteSerializer, AllowlistValidator, versioning helpers.
- `learning/views.py`: Chunk 2 endpoints (notes_collection enhanced, notes_with_cursor_pagination, my_notes_view).
- `learning/utils.py`: Pagination and parameter coercion (already supports limits).
- `learning/tests.py`: Chunk 2 tests (filtering, sorting, cursor pagination, validations).
- `learning/urls.py`: Chunk 2 routes.

**Flow Order:** URL -> view (extract params) -> allowlist validation -> queryset.filter().order_by() -> paginate -> serialize -> response.

**Control Flow:**
```
CHUNK 2 READ WITH FILTERS:
GET /api/notes/?title=python&sort=-created_at&limit=10&offset=0 -> notes_collection() ->
  coerce_positive_int() -> AllowlistValidator.validate_sort() ->
  list_notes(**filters) -> order_by(sort_param) -> paginate_queryset() ->
  serialize_note() -> JsonResponse

CHUNK 2 CURSOR PAGINATION:
GET /api/notes-cursor/?limit=10&cursor=last_id -> notes_with_cursor_pagination() ->
  decode cursor -> Note.objects.filter(id__gt=cursor).order_by('id') ->
  slice(limit+1) -> determine next_cursor -> JsonResponse with next_cursor
```

---

## 3. Data Modeling and Migrations
- Indexes, unique constraints, and data migrations.
- Soft deletes vs hard deletes.
- Relationship modeling (one-to-many, many-to-many).
- Flow order: model change -> migration -> database -> queryset -> view -> response.

## 4. Error Handling and Observability
- Structured logging and request IDs.
- Centralized exception handling middleware.
- Health checks and readiness probes.
- Flow order: request -> middleware -> view -> logger/metrics -> response.

## 5. Background Jobs and Async Work
- Task queues (Celery/RQ) and retries.
- Idempotency keys for safe retries.
- Scheduled tasks and cleanup jobs.
- Flow order: request -> enqueue task -> worker -> data write -> status lookup.

## 6. Performance and Caching
- Query profiling and N+1 fixes.
- Caching layers and cache invalidation basics.
- Static/media storage strategies.
- Flow order: request -> cache lookup -> queryset -> cache fill -> response.

## 7. Security Hardening
- Security headers and CSP.
- Rate limiting and brute-force protection.
- Secrets management and environment isolation.
- Flow order: request -> security middleware -> view -> response headers.

## 8. Deployment and Operations
- Environments, settings separation, and 12-factor.
- Database backups and migrations in CI/CD.
- Monitoring, alerting, and incident response.
- Flow order: build -> migrate -> serve -> monitor -> alert -> recover.

