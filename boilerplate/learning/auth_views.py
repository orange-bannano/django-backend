from __future__ import annotations

import django.core.validators
from django.contrib.auth import authenticate, login, logout, get_user_model, password_validation
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, Permission
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from boilerplate import settings
from learning.services import rate_limit_ip
from learning.utils import parse_json_body


User = get_user_model()

# ============================================================================
# CHUNK 1: AUTHENTICATION AND AUTHORIZATION
# ============================================================================

### USER STATUS MARKER STARTS, NO FUNCTIONAL INFLUENCE ###

# LOGGED_IN_USER_TTL_SECONDS = 86400

@require_http_methods(["GET"])
def auth_frontend_view(request):
    """Render a small UI for login and account operations."""

    return render(request, "learning/auth_frontend.html")


def _logged_in_cache_key(user_id: int) -> str:
    return f"auth:logged-in:{user_id}"


def mark_user_logged_in(user) -> None:
    cache.set(_logged_in_cache_key(user.id), True, timeout=settings.SESSION_COOKIE_AGE)


def mark_user_logged_out(user) -> None:
    cache.delete(_logged_in_cache_key(user.id))


def is_user_logged_in(user) -> bool:
    return bool(cache.get(_logged_in_cache_key(user.id), False))


def serialize_registered_user(user) -> dict:
    return {
        "username": user.username,
        "is_active": user.is_active,
        "is_logged_in": is_user_logged_in(user),
    }

### USER STATUS MARKER ENDS###

def is_authenticated_or_error(user):
    if user.is_authenticated:
        return True
    raise PermissionDenied  # Throws an HTTP 403 error

def is_admin(user):
    if user.groups.filter(name="Admin").exists() | user.is_superuser:
        user.groups.filter()
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
    if user.groups.filter(name="Admin").exists():
        request.session.set_expiry(45)  # 45 seconds, not valid for /admin/
    else:
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)  # 1 hour

    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])

    mark_user_logged_in(user)
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
        200: {"status": "logged out","login session length (in seconds)": 5.5243}

    Postman:
        Method: POST
        URL: /api/logout/
        Query params: none
        Body: none
        Auth: session cookie from login
    """

    user = request.user
    # Clear the session for this user.
    logout(request)
    mark_user_logged_out(user)

    return JsonResponse({"status": "logged out",
                         "login session length (in seconds)": (timezone.now() - user.last_login).total_seconds()
                         })

@user_passes_test(is_authenticated_or_error)
@csrf_exempt
@require_http_methods(["GET"])
def current_user_view(request):
    """
    Return the currently authenticated user's information.

    Flow: request -> check auth -> return user -> response.

    Response (authenticated):
        200: {
            "user": {
                    "id": 8,
                    "email": "admin@gmail.com",
                    "username": "admin@gmail.com",
                    "groups": ["Admin", "Group B"]
                    "is_staff": false,
                    "last login": "2026-06-25T19:20:28.958Z"
                    "first_name": "Ashok",
                    "last_name": "Kumar","
                    }
            }

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
            "username": request.user.username,
            "groups": [serialize_group(group) for group in request.user.groups.all()],
            "is_staff": request.user.is_staff,
            "last_login": request.user.last_login,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
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
    mark_user_logged_out(user)

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
    mark_user_logged_out(user)
    return JsonResponse({"status": "password updated, please log in again"})

@user_passes_test(is_authenticated_or_error)
@csrf_exempt
@require_http_methods(["POST"])
def deactivate_own_account(request):
    """Deactivate the current user's account and log them out. Locks the user out, preventing them to perform CRUD operations. They can still login
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
    mark_user_logged_out(user)
    return JsonResponse({"status": "soft deleted, logged out"})

@user_passes_test(is_admin)
@csrf_exempt
@require_http_methods(["POST"])
def create_user_view(request):
    """
    Register a new user with email, password, and optional user name. Accessible to users with Admin privilege.

    Flow: request -> CSRF check -> validate -> create User -> create session -> response.

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
            "user_name":"new user",
            "password": "secret123",
            "first_name": "Ashok",
            "last_name": "Kumar",
            "groups": ["Employee", "Group A"]
        }
        Auth: admin session cookie
    """
    # Parse JSON input.
    payload, error_message = parse_json_body(request)
    if error_message:
        return JsonResponse({"error": error_message}, status=400)

    # Extract fields and validate format.
    email = payload.get("email", "").strip()
    username = payload.get("user_name", email).strip()
    password = payload.get("password", "").strip()
    first_name = payload.get("first_name", "").strip()
    last_name = payload.get("last_name", first_name).strip()

    # Guard against missing required fields.
    if not email or not password:
        return JsonResponse(
            {"error": "Email and password are required."},
            status=400,
        )

    # Validate email format (simple check; use django.core.validators for production).

    try:
        django.core.validators.validate_email(email)
    except ValidationError as e:
        return JsonResponse({"error": "Invalid Email, which is necessary"}, status=400, )

    # Check for duplicate email (prevent unique constraint violation later).
    if User.objects.filter(email=email).exists():
        return JsonResponse(
            {"error": "Email already exists."},
            status=409,
        )

    # Enforce a minimal password length for this learning example. In a
    # production system prefer Django's AUTH_PASSWORD_VALIDATORS setting which
    # provides more comprehensive checks (common password lists, numeric checks, etc.).
    try:
        # 1. Manually validate the password against AUTH_PASSWORD_VALIDATORS
        password_validation.validate_password(password)
    except ValidationError as e:
        return JsonResponse({"error": "Invalid Password"}, status=400,)

    # group, _ = Group.objects.get(name=role)
    unfiltered_groups = payload.get("groups", ["Employee"])
    if isinstance(unfiltered_groups, str):
        unfiltered_groups = [unfiltered_groups.strip()]
    elif isinstance(unfiltered_groups, list):
        unfiltered_groups = [
            str(codename).strip()
            for codename in unfiltered_groups
            if str(codename).strip()
        ]
    else:
        return JsonResponse(
            {"error": "Group or Role must be a string or list of strings."},
            status=400,
        )
    groups = list(Group.objects.filter(codename__in=unfiltered_groups))

    # Create the user with the validated data.
    user = User.objects.create_user(
        username=username,  # Django requires username; use email for simplicity.
        email=email,
        password=password,
    )
    user.groups.add(*groups)
    # At this point, user is a User object that has already been saved
    # to the database. You can continue to change its attributes
    # if you want to change other fields.
    user.first_name = first_name
    user.last_name = last_name
    user.save()

    # Automatically log in the new user using the default backend.
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    mark_user_logged_in(user)

    return JsonResponse({
        "user": {
            "id": user.id,
            # "user_name": user.username,
            "email": user.email,
            # "first_name": user.first_name,
            # "last_name": user.last_name,
        }
    }, status=201)

@user_passes_test(is_admin)
@require_http_methods(["GET"])
def registered_users_view(request):
    """Return registered users with active and logged-in status. Accessible to users with Admin privilege."""

    users = User.objects.order_by("username").only("id", "username", "is_active")
    return JsonResponse(
        {
            "users": [serialize_registered_user(user) for user in users],
        }
    )

def serialize_group(group: Group) -> dict:
    return {
        "id": group.id,
        "name": group.name,
        "permissions": [
            permission.codename
            for permission in group.permissions.all()
        ],
    }


@require_http_methods(["GET"])
def groups_view(request):
    """Return all groups and their permissions."""

    groups = Group.objects.order_by("name").prefetch_related("permissions")
    return JsonResponse(
        {
            "groups": [serialize_group(group) for group in groups],
        }
    )

from django.contrib.auth.models import Group, Permission
from django.db import IntegrityError

@user_passes_test(is_admin)
@csrf_exempt
@require_http_methods(["POST"])
def create_group_view(request):
    """Create a group and assign permissions.

    Response (success):
        201: {"id": 2, "name": "Manager", "permissions": ["view_note", "add_note", "change_note"]}

    Response (conflict):
        409: {"error": "Group already exists."}

    Response (invalid input):
        400: {"error": "Unknown permission(s): {permission1, permission2}"}
        400: {"error": "Group name is required."}
        400: {"error": "permission must be a string or list of strings."}
        400: {"error": "..."}

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

    # if not permission_codenames:
    #     return JsonResponse(
    #         {"error": "At least one permission codename is required."},
    #         status=400,
    #     )

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
            status=409,
        )

    group.permissions.add(*permissions)

    return JsonResponse(
        serialize_group(group),
        status=201,
    )
