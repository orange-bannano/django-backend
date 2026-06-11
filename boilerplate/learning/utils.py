"""Reusable HTTP helpers focused on safety and clarity."""

from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any, Iterable


def parse_json_body(request, *, max_bytes: int = 10_000) -> tuple[dict[str, Any] | None, str | None]:
    """Parse a JSON request body with simple size and type guards."""

    # Enforce JSON-only content types to avoid ambiguous parsing.
    if request.content_type != "application/json":
        return None, "Content-Type must be application/json."

    # Guard against excessively large payloads.
    if len(request.body) > max_bytes:
        return None, "Payload too large."

    # Decode an empty body as an empty object for simpler handling.
    raw_body = request.body.decode("utf-8") if request.body else "{}"

    # Fail fast on invalid JSON syntax.
    try:
        data = json.loads(raw_body)
    except JSONDecodeError:
        return None, "Invalid JSON payload."

    # Enforce object payloads to keep validation simple and explicit.
    if not isinstance(data, dict):
        return None, "JSON payload must be an object."

    return data, None


def coerce_positive_int(value: str | None, *, default: int, max_value: int) -> int:
    """Convert query-string values to bounded positive integers."""

    # Prefer the default when parsing fails.
    try:
        parsed = int(value) if value is not None else default
    except ValueError:
        return default

    # Reject negative numbers to keep pagination consistent.
    if parsed < 0:
        return default

    # Clamp values to avoid huge query costs.
    return min(parsed, max_value)


def paginate_queryset(
    items: Iterable[Any],
    *,
    limit: int,
    offset: int,
    total_count: int,
) -> tuple[list[Any], dict[str, int | None]]:
    """Return a slice of items with simple offset pagination metadata."""

    # Materialize the sliced results once, then compute metadata.
    page_items = list(items)
    next_offset = offset + limit if offset + limit < total_count else None
    previous_offset = offset - limit if offset - limit >= 0 else None

    return page_items, {
        "limit": limit,
        "offset": offset,
        "count": total_count,
        "next_offset": next_offset,
        "previous_offset": previous_offset,
    }
    # using the metadata, next page can be identified via next_offset and previous page by previous_offset, which become the new offset for new page while navigating