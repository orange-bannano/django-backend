# Architecture Patterns: MVC, MVT, and Backend Structure

This file explains common server-side architecture patterns and where Django fits.

## MVC

### Definition
MVC stands for Model-View-Controller.

### Responsibilities
- **Model:** Handles data and business rules.
- **View:** Renders the user interface.
- **Controller:** Accepts input and coordinates between model and view.

### Why It Matters
MVC separates concerns so code is easier to test, understand, and maintain.

## MVT

### Definition
MVT stands for Model-View-Template and is the pattern commonly associated with Django.

### Responsibilities
- **Model:** Defines data structures and persistence logic.
- **View:** Contains request-handling logic.
- **Template:** Renders presentation output.

### Django Interpretation
- Django views often behave similarly to controllers in MVC.
- Django templates are the presentation layer.
- Django models manage persistence and often contain domain logic.

### Why It Matters
Understanding MVT helps developers place logic in the right layer and avoid tightly coupled code.

## Separation of Concerns

### Definition
Separation of concerns means keeping data access, business rules, request handling, and presentation logic distinct.

### Important Practices
- Keep views thin when possible.
- Place business rules in services, domain logic, or models as appropriate.
- Keep serializers, forms, and validators focused on input/output concerns.

### Why It Matters
Clear boundaries improve maintainability and reduce accidental side effects.

## Authentication vs Authorization

### Authentication
- **Definition:** Verifying who the user is.
- **Examples:** Password login, session authentication, JWT authentication.

### Authorization
- **Definition:** Verifying what the user is allowed to do.
- **Examples:** Role checks, object-level permissions, scope checks.

### Important Practices
- Perform both checks where required.
- Do not confuse “logged in” with “allowed.”

### Why It Matters
Many security bugs come from missing authorization rather than missing authentication.

## Request Lifecycle in a Backend Framework

### Typical Flow
1. Client sends an HTTP request.
2. Routing selects the correct handler.
3. Middleware performs shared logic such as logging, auth, or CSRF checks.
4. Validation and business logic run.
5. Data is read or written.
6. A response is serialized and returned.

### Important Practices
- Keep middleware focused and predictable.
- Centralize cross-cutting concerns such as authentication and logging.
- Validate input before using it.

### Why It Matters
Understanding the request lifecycle makes debugging and system design easier.

## Caching

### Definition
Caching stores reusable data temporarily to reduce repeated work.

### Important Practices
- Cache expensive reads, not sensitive per-user data without strict controls.
- Define expiration and invalidation rules clearly.
- Avoid serving stale or unauthorized content.

### Why It Matters
Caching improves performance but can introduce correctness and security bugs when misused.
