"""Input validation helpers for the learning app."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
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


# def validate_transaction_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
#     """Validate transactional payloads for forwarding to the payment gateway.
#
#     Returns a tuple of (clean_data, errors). If errors is non-empty, the request
#     should be rejected with a 400 response.
#     """
#
#     # Track validation issues by field name.
#     errors: dict[str, str] = {}
#
#     # Validate and normalize the amount.
#     raw_amount = payload.get("amount")
#     amount: Decimal | None = None
#     if raw_amount is None:
#         errors["amount"] = "Amount is required."
#     else:
#         try:
#             amount = Decimal(str(raw_amount))
#             if amount <= 0:
#                 errors["amount"] = "Amount must be greater than zero."
#         except (InvalidOperation, ValueError):
#             errors["amount"] = "Amount must be a valid number."
#
#     # Validate the currency as an ISO-like 3-letter code.
#     raw_currency = str(payload.get("currency", "")).strip().upper()
#     if not raw_currency:
#         errors["currency"] = "Currency is required."
#     elif len(raw_currency) != 3:
#         errors["currency"] = "Currency must be a 3-letter ISO code."
#
#     # Validate the external reference for idempotent lookups.
#     raw_reference = str(payload.get("reference", "")).strip()
#     if not raw_reference:
#         errors["reference"] = "Reference is required."
#     elif len(raw_reference) > 64:
#         errors["reference"] = "Reference must be 64 characters or fewer."
#
#     # Validate the optional description for gateway display.
#     raw_description = str(payload.get("description", "")).strip()
#     if raw_description and len(raw_description) > 200:
#         errors["description"] = "Description must be 200 characters or fewer."
#
#     # Return normalized payload plus any errors.
#     return {
#         "amount": str(amount) if amount is not None else "",
#         "currency": raw_currency,
#         "reference": raw_reference,
#         "description": raw_description,
#         "metadata": payload.get("metadata", {}) if isinstance(payload.get("metadata", {}), dict) else {},
#     }, errors
