/**
 * Generates a unique idempotency key for mutating API requests.
 * Uses crypto.randomUUID when available, with a timestamp+random fallback.
 */
export function generateIdempotencyKey() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  const random = Math.random().toString(36).slice(2, 12);
  return `idem-${Date.now()}-${random}`;
}
