"""Input validation helpers for the learning app."""

from __future__ import annotations

from typing import Any


def validate_note_payload(
    payload: dict[str, Any],
    title_max_length: int = 500,
    body_max_length: int = 3000,
) -> tuple[dict[str, str], dict[str, str]]:
    """Validate user input before creating a note.

    Returns a tuple of (clean_data, errors). If errors is non-empty, the request
    should be rejected with a 400 response.
    """

    # Collect validation errors in a field-to-message mapping.
    errors: dict[str, str] = {}

    # Normalize and validate the title.
    raw_title = str(payload.get("title", "")).strip()
    if not raw_title:
        errors["title"] = "Title is required."
    elif len(raw_title) > title_max_length:
        errors["title"] = f"Title must be {title_max_length} characters or fewer."

    # Normalize and validate the body.
    raw_body = str(payload.get("body", "")).strip()
    if len(raw_body) > body_max_length:
        errors["body"] = f"Body must be {body_max_length} characters or fewer."

    return {
        "title": raw_title,
        "body": raw_body,
    }, errors
