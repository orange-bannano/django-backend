from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from learning.transactions import get_cached_record, is_third_party_healthy, store_pending_request, \
    reconcile_pending_requests, send_payment, store_completed_response
from learning.utils import parse_json_body


@require_http_methods(["POST"])
@csrf_exempt
def transactional_request(request):
    """Forward transactional requests with idempotency protection.

    Postman:
        Method: POST
        URL: /api/transactions/
        Headers:
            Idempotency-Key: 8f0a9d52-7f40-4a16-b0db-6d7df06e6c11
        Body:
        {
            "reference": "INV-1001",
            "amount": "499.99",
            "currency": "INR",
            "description": "June hosting invoice",
            "metadata": {
                "vendor_id": "vendor-42",
                "source": "postman"
            }
        }
    """

    # Parse and validate the incoming JSON payload.
    payload, error_message = parse_json_body(request)
    if error_message:
        return JsonResponse({"error": error_message}, status=400)

    # Require an idempotency key to prevent duplicate processing.
    idempotency_key = str(request.headers.get("Idempotency-Key", "")).strip()
    if not idempotency_key:
        return JsonResponse({"error": "Idempotency-Key header is required."}, status=400)

    # Validate business fields before calling downstream services.
    clean_data, errors = validate_transaction_payload(payload)
    if errors:
        return JsonResponse({"errors": errors}, status=400)

    # Short-circuit if we have a cached response or a pending request.
    cached_record = get_cached_record(idempotency_key)
    if cached_record:
        if cached_record.get("status") == "pending":
            return JsonResponse(
                {
                    "error": "Request is already pending.",
                    "idempotency_key": idempotency_key,
                },
                status=409,
            )
        if cached_record.get("status") == "completed":
            return JsonResponse(
                cached_record.get("response", {}),
                status=int(cached_record.get("status_code", 200)),
            )

    # Accept-and-cache if the third-party gateway is down.
    if not is_third_party_healthy():
        store_pending_request(idempotency_key, clean_data)
        return JsonResponse(
            {
                "status": "accepted",
                "pending": True,
                "idempotency_key": idempotency_key,
            },
            status=202,
        )

    # Attempt to reconcile any earlier pending requests.
    reconcile_pending_requests()

    # Forward the transaction to the third-party gateway.
    status_code, gateway_payload, error = send_payment(clean_data, idempotency_key)
    if error or status_code is None or status_code >= 500:
        store_pending_request(idempotency_key, clean_data)
        return JsonResponse(
            {
                "status": "accepted",
                "pending": True,
                "idempotency_key": idempotency_key,
            },
            status=202,
        )

    # Cache and return the successful response for idempotent retries.
    gateway_payload = gateway_payload or {}
    response_payload = {
        "status": "submitted",
        "idempotency_key": idempotency_key,
        "gateway_response": gateway_payload,
    }

    store_completed_response(idempotency_key, response_payload, status_code)
    return JsonResponse(response_payload, status=status_code)