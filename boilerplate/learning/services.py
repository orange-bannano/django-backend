"""Service-layer helpers to keep views small and testable."""

from __future__ import annotations

from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse

from learning.models import Note, NoteMembership


def resolve_user_role(user) -> str:
    """Map the authenticated user to the note authorization role."""

    if user.is_superuser or user.groups.filter(name="Admin").exists():
        return NoteMembership.ROLE_ADMIN
    if user.groups.filter(name="Manager").exists():
        return NoteMembership.ROLE_MANAGER
    return NoteMembership.ROLE_EMPLOYEE


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

def archive_note(*, note_id: int) -> Note:
    """Mark a note as archived using a row lock for consistency."""

    # Lock the row to avoid concurrent updates during the archive operation.
    with transaction.atomic():
        note = Note.objects.select_for_update().get(pk=note_id)
        note.is_archived = True
        note.save(update_fields=["is_archived", "updated_at"])

    return note

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