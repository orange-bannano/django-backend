"""Authentication backends for the learning app.

This module demonstrates custom authentication backends that validate user credentials
and return Django User instances. Backends are queried in order by Django's auth system.
Each backend implements authenticate() to check credentials and get_user() to load by ID.

Auth flow: request -> middleware -> URLs -> view (check request.user) -> permission checks.
Custom backends let you implement session, token, API key, or hybrid auth.
"""

from __future__ import annotations

from django.contrib.auth.backends import ModelBackend
# for custom https://docs.djangoproject.com/en/6.0/topics/auth/customizing/
from django.contrib.auth import get_user_model
from typing import Optional

User = get_user_model()


class SimpleEmailBackend(ModelBackend):
    """
    Allow authentication using email address and password.

    This backend demonstrates overriding Django's default username-based auth.
    In Chunk 1, users can log in with email instead of username.

    Example:
        authenticate(request=request, email="user@example.com", password="secret")
    """

    def authenticate(
        self,
        request,
        email: str | None = None,
        password: str | None = None,
        **kwargs
    ) -> User | None:
        """
        Validate email and password, then return the User or None.

        Args:
            request: The incoming HTTP request.
            email: User's email address.
            password: User's password.
            **kwargs: Ignored; allows flexibility in future parameters.

        Returns:
            User instance if valid, else None.
        """

        # Guard against missing credentials at entry.
        if not email or not password:
            return None

        try:
            # Query user by email; email is unique in our schema.
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Prevent timing attacks by still hashing the password. Expensive operation simulate time taken by successfully auth, prevents attackers from measuring response time to guess valid emails.
            # User().set_password(password)
            return None

        # Check the password hash against the database record and if requested user is not active.
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id: int) -> User | None:
        """
        Retrieve a user by primary key.

        Called by Django after authentication to retrieve the full User instance.
        Allows auth middleware to restore the user from session or token.
        """

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class TokenBackend(ModelBackend):
    """
    Authenticate via a bearer token in the Authorization header.

    This backend demonstrates token-based auth (similar to JWT or API keys).
    In Chunk 1, clients send 'Authorization: Bearer <token>' to authenticate.
    Tokens are validated against stored credentials (e.g., hashed token in DB).

    Example:
        Authorization: Bearer abc123def456
    """

    TOKEN_HEADER_PREFIX = "Bearer"

    def authenticate(self, request, token: str | None = None, **kwargs) -> User | None:
        """
        Validate a bearer token and return the associated User or None.

        Args:
            request: The incoming HTTP request.
            token: The raw token string (extracted by middleware).
            **kwargs: Ignored.

        Returns:
            User instance if token is valid, else None.
        """

        # Guard against missing token.
        if not token:
            return None

        # NOTE: In production, tokens would be stored in DB (often hashed).
        # This example uses a simple in-memory mapping for demonstration.
        # For real apps, use libraries like djangorestframework-simplejwt or django-rest-knox.

        # Dummy token validation: real implementations query the token table.
        VALID_TOKENS = {
            "demo-token-123": 1,  # Maps token to user_id.
            "demo-token-456": 2,
        }

        user_id = VALID_TOKENS.get(token)
        if user_id is None:
            return None

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id: int) -> User | None:
        """Retrieve a user by primary key for session restoration."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

