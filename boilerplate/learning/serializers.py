"""Serializers and response formatters for API design in Chunk 2.

Serializers convert Python objects to JSON and validate incoming JSON payloads.
They're the boundary between HTTP and domain logic, centralizing data transformation.

Chunk 2 demonstrates:
- Explicit version headers for API versioning.
- Safe schema validation (allowlist pattern).
- Nested data transformation and filtering.

Flow: request -> view -> serializer (validate) -> domain logic -> serializer (serialize) -> response.
"""

from __future__ import annotations

from typing import Any

# ============================================================================
# API VERSIONING: Accept and advertise schema versions via headers.
# ============================================================================

CURRENT_API_VERSION = "2024-06-10"
"""The latest stable API version. Change when introducing breaking changes."""

DEPRECATED_API_VERSIONS = ["2024-01-01"]
"""Versions no longer supported. Log warnings or reject requests using old versions."""


def serialize_with_version(data: dict[str, Any], version: str = CURRENT_API_VERSION) -> dict[str, Any]:
    """
    Wrap response data with version metadata.

    Clients can inspect the version to ensure schema compatibility.
    Useful for deprecation warnings and feature gates.

    Args:
        data: The response payload.
        version: API version string.

    Returns:
        Wrapped response with version header.

    Example:
        {
            "data": {...},
            "api_version": "2024-06-10",
            "deprecated": False
        }
    """

    # Mark if this version is deprecated; helps clients migrate.
    is_deprecated = version in DEPRECATED_API_VERSIONS

    return {
        "data": data,
        "api_version": version,
        "deprecated": is_deprecated,
    }


def get_api_version_from_header(request) -> str:
    """
    Extract or negotiate API version from request headers.

    Clients can specify 'Accept-Version: 2024-06-10' or default to current.

    Args:
        request: The incoming HTTP request.

    Returns:
        API version string.
    """

    # Allow clients to opt into specific versions.
    requested_version = request.headers.get("Accept-Version", "").strip()

    # Return requested version if valid; otherwise use current.
    if requested_version and requested_version in [CURRENT_API_VERSION] + DEPRECATED_API_VERSIONS:
        return requested_version

    return CURRENT_API_VERSION


# ============================================================================
# SAFE FILTERING AND SORTING: Allowlist pattern prevents SQL injection.
# ============================================================================

class AllowlistValidator:
    """
    Validates that query parameters (filters, sorts) match a safe allowlist.

    SQL injection via dynamic ordering: 'sort=title; DROP TABLE notes;' would fail.
    With an allowlist, only "title", "created_at", etc. are permitted.

    Usage:
        validator = AllowlistValidator(allowed_fields={"title", "created_at"})
        validator.validate_sort("created_at")  # OK
        validator.validate_sort("DROP TABLE;")  # Raises ValueError
    """

    def __init__(self, allowed_fields: set[str]):
        """Initialize with a set of allowed field names."""
        self.allowed_fields = allowed_fields

    def validate_sort(self, sort_param: str) -> str:
        """
        Validate and normalize a sort parameter.

        Supports "-field" for descending order (e.g., "-created_at").

        Args:
            sort_param: Incoming sort parameter from query string.

        Returns:
            "field" or "-field" if valid.

        Raises:
            ValueError: If sort_param is not in allowlist.

        Example:
            "-created_at" -> "-created_at"
            "title" -> "title"
            "DROP TABLE;" -> ValueError
        """

        # Support descending order with "-" prefix.
        is_descending = sort_param.startswith("-")
        field_name = sort_param[1:] if is_descending else sort_param

        # Reject fields not on the allowlist.
        if field_name not in self.allowed_fields:
            raise ValueError(f"Sort field '{field_name}' is not allowed. Choose from: {self.allowed_fields}")

        return sort_param

    def validate_filters(self, filter_dict: dict[str, Any]) -> dict[str, Any]:
        """
        Validate and normalize filter parameters.

        Only allows blacklist keys; values are type-checked.

        Args:
            filter_dict: {field_name: field_value, ...}

        Returns:
            Validated filter dict.

        Raises:
            ValueError: If any field is not in allowlist.

        Example:
            {"title": "Python", "is_archived": "1"} -> OK
            {"title": "Python", "__class__": "..."}  -> ValueError
        """

        validated = {}
        for field_name, value in filter_dict.items():
            # Reject fields not on the allowlist.
            if field_name not in self.allowed_fields:
                raise ValueError(f"Filter field '{field_name}' is not allowed. Choose from: {self.allowed_fields}")

            validated[field_name] = value

        return validated


# ============================================================================
# NOTE SERIALIZER: Demonstrates schema versioning and safe transformation.
# ============================================================================

class NoteSerializer:
    """
    Serializer for Note model.

    Decouples JSON representation from database schema.
    Supports versioned output and filtered field inclusion.
    """

    # Define which fields are included in v1 (baseline).
    FIELDS_V1 = {"id", "title", "body", "created_at", "updated_at"}

    # Define which fields are included in v2 (added is_archived visibility).
    FIELDS_V2 = FIELDS_V1 | {"is_archived"}

    def __init__(self, version: str = CURRENT_API_VERSION):
        """Initialize with a specific API version."""
        self.version = version
        self.fields = self.FIELDS_V2 if version == CURRENT_API_VERSION else self.FIELDS_V1

    def serialize(self, note, *, include_fields: set[str] | None = None) -> dict[str, Any]:
        """
        Convert a Note instance to a JSON-safe dict.

        Args:
            note: A Note model instance.
            include_fields: Optional subset of fields to include. Defaults to all.

        Returns:
            Dict ready for JSON encoding.
        """

        # Use include_fields if specified; otherwise use version default.
        fields_to_use = include_fields & self.fields if include_fields else self.fields

        # Build dict from model fields.
        result = {}
        for field_name in fields_to_use:
            if field_name == "created_at" or field_name == "updated_at":
                # Serialize datetime to ISO string.
                result[field_name] = getattr(note, field_name).isoformat()
            else:
                result[field_name] = getattr(note, field_name)

        return result

    def serialize_many(self, notes, **kwargs) -> list[dict[str, Any]]:
        """Serialize a list of Note instances."""
        return [self.serialize(note, **kwargs) for note in notes]

