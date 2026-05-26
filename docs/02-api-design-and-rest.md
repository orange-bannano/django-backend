# REST API Design and OpenAPI

This file focuses on designing maintainable APIs and documenting them clearly.

## REST API

### Definition
REST is an architectural style for APIs that models application data as resources and uses standard HTTP semantics to interact with them.

### Key Points
- Resources should have stable, meaningful URLs.
- Methods should align with HTTP semantics.
- Requests should be stateless.
- Representations are commonly JSON.

### Important Practices
- Use nouns for resource names, such as `/users` and `/orders`.
- Keep URL structures predictable.
- Prefer plural resource names for consistency.
- Version APIs when breaking changes are introduced.

### Why It Matters
REST conventions reduce ambiguity and help clients understand and integrate with APIs quickly.

## Resource Modeling

### Definition
Resource modeling is deciding how business entities are represented and exposed through endpoints.

### Important Practices
- Separate internal database design from public API design.
- Avoid exposing sensitive or irrelevant internal fields.
- Keep relationships explicit and predictable.

### Why It Matters
Well-modeled resources are easier to secure, evolve, and document.

## Filtering, Sorting, Pagination, and Partial Loading

### Filtering
- **Definition:** Narrowing results based on field values.
- **Practice:** Use explicit query parameters such as `?status=active`.
- **Reason:** Clients can retrieve only what they need.

### Sorting
- **Definition:** Ordering a result set.
- **Practice:** Allow safe, documented sort fields only.
- **Reason:** Prevents misuse and inconsistent behavior.

### Pagination
- **Definition:** Splitting large result sets into smaller pages.
- **Practice:** Use page-based or cursor-based pagination.
- **Reason:** Protects performance and improves usability.

### Partial Loading
- **Definition:** Returning only part of a resource or only selected related data.
- **Practice:** Support sparse field selection or controlled expansion, such as `?fields=id,name`.
- **Reason:** Reduces payload size and database work.

## Validation and Serialization

### Validation
- **Definition:** Ensuring incoming data matches business and format rules.
- **Practice:** Validate at API boundaries and return clear field-level errors.
- **Reason:** Prevents bad data from reaching core logic.

### Serialization
- **Definition:** Converting internal objects into API-friendly representations.
- **Practice:** Keep serializer logic explicit and secure.
- **Reason:** Prevents accidental data leakage and inconsistent responses.

## OpenAPI

### Definition
OpenAPI is a machine-readable specification format used to describe HTTP APIs.

### Key Benefits
- Documents paths, methods, parameters, schemas, and security requirements.
- Supports client SDK generation and interactive docs.
- Improves alignment between frontend, backend, QA, and partner teams.

### Important Practices
- Keep the spec updated with real API behavior.
- Document request and response examples.
- Include authentication, error responses, and pagination details.

### Why It Matters
Accurate API contracts reduce integration errors and speed up collaboration.

## API Versioning

### Definition
Versioning is a strategy for evolving APIs without breaking existing clients unexpectedly.

### Important Practices
- Version only when needed.
- Communicate deprecations early.
- Prefer additive changes when possible.

### Why It Matters
Good versioning protects long-lived clients and lowers migration risk.
