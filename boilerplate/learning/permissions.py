"""Permission classes and authorization helpers for the learning app.

This module demonstrates object-level access control. Permissions check what
an authenticated user is allowed to do (read, write, delete, etc.).
Unlike authentication (who are you?), authorization answers: what can you do?

Patterns:
- View-level: Enforce minimum auth status (is_authenticated).
- Object-level: Check if user owns or has grant to the specific object.
- Role-based: Check user.groups or user.is_staff for role grants.

In Chunk 1, we implement custom permission classses that can be mixed into views.
"""

from __future__ import annotations

from typing import Protocol


class PermissionChecker(Protocol):
    """
    Protocol (duck type) for checking permissions.

    Any callable or object matching this interface can be used.
    Allows custom permission logic without strict inheritance.
    """

    def __call__(self, user, obj: object | None = None) -> bool:
        """
        Check if user has permission.

        Args:
            user: Django User instance (may be AnonymousUser).
            obj: Object being accessed (e.g., a Note instance), if applicable.

        Returns:
            True if allowed, False otherwise.
        """
        ...


def is_authenticated(user) -> bool:
    """
    Check that the user is authenticated (not AnonymousUser).

    Usage:
        if not is_authenticated(request.user):
            return JsonResponse({"error": "Login required."}, status=401)
    """
    return user.is_authenticated


def is_owner(user, obj: object) -> bool:
    """
    Check if user is the owner of an object.

    Common pattern: user.id == obj.user_id.
    This requires the object to have a 'user' or 'user_id' field.

    Usage:
        if not is_owner(request.user, note):
            return JsonResponse({"error": "Not your note."}, status=403)
    """

    # Guard: object must have a user reference.
    if not hasattr(obj, "user") and not hasattr(obj, "user_id"):
        return False

    # Compare user instances or IDs.
    obj_user_id = obj.user_id if hasattr(obj, "user_id") else obj.user.id
    return user.id == obj_user_id


def is_staff(user) -> bool:
    """
    Check if user is a staff member (admin).

    Common pattern for admin-only endpoints.

    Usage:
        if not is_staff(request.user):
            return JsonResponse({"error": "Admin access required."}, status=403)
    """
    return user.is_staff


def has_group(user, group_name: str) -> bool:
    """
    Check if user belongs to a specific group.

    Groups are Django's way of assigning permissions to cohorts of users.

    Usage:
        if not has_group(request.user, "editors"):
            return JsonResponse({"error": "Editor access required."}, status=403)
    """
    return user.groups.filter(name=group_name).exists()


class PermissionMixin:
    """
    Mixin for views that need permission checks.

    Subclasses set permission_checkers and call check_permissions() before processing.
    Separates auth concerns from business logic.

    Example:
        class MyView(PermissionMixin):
            permission_checkers = [is_authenticated, (is_owner, 'obj')]

            def dispatch(self, request, *args, **kwargs):
                self.check_permissions(request)
                return super().dispatch(request, *args, **kwargs)
    """

    permission_checkers: list[PermissionChecker | tuple[PermissionChecker, str]] = []

    def check_permissions(self, request, obj: object | None = None) -> None:
        """
        Run all permission checkers and raise if any fail.

        Args:
            request: The incoming HTTP request.
            obj: Optional object for object-level checks.

        Raises:
            PermissionDenied: If any checker returns False.
        """

        # Import here to avoid circular dependencies.
        from django.core.exceptions import PermissionDenied

        for checker in self.permission_checkers:
            # Unpack (checker, obj_attr) tuples to get the object from request.
            if isinstance(checker, tuple):
                perm_func, obj_attr = checker
                obj = getattr(self, obj_attr, obj)
            else:
                perm_func = checker

            # Run the permission check.
            if not perm_func(request.user, obj):
                raise PermissionDenied()


# Common permission sets you can reuse.

PERMISSIONS_AUTHENTICATED_ONLY = [is_authenticated]
"""Allow only logged-in users."""

PERMISSIONS_ADMIN_ONLY = [is_authenticated, is_staff]
"""Allow only admin users."""

PERMISSIONS_OWNER_ONLY = [is_authenticated]
"""Allow owner; object-level check in view. Use with (is_owner, 'obj') in view."""

PERMISSIONS_EDITOR_GROUP = [is_authenticated, lambda u: has_group(u, "editors")]
"""Allow members of the 'editors' group."""

