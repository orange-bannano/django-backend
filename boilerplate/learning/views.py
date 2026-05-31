"""HTTP views for the learning app.

The views are intentionally small, delegating data validation and persistence
to helper modules so each concept is easy to copy elsewhere.
"""

from __future__ import annotations

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from learning.models import Note
from learning.services import archive_note, create_note, list_notes
from learning.utils import coerce_positive_int, paginate_queryset, parse_json_body
from learning.validators import validate_note_payload


def serialize_note(note: Note) -> dict[str, str | int | bool]:
    """Convert a Note model instance into JSON-serializable primitives."""

    # Flatten model fields into JSON-safe primitives.
    return {
        "id": note.id,
        "title": note.title,
        "body": note.body,
        "is_archived": note.is_archived,
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat(),
    }


@require_http_methods(["GET"])
def health_check(request):
    """Return a lightweight response used by monitors and load balancers."""

    # Keep the response tiny and deterministic for monitoring.
    return JsonResponse({"status": "ok"})


@require_http_methods(["GET", "POST"])
@csrf_protect
@ensure_csrf_cookie
def notes_collection(request):
    """List notes or create a new note in a single endpoint."""

    # Write path: validate JSON input then store a new note.
    if request.method == "POST":
        payload, error_message = parse_json_body(request)
        if error_message:
            return JsonResponse({"error": error_message}, status=400)

        # Validate the payload before calling the service layer.
        clean_data, errors = validate_note_payload(payload)
        if errors:
            return JsonResponse({"errors": errors}, status=400)

        note = create_note(**clean_data)
        return JsonResponse({"note": serialize_note(note)}, status=201)

    # Read path: apply bounded pagination and optional filters.
    limit = coerce_positive_int(request.GET.get("limit"), default=10, max_value=50)
    offset = coerce_positive_int(request.GET.get("offset"), default=0, max_value=10_000)
    include_archived = request.GET.get("include_archived") == "1"

    queryset = list_notes(include_archived=include_archived)
    total_count = queryset.count()
    page_items, meta = paginate_queryset(
        queryset[offset : offset + limit],
        limit=limit,
        offset=offset,
        total_count=total_count,
    )

    return JsonResponse(
        {
            "notes": [serialize_note(note) for note in page_items],
            "meta": meta,
        }
    )


@require_http_methods(["POST"])
@csrf_protect
def archive_note_view(request, note_id: int):
    """Archive a note and return the updated resource."""

    # Keep the database lookup in the service layer; handle missing rows here.
    try:
        note = archive_note(note_id=note_id)
    except Note.DoesNotExist:
        return JsonResponse({"error": "Note not found."}, status=404)

    return JsonResponse({"note": serialize_note(note)})


def say_hello(request):
    return render(request, 'hello.html')