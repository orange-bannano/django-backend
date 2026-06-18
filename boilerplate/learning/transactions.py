"""Helpers for forwarding transactional requests with idempotency."""

from __future__ import annotations

import base64
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.utils.dateparse import parse_datetime

PENDING_KEYS_CACHE_KEY = "transactions:pending-keys"


def _cache_key(idempotency_key: str) -> str:
    # Build a stable cache key for one idempotency token.
    return f"transactions:request:{idempotency_key}"


def _auth_header() -> str:
    # Create a basic auth header for the downstream gateway.
    username = getattr(settings, "THIRD_PARTY_USER", "demo")
    password = getattr(settings, "THIRD_PARTY_PASSWORD", "demo")
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def _request_json(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    *,
    extra_headers: dict[str, str] | None = None,
    timeout_seconds: int | None = None,
) -> tuple[int | None, dict[str, Any] | None, str | None]:
    # Normalize base URL and timeout values.
    base_url = getattr(settings, "THIRD_PARTY_BASE_URL", "http://localhost:9000")
    timeout = timeout_seconds or getattr(settings, "THIRD_PARTY_TIMEOUT_SECONDS", 3)
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    # Assemble required headers for JSON + auth.
    headers = {
        "Accept": "application/json",
        "Authorization": _auth_header(),
    }
    if extra_headers:
        headers.update(extra_headers)

    # Encode the JSON payload if provided.
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    try:
        # Send the request and parse JSON on success.
        request = Request(url, data=data, headers=headers, method=method)
        with urlopen(request, timeout=timeout) as response:
            raw_body = response.read().decode("utf-8")
            parsed = json.loads(raw_body) if raw_body else None
            return response.status, parsed, None
    except HTTPError as exc:
        # Return HTTP error responses with parsed JSON if present.
        raw_body = exc.read().decode("utf-8") if hasattr(exc, "read") else ""
        parsed = json.loads(raw_body) if raw_body else None
        return exc.code, parsed, None
    except (URLError, TimeoutError, ValueError) as exc:
        # Normalize transport and parsing failures into an error string.
        return None, None, str(exc)


def is_third_party_healthy() -> bool:
    # Lightweight health check used before forwarding requests.
    status, _, error = _request_json("GET", "health")
    return error is None and status == 200


def send_payment(clean_data: dict[str, Any], idempotency_key: str) -> tuple[int | None, dict[str, Any] | None, str | None]:
    # Build the outbound payment payload.
    payload = {
        "amount": clean_data["amount"],
        "currency": clean_data["currency"],
        "reference": clean_data["reference"],
        "description": clean_data["description"],
        "metadata": clean_data["metadata"],
        "submitted_at": timezone.now().isoformat(),
    }
    # Forward to the third-party service with idempotency.
    return _request_json(
        "POST",
        "transactions",
        payload,
        extra_headers={"Idempotency-Key": idempotency_key},
    )


def fetch_transaction_status(reference: str) -> tuple[int | None, dict[str, Any] | None, str | None]:
    # Query the gateway for a payment status by reference.
    safe_reference = quote(reference, safe="")
    return _request_json("GET", f"transactions/{safe_reference}")


def send_reverse(reference: str) -> tuple[int | None, dict[str, Any] | None, str | None]:
    # Request a reversal for a prior transaction.
    safe_reference = quote(reference, safe="")
    return _request_json("POST", f"transactions/{safe_reference}/reverse")


def get_cached_record(idempotency_key: str) -> dict[str, Any] | None:
    # Read any cached idempotency record.
    return cache.get(_cache_key(idempotency_key))


def store_pending_request(idempotency_key: str, payload: dict[str, Any]) -> None:
    # Cache pending requests so duplicates can be rejected.
    pending_ttl = getattr(settings, "TRANSACTION_PENDING_TTL_SECONDS", 300)
    record = {
        "status": "pending",
        "payload": payload,
        "created_at": timezone.now().isoformat(),
    }
    cache.set(_cache_key(idempotency_key), record, timeout=pending_ttl)

    # Maintain a list of pending keys for reconciliation sweeps.
    pending_keys = set(cache.get(PENDING_KEYS_CACHE_KEY) or [])
    pending_keys.add(idempotency_key)
    cache.set(PENDING_KEYS_CACHE_KEY, list(pending_keys), timeout=pending_ttl)


def store_completed_response(
    idempotency_key: str,
    response_payload: dict[str, Any],
    status_code: int,
) -> None:
    # Cache completed responses so retries return the same result.
    completed_ttl = getattr(settings, "TRANSACTION_COMPLETED_TTL_SECONDS", 900)
    record = {
        "status": "completed",
        "response": response_payload,
        "status_code": status_code,
        "completed_at": timezone.now().isoformat(),
    }
    cache.set(_cache_key(idempotency_key), record, timeout=completed_ttl)

    # Remove from pending set if it was tracked.
    pending_keys = set(cache.get(PENDING_KEYS_CACHE_KEY) or [])
    if idempotency_key in pending_keys:
        pending_keys.remove(idempotency_key)
        cache.set(PENDING_KEYS_CACHE_KEY, list(pending_keys), timeout=completed_ttl)


def reconcile_pending_requests() -> None:
    # Skip reconciliation until the gateway is healthy again.
    if not is_third_party_healthy():
        return

    # Load pending idempotency keys to probe their status.
    pending_keys = list(cache.get(PENDING_KEYS_CACHE_KEY) or [])
    if not pending_keys:
        return

    reverse_after = getattr(settings, "TRANSACTION_REVERSE_AFTER_SECONDS", 600)
    now = timezone.now()

    for idempotency_key in list(pending_keys):
        record = cache.get(_cache_key(idempotency_key))
        if not record or record.get("status") != "pending":
            pending_keys.remove(idempotency_key)
            continue

        # Ask the gateway what happened for this reference.
        reference = record["payload"].get("reference", "")
        status_code, status_payload, error = fetch_transaction_status(reference)
        if error or status_code is None:
            continue

        status_payload = status_payload or {}
        state = str(status_payload.get("state") or status_payload.get("status") or "").lower()

        # Use cached age to determine if we should reverse.
        created_at = parse_datetime(record.get("created_at", "")) or now
        age_seconds = (now - created_at).total_seconds()

        if state in {"completed", "settled", "paid"}:
            if age_seconds >= reverse_after:
                reverse_code, reverse_payload, reverse_error = send_reverse(reference)
                if reverse_error is None and reverse_code is not None:
                    store_completed_response(
                        idempotency_key,
                        {
                            "status": "reversed",
                            "gateway_response": reverse_payload or {},
                        },
                        reverse_code,
                    )
                    pending_keys.remove(idempotency_key)
            else:
                store_completed_response(
                    idempotency_key,
                    {
                        "status": "completed",
                        "gateway_response": status_payload,
                    },
                    200,
                )
                pending_keys.remove(idempotency_key)
        elif state in {"failed", "declined"}:
            store_completed_response(
                idempotency_key,
                {
                    "status": "failed",
                    "gateway_response": status_payload,
                },
                409,
            )
            pending_keys.remove(idempotency_key)

    # Persist the trimmed pending key list.
    cache.set(PENDING_KEYS_CACHE_KEY, pending_keys, timeout=getattr(settings, "TRANSACTION_PENDING_TTL_SECONDS", 300))
