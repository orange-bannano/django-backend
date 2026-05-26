# HTTP and Web Backend Basics

This file covers the communication model used by backend systems and the core concepts every API developer should understand.

## HTTP Communication

### Definition
HTTP is a request-response protocol. A client sends a request to a server, and the server returns a response.

### Key Points
- A request usually contains a method, URL, headers, and sometimes a body.
- A response usually contains a status code, headers, and sometimes a body.
- HTTP is stateless by default, so each request should contain the information needed to process it.

### Important Practices
- Design endpoints so they work correctly even when requests are retried.
- Return consistent response formats.
- Use HTTPS in production to protect data in transit.

### Why It Matters
Good HTTP design improves reliability, observability, security, and client compatibility.

## HTTP Methods

### GET
- **Definition:** Retrieve data.
- **Practice:** Do not change server state.
- **Reason:** Safe reads allow caching and easy retries.

### POST
- **Definition:** Create a new resource or trigger an operation.
- **Practice:** Use for non-idempotent operations.
- **Reason:** Repeating the same POST may create duplicates unless protected.

### PUT
- **Definition:** Replace a resource with the provided representation.
- **Practice:** Send the full resource state when using PUT.
- **Reason:** PUT is expected to be idempotent.

### PATCH
- **Definition:** Partially update a resource.
- **Practice:** Only include changed fields and validate patch semantics carefully.
- **Reason:** It reduces payload size and supports partial modification.

### DELETE
- **Definition:** Remove a resource.
- **Practice:** Return clear success or not-found behavior.
- **Reason:** DELETE is typically treated as idempotent.

### HEAD
- **Definition:** Same as GET but without a response body.
- **Practice:** Use for metadata checks.
- **Reason:** Useful for cache validation and lightweight existence checks.

### OPTIONS
- **Definition:** Lists allowed methods or communication options.
- **Practice:** Support it correctly for CORS-enabled APIs.
- **Reason:** Browsers rely on it during preflight requests.

## Idempotency

### Definition
An operation is idempotent when performing it multiple times has the same final effect as performing it once.

### Examples
- GET is idempotent.
- PUT is usually idempotent.
- DELETE is usually idempotent.
- POST is usually not idempotent unless an idempotency key is used.

### Important Practices
- Use idempotency keys for payment or order creation APIs.
- Design retries so network failures do not cause duplicate business actions.

### Why It Matters
Idempotency protects systems from duplicate writes caused by retries, timeouts, and client reconnects.

## HTTP Status Codes

### Common Success Codes
- `200 OK`: Request succeeded.
- `201 Created`: Resource created successfully.
- `202 Accepted`: Request accepted for asynchronous processing.
- `204 No Content`: Success with no response body.

### Common Client Error Codes
- `400 Bad Request`: Invalid request structure or validation failure.
- `401 Unauthorized`: Authentication is required or invalid.
- `403 Forbidden`: Authenticated but not allowed.
- `404 Not Found`: Resource does not exist.
- `409 Conflict`: State conflict, such as duplicate creation.
- `422 Unprocessable Entity`: Request is valid structurally but business validation failed.
- `429 Too Many Requests`: Client exceeded allowed rate.

### Common Server Error Codes
- `500 Internal Server Error`: Unexpected server failure.
- `502 Bad Gateway`: Upstream dependency failed.
- `503 Service Unavailable`: Service is overloaded or down for maintenance.
- `504 Gateway Timeout`: Upstream service took too long to respond.

### Important Practices
- Match status codes to the real outcome.
- Avoid returning `200` for error cases.
- Include structured error details in the response body.

### Why It Matters
Correct status codes help clients recover properly and make monitoring more accurate.

## HTTP Headers

### Definition
Headers carry metadata about requests and responses.

### Common Headers
- `Authorization`: Carries credentials such as bearer tokens.
- `Content-Type`: Describes the payload format.
- `Accept`: Tells the server what formats the client can process.
- `Cache-Control`: Defines caching behavior.
- `ETag`: Helps with cache validation and concurrency control.
- `Cookie`: Sends stored cookies to the server.
- `Set-Cookie`: Instructs the client to store a cookie.
- `Origin`: Identifies the calling origin for browser requests.
- `X-Request-ID` or `Traceparent`: Helps distributed tracing and debugging.

### Important Practices
- Validate and sanitize header inputs.
- Set security-related headers intentionally.
- Avoid leaking internal implementation details through headers.

### Why It Matters
Headers affect authentication, caching, content negotiation, tracing, and browser security.

## Content Negotiation

### Definition
Content negotiation is the process of choosing the response format based on client capabilities and server support.

### Important Practices
- Respect `Accept` headers when multiple response formats are supported.
- Keep APIs consistent and predictable.

### Why It Matters
It improves interoperability and makes APIs easier to evolve.
