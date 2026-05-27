# Django Backend Learning Roadmap

This roadmap tracks the learning chunks that build on the current `learning` app.
Each chunk is sized so you can copy just the feature you need into another project.

## 0. Current Chunk (in repo now)
- Request lifecycle basics: URL routing, views, and responses.
- Security basics: CSRF protection, safe JSON parsing, and minimal headers.
- Data consistency: model validation with `full_clean()` and transactional writes.
- Efficiency: pagination with guardrails and narrow querysets.
- Testing: CSRF-aware API tests.

## 1. Authentication and Authorization
- Session auth vs token auth and when to use each.
- Login, logout, and protected endpoints.
- Permissions and object-level access patterns.

## 2. API Design Fundamentals
- Pagination metadata patterns (next/prev cursors).
- Filtering and sorting with safe allowlists.
- Versioning strategies and deprecation etiquette.

## 3. Data Modeling and Migrations
- Indexes, unique constraints, and data migrations.
- Soft deletes vs hard deletes.
- Relationship modeling (one-to-many, many-to-many).

## 4. Error Handling and Observability
- Structured logging and request IDs.
- Centralized exception handling middleware.
- Health checks and readiness probes.

## 5. Background Jobs and Async Work
- Task queues (Celery/RQ) and retries.
- Idempotency keys for safe retries.
- Scheduled tasks and cleanup jobs.

## 6. Performance and Caching
- Query profiling and N+1 fixes.
- Caching layers and cache invalidation basics.
- Static/media storage strategies.

## 7. Security Hardening
- Security headers and CSP.
- Rate limiting and brute-force protection.
- Secrets management and environment isolation.

## 8. Deployment and Operations
- Environments, settings separation, and 12-factor.
- Database backups and migrations in CI/CD.
- Monitoring, alerting, and incident response.

