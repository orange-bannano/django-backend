"""HTTP views for the learning app.

The views are intentionally small, delegating data validation and persistence
to helper modules so each concept is easy to copy elsewhere.
"""

from __future__ import annotations
from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

from learning.models import Note, NoteMembership
from learning.permissions import is_authenticated
from learning.serializers import AllowlistValidator
from learning.services import archive_note, create_note, list_notes, resolve_user_role, filter_notes_for_user, \
    can_modify_note, can_delete_note
# from learning.transactions import (
#     get_cached_record,
#     is_third_party_healthy,
#     reconcile_pending_requests,
#     send_payment,
#     store_completed_response,
#     store_pending_request,
# )
from learning.utils import coerce_positive_int, paginate_queryset, parse_json_body
from learning.validators import validate_note_payload #, validate_transaction_payload

User = get_user_model()

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

# ============================================================================
# CHUNK 0: BASIC CRUD AND CONSISTENCY
# ============================================================================

def serialize_note(note: Note) -> dict:
    """Convert a Note model instance into JSON-serializable primitives."""

    memberships = list(
        note.memberships.select_related("user")
    )

    owner = next(
        (m for m in memberships if m.is_owner),
        None,
    )

    # Flatten model fields into JSON-safe primitives.
    return {
        "id": note.id,
        "title": note.title,
        "body": note.body,
        "is_archived": note.is_archived,
        "owner": {
            "id": owner.user_id,
        } if owner else None,
        "members": [
            {
                "user_id": membership.user_id,
                "email": membership.user.email,
                "role": membership.role,
            }
            for membership in memberships
        ],
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat(),
    }

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Return a lightweight response used by monitors and load balancers.

    Postman:
        Method: GET
        URL: /api/health/
        Query params: none
        Body: none
    """

    # Keep the response tiny and deterministic for monitoring.
    return JsonResponse({"status": "ok"})

@csrf_exempt
def say_hello(request):
    """Render a simple HTML template.

    Postman:
        Method: GET
        URL: /api/
        Query params: none
        Body: none
    """
    return render(request, 'hello.html')

# 4 requests per minute per IP address or user, key = "user"
@ratelimit(key="ip", rate="4/m", method="POST", block=True)
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def notes_collection(request):
    """List notes or create a new note in a single endpoint.

    CHUNK 0:
        GET:    List notes the current user can access, with pagination.
        POST:   Create a new note with validation.
        PUT:    Update a note by `note_id` in the JSON body.
        DELETE: Delete a note by `note_id` in the JSON body (admin only).

    CHUNK 2:
        GET:  Supports filtering (title, is_archived) and sorting (title, created_at).
              Uses allowlists to prevent SQL injection.

    Postman:
        GET /api/notes/?limit=10&offset=0&sort=-created_at&title=django&title=python&include_archived=0

        POST /api/notes/
        {
            "title": "Django ORM basics",
            "body": "Review select_related and prefetch_related."
        }

        PUT /api/notes/
        {
            "note_id": 12,
            "title": "Updated title",
            "body": "Updated body"
        }

        DELETE /api/notes/
        {
            "note_id": 12
        }
    """

    if not is_authenticated(request.user):
        return JsonResponse({"error": "Authentication required."}, status=401)

    # ========================================================================
    # CHUNK 0 + 2: WRITE PATH - Create a new note with validation
    # ========================================================================
    if request.method == "POST":
        # Parse JSON input with size guards.
        payload, error_message = parse_json_body(request)
        if error_message:
            return JsonResponse({"error": error_message}, status=400)

        # Validate the payload structure and content before database write.
        clean_data, errors = validate_note_payload(payload)
        if errors:
            return JsonResponse({"errors": errors}, status=400)

        # Delegate persistence to the service layer.
        # **clean_data unpacks the dictionary into keyword arguments.
        note = create_note(owner=request.user, **clean_data)
        # return JsonResponse({"note": serialize_note(note)}, status=201)

        # When concatenation is used vulnerability persists
        html = f"""
        <html>
        <body>
            <h1>Note Created</h1>

            <h2>{note.title}</h2>

            <div>
                {note.body}
            </div>
        </body>
        </html>
        """
        return HttpResponse(html, status=201)

        # template variables are auto-escaped
        # return render(
        #     request,
        #     "note_created.html",
        #     {
        #         "note": note,
        #     },
        #     status=201,
        # )

    if request.method in {"PUT", "DELETE"}:
        payload, error_message = parse_json_body(request)
        if error_message:
            return JsonResponse({"error": error_message}, status=400)

        note_id = payload.get("note_id")
        try:
            note_id = int(note_id)
        except (TypeError, ValueError):
            return JsonResponse({"error": "note_id must be a valid integer."}, status=400)

        try:
            note = Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            return JsonResponse({"error": "Note not found."}, status=404)

        if request.method == "DELETE":
            if not can_delete_note(request.user):
                return JsonResponse({"error": "Admin access required."}, status=403)
            note.delete()
            return JsonResponse({"status": "deleted", "note_id": note_id})

        if not can_modify_note(request.user, note):
            return JsonResponse({"error": "You do not have permission to modify this note."}, status=403)

        merged_payload = {
            "title": payload.get("title", note.title),
            "body": payload.get("body", note.body),
        }
        clean_data, errors = validate_note_payload(merged_payload)
        if errors:
            return JsonResponse({"errors": errors}, status=400)

        note.title = clean_data["title"]
        note.body = clean_data["body"]
        note.full_clean()
        note.save(update_fields=["title", "body", "updated_at"])
        return JsonResponse({"note": serialize_note(note)})

    # ========================================================================
    # CHUNK 2: READ PATH - List with filtering and sorting support
    # ========================================================================

    # Extract query parameters for pagination.
    # Eg: GET /api/notes/?limit=5&offset=10
    limit = coerce_positive_int(request.GET.get("limit"), default=10, max_value=50)
    offset = coerce_positive_int(request.GET.get("offset"), default=0, max_value=10_000)

    # START: Chunk 2 - Safe filtering with allowlist pattern.

    # Define which fields can be filtered and sorted on (prevents SQL injection).
    ALLOWED_FILTER_FIELDS = {"title", "is_archived"}
    ALLOWED_SORT_FIELDS = {"title", "created_at"}
    validator = AllowlistValidator(allowed_fields=ALLOWED_FILTER_FIELDS | ALLOWED_SORT_FIELDS)

    # Determine if archived notes should be included.
    include_archived = request.GET.get("include_archived") == "1"

    # Example: /api/notes/?title=django&title=python
    title_params = request.GET.getlist("title")
    # Use __icontains for case-insensitive substring search (safe: no user SQL).
    query = Q()
    for keyword in title_params:
        query |= Q(title__icontains=keyword)

    # https://docs.djangoproject.com/en/6.0/ref/models/expressions/#query-expressions
    # Extract and validate sort parameter (default: -created_at for newest first, created_at for descending).
    sort_param = request.GET.get("sort", "-created_at").strip()
    try:
        sort_param = validator.validate_sort(sort_param)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    # END: Chunk 2 - Safe filtering and sorting.

    # Apply filters and sorting to the queryset, passing include_archived separately.
    queryset = filter_notes_for_user(
        list_notes(include_archived=include_archived, query=query),
        request.user,
    ).order_by(sort_param)
    total_count = queryset.count()

    # Slice the paginated subset.
    page_items, meta = paginate_queryset(
        # The slicing happens before entering paginate_queryset.
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

@csrf_exempt
@require_http_methods(["POST"])
def archive_note_view(request, note_id: int):
    """Archive a note and return the updated resource.

    Postman:
        Method: POST
        URL: /api/notes/<note_id>/archive/
        Example URL: /api/notes/12/archive/
        Query params: none
        Body: none
    """

    # Keep the database lookup in the service layer; handle missing rows here.
    try:
        note = archive_note(note_id=note_id)
    except Note.DoesNotExist:
        return JsonResponse({"error": "Note not found."}, status=404)

    return JsonResponse({"note": serialize_note(note)})

# ============================================================================
# CHUNK 1: AUTHENTICATION AND AUTHORIZATION
# ============================================================================

def is_authenticated_or_error(user):
    if user.is_authenticated:
        return True
    raise PermissionDenied  # Throws an HTTP 403 error

def is_admin(user):
    if user.groups.filter(name="Admin").exists() | user.is_superuser:
        return True
    raise PermissionDenied  # Throws an HTTP 403 error

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """
    Authenticate a user via email and password, create a session, and return status.

    Flow: request -> CSRF check -> parse JSON -> authenticate() -> create session -> response.

    Clients send:
        POST /api/login/
        {"email": "user@example.com", "password": "secret"}

    Response:
        200: {"user": {"id": 1, "email": "user@example.com"}}
        400: {"error": "Invalid credentials."}
        401: {"error": "Authentication failed."}

    Postman:
        Method: POST
        URL: /api/login/
        Body:
        {
            "email": "admin@example.com",
            "password": "secret123"
        }
    """
    resp = rate_limit_ip(request)
    if resp:
        return resp

    # Parse JSON input.
    payload, error_message = parse_json_body(request)
    if error_message:
        return JsonResponse({"error": error_message}, status=400)

    # Extract credentials and guard against missing fields.
    email = payload.get("email", "").strip()
    password = payload.get("password", "").strip()
    if not email or not password:
        return JsonResponse(
            {"error": "Email and password are required."},
            status=400,
        )

    # https://docs.djangoproject.com/en/6.0/topics/auth/default/#django.contrib.auth.login
    # Authenticate using the custom email backend.
    # authenticate() queries all backends in AUTHENTICATION_BACKENDS. If the first authentication method fails, Django tries the second one, and so on, until all backends have been attempted.
    user = authenticate(request=request, email=email, password=password)
    #  If the credentials aren’t valid for any backend or if a backend raises PermissionDenied, it returns None.
    if user is None:
        return JsonResponse(
            {"error": "Invalid credentials."},
            status=401,
        )

    # Create a session cookie for the authenticated user.
    # This sets request.user and persists across future requests in which specified backend is used to fetch user details.
    login(request, user, backend='learning.auth_backends.SimpleEmailBackend')

    # Return user info (safe: no sensitive data like passwords).
    return JsonResponse({
        "user": {
            "id": user.id,
            "email": user.email,
            "is_staff": user.is_staff,
        }
    })

@user_passes_test(is_authenticated_or_error)
@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    """
    Clear the user's session and return success.

    Flow: request -> CSRF check -> clear session -> response.

    Response:
        200: {"status": "logged out"}

    Postman:
        Method: POST
        URL: /api/logout/
        Query params: none
        Body: none
        Auth: session cookie from login
    """

    # Clear the session for this user.
    logout(request)

    return JsonResponse({"status": "logged out"})

@user_passes_test(is_authenticated_or_error)
@csrf_exempt
@require_http_methods(["GET"])
def current_user_view(request):
    """
    Return the currently authenticated user's information.

    Flow: request -> check auth -> return user -> response.

    Response (authenticated):
        200: {"user": {"id": 1, "email": "user@example.com"}}

    Response (unauthenticated):
        401: {"error": "Authentication required."}

    Postman:
        Method: GET
        URL: /api/me/
        Query params: none
        Body: none
        Auth: session cookie from login
    """

    # # Check that the user is authenticated.
    # if not is_authenticated(request.user):
    #     return JsonResponse(
    #         {"error": "Authentication required."},
    #         status=401,
    #     )

    return JsonResponse({
        "user": {
            "id": request.user.id,
            "email": request.user.email,
            "is_staff": request.user.is_staff,
        }
    })


@user_passes_test(is_authenticated_or_error)
@csrf_exempt
@require_http_methods(["POST"])
def delete_own_account(request):
    """Delete the currently authenticated user account.

    Postman:
        Method: POST
        URL: /api/delete/
        Query params: none
        Body: none
        Auth: session cookie from login
    """

    user = request.user
    logout(request)

    # Delete the user record from the database
    user.delete()

    return JsonResponse({"status": "permanent deleted"})

@user_passes_test(is_authenticated_or_error)
@csrf_exempt
@require_http_methods(["POST"])
def update_password(request):
    """Update the current user's password and log them out.

    Postman:
        Method: POST
        URL: /api/reset/
        Body:
        {
            "password": "new-secret123"
        }
        Auth: session cookie from login
    """
    # Parse JSON input.
    payload, error_message = parse_json_body(request)
    if error_message:
        return JsonResponse({"error": error_message}, status=400)

    new_password = payload.get("password", "")
    user = request.user
    user.set_password(new_password)
    user.save()
    logout(request)
    return JsonResponse({"status": "password updated, please log in again"})

@user_passes_test(is_authenticated_or_error)
@csrf_exempt
@require_http_methods(["POST"])
def deactivate_own_account(request):
    """Deactivate the current user's account and log them out.

    Postman:
        Method: POST
        URL: /api/deactivate/
        Query params: none
        Body: none
        Auth: session cookie from login
    """

    user = request.user
    user.is_active = False
    user.save()
    logout(request)
    return JsonResponse({"status": "soft deleted, logged out"})

@user_passes_test(is_admin)
@csrf_exempt
@require_http_methods(["POST"])
def create_user_view(request):
    """
    Register a new user with email, password, and optional name.

    Flow: request -> CSRF check -> validate -> create User -> create session -> response.

    Clients send:
        POST /api/register/
        {"email": "newuser@example.com", "password": "secret", "first_name": "Alice"}

    Response (success):
        201: {"user": {"id": 2, "email": "newuser@example.com"}}

    Response (conflict):
        409: {"error": "Email already exists."}

    Response (invalid input):
        400: {"error": "..."}

    Postman:
        Method: POST
        URL: /api/register/
        Body:
        {
            "email": "newuser@example.com",
            "password": "secret123",
            "first_name": "Alice",
            "role": "Viewer"
        }
        Auth: admin session cookie
    """
    # Parse JSON input.
    payload, error_message = parse_json_body(request)
    if error_message:
        return JsonResponse({"error": error_message}, status=400)

    # Extract fields and validate format.
    email = payload.get("email", "").strip()
    password = payload.get("password", "").strip()
    first_name = payload.get("first_name", "").strip()
    role = payload.get("role", "Viewer").strip()

    # Guard against missing required fields.
    if not email or not password:
        return JsonResponse(
            {"error": "Email and password are required."},
            status=400,
        )

    # Validate email format (simple check; use django.core.validators for production).
    if "@" not in email:
        return JsonResponse(
            {"error": "Invalid email format."},
            status=400,
        )

    # Check for duplicate email (prevent unique constraint violation later).
    if User.objects.filter(email=email).exists():
        return JsonResponse(
            {"error": "Email already exists."},
            status=409,
        )

    # Enforce a minimal password length for this learning example. In a
    # production system prefer Django's AUTH_PASSWORD_VALIDATORS setting which
    # provides more comprehensive checks (common password lists, numeric checks, etc.).
    if len(password) < 8:
        return JsonResponse(
            {"error": "Password must be at least 8 characters."},
            status=400,
        )

    group, _ = Group.objects.get_or_create(name=role)

    # Create the user with the validated data.
    user = User.objects.create_user(
        username=email,  # Django requires username; use email for simplicity.
        email=email,
        password=password,
    )
    user.groups.add(group)
    # At this point, user is a User object that has already been saved
    # to the database. You can continue to change its attributes
    # if you want to change other fields.
    user.first_name = first_name
    user.save()

    # Automatically log in the new user using the default backend.
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return JsonResponse({
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
        }
    }, status=201)

def serialize_group(group: Group) -> dict:
    return {
        "id": group.id,
        "name": group.name,
        "permissions": [
            permission.codename
            for permission in group.permissions.all()
        ],
    }

from django.contrib.auth.models import Group, Permission
from django.db import IntegrityError

@user_passes_test(is_admin)
@csrf_exempt
@require_http_methods(["POST"])
def create_group_view(request):
    """Create a group and assign permissions.

    Postman:
        Method: POST
        URL: not currently routed in learning/urls.py
        Body:
        {
            "group": "Editor",
            "permission": ["view_note", "add_note", "change_note"]
        }
        Auth: admin session cookie
    """
    payload, error_message = parse_json_body(request)
    if error_message:
        return JsonResponse(
            {"error": error_message},
            status=400,
        )

    group_name = payload.get("group", "").strip()

    if not group_name:
        return JsonResponse(
            {"error": "Group name is required."},
            status=400,
        )

    permission_codenames = payload.get("permission", ["view_note"])
    if isinstance(permission_codenames, str):
        permission_codenames = [permission_codenames.strip()]
    elif isinstance(permission_codenames, list):
        permission_codenames = [
            str(codename).strip()
            for codename in permission_codenames
            if str(codename).strip()
        ]
    else:
        return JsonResponse(
            {"error": "permission must be a string or list of strings."},
            status=400,
        )

    # permission_codenames = payload.get(
    #     "permission",
    #     ["view_note"],
    # ).strip()
    #
    # try:
    #     permission = Permission.objects.filter(
    #         codename__in=permission_codenames
    #     )
    # except Permission.DoesNotExist:
    #     return JsonResponse(
    #         {"error": f"Unknown permission: {permission_codenames}"},
    #         status=400,
    #     )

    if not permission_codenames:
        return JsonResponse(
            {"error": "At least one permission codename is required."},
            status=400,
        )

    permissions = list(Permission.objects.filter(codename__in=permission_codenames))
    found_codenames = {permission.codename for permission in permissions}
    missing_codenames = [
        codename for codename in permission_codenames if codename not in found_codenames
    ]
    if missing_codenames:
        return JsonResponse(
            {"error": f"Unknown permission(s): {', '.join(missing_codenames)}"},
            status=400,
        )

    try:
        group = Group.objects.create(
            name=group_name
        )
    except IntegrityError:
        return JsonResponse(
            {"error": "Group already exists."},
            status=400,
        )

    group.permissions.add(*permissions)

    return JsonResponse(
        serialize_group(group),
        status=201,
    )

# ============================================================================
# CHUNK 2: FILTERING, SORTING, AND PAGINATION ENHANCEMENTS
# ============================================================================
# @csrf_exempt
# @require_http_methods(["GET"])
# def notes_with_cursor_pagination(request):
#     """
#     Alternative to offset pagination: cursor-based pagination for stable scrolling.
#
#     Offsets can become inconsistent if data changes during pagination.
#     Cursors (opaque tokens) point to specific database rows and are stable.
#
#     Query params:
#         cursor: Opaque token from previous response (URL-or base64-encoded).
#         limit: Page size (default 10, max 50).
#         include_archived: If "1", include archived notes (default false).
#
#     Response includes 'next_cursor' for fetching the next page.
#
#     Note: This is a simplified example. Production uses encrypted cursors.
#
#     Flow: request -> validate -> cursor decode -> apply filters -> limit ->
#           serialize -> encode next_cursor -> response.
#
#     Postman:
#         Method: GET
#         URL: /api/notes-cursor/?limit=5&cursor=25&include_archived=0
#         Query params:
#             limit=5
#             cursor=25
#             include_archived=0
#         Body: none
#     """
#
#     # Extract limit and cursor from query params.
#     limit = coerce_positive_int(request.GET.get("limit"), default=10, max_value=50)
#     cursor_param = request.GET.get("cursor", "").strip()
#     include_archived = request.GET.get("include_archived") == "1"
#
#     # Decode cursors to get the starting ID (simplified; use base64 or JWT in production).
#     start_id = 0
#     if cursor_param:
#         try:
#             start_id = int(cursor_param)
#         except ValueError:
#             return JsonResponse({"error": "Invalid cursor."}, status=400)
#
#     # Fetch one extra row to determine if there's a next page.
#     queryset = Note.objects.filter(id__gt=start_id).order_by("id")
#
#     # Optionally filter archived notes.
#     if not include_archived:
#         queryset = queryset.filter(is_archived=False)
#
#     all_items = list(queryset[: limit + 1])
#
#     # Determine next cursor.
#     has_next = len(all_items) > limit
#     page_items = all_items[:limit]
#     next_cursor = str(page_items[-1].id) if has_next and page_items else None
#
#     return JsonResponse({
#         "notes": [serialize_note(note) for note in page_items],
#         "next_cursor": next_cursor,
#         "has_next": has_next,
#     })
#
#
# @csrf_exempt
# @require_http_methods(["GET"])
# def my_notes_view(request):
#     """
#     List only the current user's notes (protected endpoint).
#
#     Demonstrates ownership-based access control.
#
#     Flow: request -> auth check -> filter by user -> serialize -> response.
#
#     If Note model had a 'user' FK, this would filter by request.user.
#     For now, we just demonstrate the pattern with all notes (owner check in production).
#
#     Response (authenticated):
#         200: {"notes": [...], "meta": {...}}
#
#     Response (unauthenticated):
#         401: {"error": "Authentication required."}
#
#     Postman:
#         Method: GET
#         URL: /api/my-notes/?limit=10&offset=0
#         Query params:
#             limit=10
#             offset=0
#         Body: none
#         Auth: session cookie from login
#     """
#
#     # Enforce authentication before proceeding.
#     if not is_authenticated(request.user):
#         return JsonResponse(
#             {"error": "Authentication required."},
#             status=401,
#         )
#
#     # In a real app, filter by request.user: Note.objects.filter(user=request.user)
#     # For this example, list all non-archived notes (placeholder).
#     queryset = Note.objects.filter(is_archived=False)
#     limit = coerce_positive_int(request.GET.get("limit"), default=10, max_value=50)
#     offset = coerce_positive_int(request.GET.get("offset"), default=0, max_value=10_000)
#
#     total_count = queryset.count()
#     page_items, meta = paginate_queryset(
#         queryset[offset : offset + limit],
#         limit=limit,
#         offset=offset,
#         total_count=total_count,
#     )
#
#     return JsonResponse({
#         "notes": [serialize_note(note) for note in page_items],
#         "meta": meta,
#     })

@csrf_exempt
def frontend_ui(request):
    """
    Developer-facing single-page UI for exercising the learning API.

    This page is intentionally minimal: it loads JavaScript that calls the
    API endpoints (register, login, list/create notes, archive, etc.) so a
    beginner can interact with the backend without crafting raw JSON each time.

    Security notes:
    - The page is served with a CSRF cookie (via @ensure_csrf_cookie). JavaScript
      will read that cookie and attach it to unsafe requests (POST) so the
      existing CSRF protection in views works as-is.
    - This UI is for local development and learning only; do not expose it in
      production without proper access controls.

    Flow: request -> set csrf cookie -> render template -> client-side JS drives API calls.

    Postman:
        Method: GET
        URL: /api/ui/
        Query params: none
        Body: none
    """

    # Render the frontend template located at learning/templates/learning/frontend.html
    return render(request, 'learning/frontend.html')

# @require_http_methods(["POST"])
# @csrf_exempt
# def transactional_request(request):
#     """Forward transactional requests with idempotency protection.
#
#     Postman:
#         Method: POST
#         URL: /api/transactions/
#         Headers:
#             Idempotency-Key: 8f0a9d52-7f40-4a16-b0db-6d7df06e6c11
#         Body:
#         {
#             "reference": "INV-1001",
#             "amount": "499.99",
#             "currency": "INR",
#             "description": "June hosting invoice",
#             "metadata": {
#                 "vendor_id": "vendor-42",
#                 "source": "postman"
#             }
#         }
#     """
#
#     # Parse and validate the incoming JSON payload.
#     payload, error_message = parse_json_body(request)
#     if error_message:
#         return JsonResponse({"error": error_message}, status=400)
#
#     # Require an idempotency key to prevent duplicate processing.
#     idempotency_key = str(request.headers.get("Idempotency-Key", "")).strip()
#     if not idempotency_key:
#         return JsonResponse({"error": "Idempotency-Key header is required."}, status=400)
#
#     # Validate business fields before calling downstream services.
#     clean_data, errors = validate_transaction_payload(payload)
#     if errors:
#         return JsonResponse({"errors": errors}, status=400)
#
#     # Short-circuit if we have a cached response or a pending request.
#     cached_record = get_cached_record(idempotency_key)
#     if cached_record:
#         if cached_record.get("status") == "pending":
#             return JsonResponse(
#                 {
#                     "error": "Request is already pending.",
#                     "idempotency_key": idempotency_key,
#                 },
#                 status=409,
#             )
#         if cached_record.get("status") == "completed":
#             return JsonResponse(
#                 cached_record.get("response", {}),
#                 status=int(cached_record.get("status_code", 200)),
#             )
#
#     # Accept-and-cache if the third-party gateway is down.
#     if not is_third_party_healthy():
#         store_pending_request(idempotency_key, clean_data)
#         return JsonResponse(
#             {
#                 "status": "accepted",
#                 "pending": True,
#                 "idempotency_key": idempotency_key,
#             },
#             status=202,
#         )
#
#     # Attempt to reconcile any earlier pending requests.
#     reconcile_pending_requests()
#
#     # Forward the transaction to the third-party gateway.
#     status_code, gateway_payload, error = send_payment(clean_data, idempotency_key)
#     if error or status_code is None or status_code >= 500:
#         store_pending_request(idempotency_key, clean_data)
#         return JsonResponse(
#             {
#                 "status": "accepted",
#                 "pending": True,
#                 "idempotency_key": idempotency_key,
#             },
#             status=202,
#         )
#
#     # Cache and return the successful response for idempotent retries.
#     gateway_payload = gateway_payload or {}
#     response_payload = {
#         "status": "submitted",
#         "idempotency_key": idempotency_key,
#         "gateway_response": gateway_payload,
#     }
#
#     store_completed_response(idempotency_key, response_payload, status_code)
#     return JsonResponse(response_payload, status=status_code)

