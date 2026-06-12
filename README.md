## For business logic:
## [VIEW](boilerplate/learning/views.py)
## [SETTINGS](boilerplate/boilerplate/settings.py)

# django-backend

This repository is part of the Internship project @ [Samaro AI](https://samaro.ai/)
It includes a compact backend web development knowledge base & code focused on best practices and habits to ensure efficency and security.
Refer the [progress sheet](https://docs.google.com/spreadsheets/d/1VsqfiaUyQ_vsXXupU7ZZjFJQfqHpv41TX4E4Je0PoqM/edit?gid=0#gid=0) for currents status and milestones of this project.

## Learning App Quickstart

The `boilerplate` folder contains a minimal Django project with a `learning` app.
It demonstrates the practical example of critcical backend web service concepts (discussed below).

## The API usage details of the endpoint view within this project can be found [here](docs/apiDoc.md)

### Quickstart (from repo root)
```powershell
cd C:\Users\praty\PycharmProjects\django-backend\boilerplate
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r ..\requirements.txt
python manage.py migrate
python manage.py runserver
```

## Theory documentation Overview

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
