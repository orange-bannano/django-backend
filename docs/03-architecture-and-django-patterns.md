# Architecture Patterns: MVC, MVT, and Backend Structure

This file explains common server-side architecture patterns and where Django fits.

## Loose coupling
Loose coupling means components interact through well-defined interfaces, not direct dependencies.
Actual implementation is done by the framework (via constructors, whose args are futher dependencies for class), not the developer, which are then stored in Application Context (IOC CONTAINER, SpringBoot).
This allows for flexibility and easier maintenance at large scale.

## MVC (Model-View-Controller) (SpringBoot)
MVC: User Request ➔ Controller (Handles Logic) ➔ Model (Data) ➔ View (UI) ➔ User

### Responsibilities
- **Model:** Handles database and business rules. **[ Service Layer ➔ Repository Layer ➔ Database ]**
- **View:** Renders the user interface.
- **Controller:** Accepts input and coordinates between model and view.

### Why It Matters
MVC separates concerns so code is easier to test, understand, and maintain.

## MVT (Model-View-Template) (Django)
MVT: User Request ➔ Framework (URL Router)  ➔ View (Handles Logic) ➔ Template (UI) ➔ User

### Responsibilities
- **Model:** Defines data structures and persistence logic.
- **View:** Accepts HTTP requests, executes business logic, fetches data from the Model, and passes it to the Template.
Django views often behave similarly to controllers in MVC. The framework handles the controller routing implicitly.
- **Template:** Renders presentation output (UI).

## Separation of Concerns
Separation of concerns means keeping data access, business rules, request handling, and presentation logic distinct.

### Important Practices
- Keep views thin when possible.
- Place business rules in services, domain logic, or models as appropriate.
- Keep **serializers, forms, and validators** focused on input/output concerns.

### Why It Matters
Clear boundaries improve maintainability and reduce accidental side effects.
And, promotes **loose coupling**, making it easier to change one part of the system without affecting others.

##ORM (Object-Relational Mapping)
Maps objects which is used in code to RAW DB data (database tables and rows in SQL).
In Java, it is achieved by JPA (Java Persistence API) and in python, it is achieved by Django ORM.
And for SpringBoot via JPA implementations like Hibernate which auto configures/ implements DataSource, EntityManagerFactory, and TransactionManager based on the **dependencies** in the classpath and **properties** defined in application.properties or application.yml.
In spring code, database repository act as JPA interface.
Sometimes JSON / XML need to be created manually to interact.

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
Caching stores reusable data temporarily to reduce repeated work.

### Important Practices
- Cache expensive reads, not sensitive per-user data without strict controls.
- Define expiration and invalidation rules clearly.
- Avoid serving stale or unauthorized content.
- Monitor cache performance and hit rates.
- Use appropriate cache levels (in-memory, distributed, CDN) based on access patterns.
- Consider cache consistency and potential
- staleness when designing your caching strategy.
- Implement cache warming for critical paths to improve performance on first access.
- Use cache keys that are unique and descriptive to avoid collisions and ensure correct data retrieval.
- Test cache behavior under load and during failure scenarios to ensure it degrades gracefully.

### Why It Matters
Caching improves performance but can introduce correctness and security bugs when misused.
