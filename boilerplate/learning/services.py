"""Service-layer helpers to keep views small and testable."""

from __future__ import annotations

from django.db import transaction

from learning.models import Note


def create_note(*, title: str, body: str) -> Note:
    """Create a note using model validation and a transaction."""

    # Build the model instance and run Django's model-level validation.
    note = Note(title=title, body=body)
    note.full_clean()

    # Persist inside a transaction to keep writes consistent.
    with transaction.atomic():
        note.save()

    return note


def list_notes(*, include_archived: bool = False):
    """Return a queryset of notes in a deterministic order."""

    # Limit the selected columns to reduce payload and DB work.
    queryset = Note.objects.all().only("id", "title", "body", "is_archived", "created_at", "updated_at")

    # Exclude archived records unless explicitly requested.
    if not include_archived:
        queryset = queryset.filter(is_archived=False)

    return queryset.order_by("-created_at")


def archive_note(*, note_id: int) -> Note:
    """Mark a note as archived using a row lock for consistency."""

    # Lock the row to avoid concurrent updates during the archive operation.
    with transaction.atomic():
        note = Note.objects.select_for_update().get(pk=note_id)
        note.is_archived = True
        note.save(update_fields=["is_archived", "updated_at"])

    return note
