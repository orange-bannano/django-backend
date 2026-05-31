### used by copilot
# Django Backend Learning Roadmap

This roadmap grows the `learning` app into a set of copy-paste friendly features.
Each chunk is intentionally small so you can lift it into another project.

## 0. Current Chunk (in repo now)
- Request lifecycle basics: URL routing, views, and JSON responses.
- Security basics: CSRF protection and safe JSON parsing.
- Data consistency: model validation with `full_clean()` and transactional writes.
- Efficiency basics: bounded pagination and narrow querysets.
- Testing: CSRF-aware API tests for JSON endpoints.
- Flow order (read): URL -> view -> utils -> services -> model -> response.
- Flow order (write): URL -> view -> utils -> validators -> services -> model -> response.

## 1. Authentication and Authorization
- Session auth vs token auth and when to use each.
- Login, logout, and protected endpoints.
- Permissions and object-level access patterns.
- Flow order: URL -> middleware -> auth backend -> view -> permission checks -> response.

## 2. API Design Fundamentals
- Filtering and sorting with safe allowlists.
- Stable pagination with cursors and link headers.
- Versioning strategies and deprecation etiquette.
- Flow order: URL -> view -> allowlist validation -> queryset -> serializer -> response.

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

