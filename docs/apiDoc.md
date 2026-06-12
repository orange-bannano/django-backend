# Django Starter Project — API Documentation

A RESTful API backend built with **Django** for a notes management application. Supports user registration, authentication (session-based), note CRUD operations, password management, and permission group management.

---

## Base URL

```
http://127.0.0.1:8000
```

> Replace with your deployed server URL in production.

---

## Authentication

Most endpoints require **HTTP Basic Authentication**.

```
Authorization: Basic <base64(email:password)>
```

Endpoints that do **not** require authentication: `Register`, `Login`.

---

## Endpoint Summary

| # | Name            | Method | Endpoint               | Auth Required |
|---|-----------------|--------|------------------------|---------------|
| 1 | Create User     | POST   | `/api/register/`       | No            |
| 2 | Login           | POST   | `/api/login/`          | No            |
| 3 | Logout          | POST   | `/api/logout/`         | Yes           |
| 4 | Current User    | GET    | `/api/me/`             | Yes           |
| 5 | Update Password | POST   | `/api/reset/`          | Yes           |
| 6 | Delete Account  | POST   | `/api/delete/`         | Yes           |
| 7 | Get Notes       | GET    | `/api/notes/`          | Yes           |
| 8 | Create Note     | POST   | `/api/notes/`          | Yes           |
| 9 | Update Note     | PUT    | `/api/notes/`          | Yes           |
|10 | Delete Note     | DELETE | `/api/notes/`          | Yes           |
|11 | Create Group    | POST   | `/api/register-group/` | Yes           |

---

## Auth

### 1. Register (Create User)
- **POST** `/api/register/`
```json
{ "email": "newuser@example.com", "password": "secret", "first_name": "Alice" }
```

### 2. Login
- **POST** `/api/login/`
```json
{ "email": "soham@123.com", "password": "soham" }
```

### 3. Logout
- **POST** `/api/logout/` — Auth required

### 4. Current User
- **GET** `/api/me/` — Auth required

---

## Account Management

### 5. Update Password
- **POST** `/api/reset/` — Auth required
```json
{ "password": "new-secret123" }
```

### 6. Delete Account
- **POST** `/api/delete/` — Auth required ⚠️ Irreversible

---

## Notes

### 7. Get Notes
- **GET** `/api/notes/` — Auth required
- Query params: `limit`, `offset`, `sort` (prefix `-` for desc), `title` (repeatable), `include_archived=1`

### 8. Create Note
- **POST** `/api/notes/` — Auth required
```json
{ "title": "Django ORM basics", "body": "Review select_related and prefetch_related." }
```

### 9. Update Note
- **PUT** `/api/notes/` — Auth required
```json
{ "note_id": 3, "title": "Updated title", "body": "Updated body" }
```

### 10. Delete Note
- **DELETE** `/api/notes/` — Auth required
```json
{ "note_id": 12 }
```

---

## Groups

### 11. Create Group
- **POST** `/api/register-group/` — Auth required
```json
{ "group": "Editor", "permission": ["view_note", "add_note", "change_note"] }
```
