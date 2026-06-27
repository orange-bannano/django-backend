# django-backend

Aim: To provides a template for constructing a web service using **vanilla Django framework**, easy to copy and paste.
Objective: Serve as a prerequisite and learning opportunity to understand cybersecurity implementations

Instead of using Django Rest Framework (DRF) or other third-party libraries, this project focuses on implementing the backend logic using only the built-in features of Django.
This approach allows developers to gain a deeper understanding of how thing works under the hood.

This repository is part of the Internship project @ [Samaro AI](https://samaro.ai/)
Refer the [progress sheet](https://docs.google.com/spreadsheets/d/1VsqfiaUyQ_vsXXupU7ZZjFJQfqHpv41TX4E4Je0PoqM/edit?gid=0#gid=0) for currents status, features and milestones of this project.

## Learning App Quickstart

Code includes a compact backend web development knowledge base focused on best practices.
The `boilerplate` (project) folder contains a minimal Django project with a `learning` app.

### The API usage details of the endpoint view within this project can be found [here](docs/apiDoc.md) and sample request/response [here](docs/django.postman_collection.json)

### Overview
The web app serve an office memorandum management system, allowing users to create, read, update, and delete (CRUD) memos (Notes).
It also includes user authentication and authorization features by implementing user roles, which are:
'Employee' = can view/modify owned notes,
'Manager' = can view/modify employee and owned notes but not of other managers,
'Admin' = can view/modify/delete all notes.
Any authenticated user can add.

### Quickstart

Fresh start? Refer [Project Initialization](django-init.txt) and [MySQL DB and Redis cache setup](setupCommands.txt)

```
git clone https://github.com/orange-bannano/django-backend.git
cd \boilerplate\
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r ..\requirements.txt
python manage.py migrate
python manage.py runserver
```

## For business logic:
### [VIEWS DEALING WITH CRUD AND FEATURES](boilerplate/learning/views.py)
### [VIEWS DEALING WITH AUTHENTICATION](boilerplate/learning/auth_views.py)
### [MODELS](boilerplate/learning/models.py)
### [SETTINGS](boilerplate/boilerplate/settings.py)
Other file are helper, making the logic more comprehensive, explore them as you need ie, as you read thought above views.
Logic, instructions and customizations are documented within the code file using comments, online docs and spacing.

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
