"""Service-layer helpers to keep views small and testable."""

from __future__ import annotations

import json

from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse

from learning.models import Note, NoteMembership

# AFTER THIS PENDING REQUEST ARE TRASHED
IDEMPOTENCY_PENDING_TTL_SECONDS = 60
### AFTER THIS, SUCCESSFUL REQUESTS CAN BE RESTARTED
IDEMPOTENCY_COMPLETED_TTL_SECONDS = 300

IDEMPOTENCY_FEATURE_FLAG_CACHE_KEY = "feature:idempotency:enabled"
IDEMPOTENCY_FEATURE_FLAG_TTL_SECONDS = None

### IDEMPOTENCY TOOLS STARTS ###

def is_idempotency_enabled() -> bool:
    """Return whether idempotency checks are currently enabled."""

    flag = cache.get(IDEMPOTENCY_FEATURE_FLAG_CACHE_KEY)
    if flag is None:
        return True
    return bool(flag)


def set_idempotency(enabled: bool) -> bool:
    """Persist the idempotency feature flag and return the new state."""

    cache.set(
        IDEMPOTENCY_FEATURE_FLAG_CACHE_KEY,
        bool(enabled),
        timeout=IDEMPOTENCY_FEATURE_FLAG_TTL_SECONDS,
    )
    return bool(enabled)

def _request_idempotency_cache_key(request, idempotency_key: str) -> str:
    """Scope request idempotency keys to the current user, method, and path."""

    user_id = request.user.id if getattr(request.user, "is_authenticated", False) else "anonymous"
    return f"idempotency:{user_id}:{request.method}:{request.path}:{idempotency_key}"


def _build_cached_response(record: dict) -> HttpResponse:
    """Reconstruct an HTTP response from a cached idempotency record."""

    status_code = int(record.get("status_code", 200))
    content_type = str(record.get("content_type", "application/json"))

    if content_type.startswith("application/json"):
        return JsonResponse(record.get("payload", {}), status=status_code)

    return HttpResponse(
        record.get("body", ""),
        status=status_code,
        content_type=content_type,
    )


def check_request_idempotency(request) -> tuple[str | None, HttpResponse | None]:
    """Return a cached response or an error if the request idempotency key is invalid."""

    if not is_idempotency_enabled():
        return None, None

    idempotency_key = str(request.headers.get("Idempotency-Key", "")).strip()
    if not idempotency_key:
        return None, JsonResponse({"error": "Idempotency-Key header is required."}, status=400)

    cache_key = _request_idempotency_cache_key(request, idempotency_key)
    record = cache.get(cache_key)
    # if no key is matched, no cached_response
    if not record:
        return cache_key, None

    if record.get("status") == "pending":
        return cache_key, JsonResponse(
            {
                "error": "Request is already pending.",
                "idempotency_key": idempotency_key,
            },
            status=409,
        )

    return cache_key, _build_cached_response(record)


def mark_request_pending(cache_key: str, idempotency_key: str) -> None:
    """Mark a request as pending so duplicate retries can be rejected."""

    if not cache_key:
        return

    cache.set(
        cache_key,
        {
            "status": "pending",
            "idempotency_key": idempotency_key,
        },
        timeout=IDEMPOTENCY_PENDING_TTL_SECONDS,
    )


def store_idempotent_response(cache_key: str, response: HttpResponse, idempotency_key: str) -> None:
    """Cache the final response for an idempotent request. And mark as completed"""

    if not cache_key:
        return

    content_type = response.headers.get("Content-Type", "application/json")
    body = response.content.decode(response.charset or "utf-8")
    record = {
        "status": "completed",
        "idempotency_key": idempotency_key,
        "status_code": response.status_code,
        "content_type": content_type,
        "body": body,
    }

    # JSON response are stored only.
    if content_type.startswith("application/json"):
        try:
            record["payload"] = json.loads(body) if body else {}
        except json.JSONDecodeError:
            record["payload"] = {}

    cache.set(cache_key, record, timeout=IDEMPOTENCY_COMPLETED_TTL_SECONDS)

### IDEMPOTENCY TOOLS ENDS ###

### ROLE VERIFICATION SERVICES STARTS ###

def resolve_user_role(user) -> str:
    """Map the authenticated user to the note authorization role."""

    if user.is_superuser or user.groups.filter(name="Admin").exists():
        return NoteMembership.ROLE_ADMIN
    if user.groups.filter(name="Manager").exists():
        return NoteMembership.ROLE_MANAGER
    return NoteMembership.ROLE_EMPLOYEE

def can_modify_note(user, note: Note) -> bool:
    """Return whether the user may update the note."""
    # MODIFY HERE TO CHANGE ACCESS
    role = resolve_user_role(user)
    if role == NoteMembership.ROLE_ADMIN:
        return True
    if note.memberships.filter(user=user, is_owner=True).exists():
        return True
    if role == NoteMembership.ROLE_MANAGER:
        return note.memberships.filter(
            is_owner=True,
            role=NoteMembership.ROLE_EMPLOYEE,
        ).exists()
    return False


def can_delete_note(user) -> bool:
    """Only admins may delete notes."""
    # MODIFY HERE TO CHANGE ACCESS
    return resolve_user_role(user) == NoteMembership.ROLE_ADMIN

### ROLE VERIFICATION SERVICES ENDS ###

### NOTE (MODEL DATA) CRUD OPERATIONS STARTS ###

def create_note(*, owner, title: str, body: str) -> Note:
    """Create a note using model validation and a transaction."""

    # Build the model instance and run Django's model-level validation.
    note = Note(title=title, body=body)
    note.full_clean()

    # Persist inside a transaction to keep writes consistent.
    with transaction.atomic():
        note.save()
        NoteMembership.objects.create(
            note=note,
            user=owner,
            role=resolve_user_role(owner),
            is_owner=True,
        )

    return note


def list_notes(*, include_archived: bool = False, query : Q):
    """
    Return a queryset of notes with optional filtering.

    Chunk 2: Supports filtering via kwargs (e.g., title__icontains="python").
    Filters are applied directly; callers must validate allowlist before calling.

    Args:
        include_archived: If False, exclude is_archived=True records.
        query: Additional ORM filter.

    Returns:
        QuerySet ordered by -created_at (newest first).
    """

    # Limit the selected columns to reduce payload and DB work.
    queryset = Note.objects.all().only(
        "id",
        "title",
        "body",
        "is_archived",
        "created_at",
        "updated_at",
    )

    # Apply custom filters
    # user_input = "'; DROP TABLE note; --" -->
    # cursor.execute("SELECT * FROM note WHERE title LIKE %s", ("%'; DROP TABLE note; --%",))
    queryset = queryset.filter(query)

    # Exclude archived records unless explicitly requested.
    if not include_archived:
        queryset = queryset.filter(is_archived=False)

    return queryset

def filter_notes_for_user(queryset, user):
    """Restrict note visibility based on owner role and the current user role."""

    role = resolve_user_role(user)
    if role == NoteMembership.ROLE_ADMIN:
        return queryset
    if role == NoteMembership.ROLE_MANAGER:
        return queryset.filter(
            Q(memberships__user=user, memberships__is_owner=True) |
            Q(
                memberships__is_owner=True,
                memberships__role=NoteMembership.ROLE_EMPLOYEE,
            )
        ).distinct()
    return queryset.filter(memberships__user=user, memberships__is_owner=True).distinct()

def archive_note(*, note_id: int) -> Note:
    """Mark a note as archived using a row lock for consistency."""

    # Lock the row to avoid concurrent updates during the archive operation.
    with transaction.atomic():
        note = Note.objects.select_for_update().get(pk=note_id)
        note.is_archived = True
        note.save(update_fields=["is_archived", "updated_at"])

    return note

### NOTE (MODEL DATA) CRUD OPERATIONS ENDS ###

### RATE LIMITING STARTS ###

def rate_limit_ip(request):
    ip = request.META.get("REMOTE_ADDR")
    key = f"rate_limit:{ip}"
    count = cache.get(key, 0)
    if count >= 10:
        return JsonResponse({"error": "Rate limit exceeded"},status=429,)
    cache.set(key,count + 1,timeout=60,)
    return None
def rate_limit_user(request):
    if not request.user.is_authenticated:
        return None
    key = f"user_limit:{request.user.id}"
    count = cache.get(key, 0)
    if count >= 100:
        return JsonResponse({"error": "Too many requests"},status=429,)
    cache.set(key,count + 1,timeout=3600,)
    return None

### RATE LIMITING ENDS ###
