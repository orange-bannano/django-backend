# django-backend

This repository now includes a compact backend web development knowledge base focused on practical concepts, definitions, and secure implementation habits.

## Documentation Overview

### 1. [HTTP and Web Backend Basics](docs/01-http-and-web-basics.md)
Covers HTTP communication, request/response structure, methods such as GET/POST/PUT/PATCH/DELETE, idempotency, status codes, headers, and content negotiation.

### 2. [REST API Design and OpenAPI](docs/02-api-design-and-rest.md)
Explains REST API principles, resource modeling, filtering, sorting, pagination, partial loading, validation, serialization, OpenAPI, and versioning.

### 3. [Architecture Patterns: MVC, MVT, and Backend Structure](docs/03-architecture-and-django-patterns.md)
Describes MVC and Django's MVT pattern, separation of concerns, authentication vs authorization, request lifecycle, and caching basics.

### 4. [Data Consistency, Transactions, and Async Operations](docs/04-data-consistency-and-async.md)
Introduces transactions, ACID guarantees, concurrency concerns, asynchronous processing, background jobs, and retry strategies.

### 5. [Backend Security Basics](docs/05-security-basics.md)
Summarizes JWT, refresh tokens, session cookies including JSESSIONID, CSRF tokens, throttling, rate limiting, security headers, common injection vulnerabilities, and authentication hardening.

## Suggested Reading Order

1. Start with HTTP basics.
2. Move to REST and API design.
3. Understand architecture patterns used in backend frameworks such as Django.
4. Learn data consistency and async processing.
5. Finish with core security practices and common vulnerabilities.

## Purpose

These documents are meant to give a structured reference for backend fundamentals and common secure-development practices that are useful across Django and general web backend work.