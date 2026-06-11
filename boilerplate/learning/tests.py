"""Tests for the learning app endpoints."""

from __future__ import annotations

import json
from unittest.mock import patch

from django.test import Client, TestCase
from django.core.cache import cache
from django.contrib.auth import get_user_model

from learning.models import Note

User = get_user_model()


class NotesApiTests(TestCase):
    """Exercise the JSON endpoints with CSRF protection enabled."""

    def setUp(self):
        # Enforce CSRF checks so tests mirror browser behavior.
        self.client = Client(enforce_csrf_checks=True)

    def _csrf_token(self) -> str:
        # Trigger a GET to receive a CSRF cookie.
        response = self.client.get("/api/notes/")
        return response.cookies["csrftoken"].value

    def test_health_check(self):
        # Validate that the health endpoint is stable.
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_list_notes_empty(self):
        # The list endpoint should return an empty collection initially.
        response = self.client.get("/api/notes/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["notes"], [])
        self.assertEqual(payload["meta"]["count"], 0)

    def test_create_note(self):
        # POST requires a CSRF token and valid JSON body.
        csrf_token = self._csrf_token()
        response = self.client.post(
            "/api/notes/",
            data=json.dumps({"title": "First note", "body": "Hello"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Note.objects.count(), 1)

    def test_archive_note(self):
        # Archiving should flip the is_archived flag.
        note = Note.objects.create(title="Archive me", body="")
        csrf_token = self._csrf_token()
        response = self.client.post(
            f"/api/notes/{note.id}/archive/",
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 200)
        note.refresh_from_db()
        self.assertTrue(note.is_archived)


# ============================================================================
# CHUNK 2: FILTERING, SORTING, AND PAGINATION TESTS
# ============================================================================

class NotesFilteringAndSortingTests(TestCase):
    """Test filtering, sorting, and pagination features."""

    def setUp(self):
        # Create test notes with varied properties.
        self.client = Client(enforce_csrf_checks=True)
        Note.objects.create(title="Apple Note", body="Fruit", is_archived=False)
        Note.objects.create(title="Banana Note", body="Yellow", is_archived=False)
        Note.objects.create(title="Cherry Note", body="Red", is_archived=True)

    def _csrf_token(self) -> str:
        response = self.client.get("/api/notes/")
        return response.cookies["csrftoken"].value

    def test_filter_by_title(self):
        """
        Filtering by title using case-insensitive substring search.
        Flow: request -> query param validation -> filter -> serialize -> response.
        """
        # Fetch notes matching "apple" (case-insensitive).
        response = self.client.get("/api/notes/?title=apple")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["notes"]), 1)
        self.assertEqual(payload["notes"][0]["title"], "Apple Note")

    def test_filter_include_archived(self):
        """
        Filtering to include archived notes.
        Query: ?include_archived=1
        """
        # By default, archived notes are hidden.
        response = self.client.get("/api/notes/")
        payload = response.json()
        self.assertEqual(payload["meta"]["count"], 2)

        # With include_archived=1, both archived and active notes show.
        response = self.client.get("/api/notes/?include_archived=1")
        payload = response.json()
        self.assertEqual(payload["meta"]["count"], 3)

    def test_sort_by_title_ascending(self):
        """
        Sorting notes by title in ascending order.
        Query: ?sort=title
        """
        response = self.client.get("/api/notes/?sort=title&include_archived=1")
        payload = response.json()
        titles = [note["title"] for note in payload["notes"]]
        self.assertEqual(titles, ["Apple Note", "Banana Note", "Cherry Note"])

    def test_sort_by_created_at_descending(self):
        """
        Sorting notes by created_at in descending order (newest first).
        Query: ?sort=-created_at (default behavior)
        """
        response = self.client.get("/api/notes/?sort=-created_at&include_archived=1")
        payload = response.json()
        # Descending order means last-created first.
        titles = [note["title"] for note in payload["notes"]]
        self.assertEqual(titles, ["Cherry Note", "Banana Note", "Apple Note"])

    def test_invalid_sort_field_rejected(self):
        """
        Allowlist validation should reject disallowed sort fields.
        Attack: ?sort=__class__ or other SQL injection attempts.
        """
        response = self.client.get("/api/notes/?sort=__class__")
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertIn("error", payload)

    def test_pagination_limit_and_offset(self):
        """
        Pagination with configurable limit and offset.
        Query: ?limit=1&offset=0
        """
        # Fetch first page (limit=1).
        response = self.client.get("/api/notes/?limit=1&offset=0")
        payload = response.json()
        self.assertEqual(len(payload["notes"]), 1)
        self.assertEqual(payload["meta"]["offset"], 0)
        self.assertEqual(payload["meta"]["next_offset"], 1)

        # Fetch second page (limit=1, offset=1).
        response = self.client.get("/api/notes/?limit=1&offset=1")
        payload = response.json()
        self.assertEqual(len(payload["notes"]), 1)
        self.assertEqual(payload["meta"]["offset"], 1)

    def test_limit_capped_at_max(self):
        """
        Limit parameter is capped to prevent resource exhaustion.
        Query: ?limit=1000 -> capped to 50.
        """
        response = self.client.get("/api/notes/?limit=1000")
        payload = response.json()
        self.assertEqual(payload["meta"]["limit"], 50)  # Max is 50.

    def test_cursor_pagination(self):
        """
        Cursor-based pagination for stable scrolling.
        First request: no cursor -> get first page + next_cursor.
        Next request: cursor=X -> get page starting after ID X.
        """
        # First page: no cursor.
        response = self.client.get("/api/notes-cursor/?limit=2&include_archived=1")
        payload = response.json()
        # Should get 2 items.
        self.assertEqual(len(payload["notes"]), 2)
        self.assertIsNotNone(payload["next_cursor"])
        first_next_cursor = payload["next_cursor"]

        # Second page: use cursor from first response (must also pass include_archived=1).
        response = self.client.get(f"/api/notes-cursor/?limit=2&cursor={first_next_cursor}&include_archived=1")
        payload = response.json()
        # Should get remaining 1 item.
        self.assertEqual(len(payload["notes"]), 1)
        self.assertIsNone(payload["next_cursor"])  # No more pages.


class TransactionalApiTests(TestCase):
    """Exercise transactional forwarding and idempotency behavior."""

    def setUp(self):
        self.client = Client()
        cache.clear()

    def _payload(self) -> dict[str, str]:
        return {
            "amount": "42.50",
            "currency": "usd",
            "reference": "order-123",
            "description": "Demo transaction",
        }

    def test_missing_idempotency_key(self):
        response = self.client.post(
            "/api/transactions/",
            data=json.dumps(self._payload()),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    @patch("learning.views.is_third_party_healthy", return_value=False)
    def test_unhealthy_gateway_creates_pending_record(self, _mock_health):
        response = self.client.post(
            "/api/transactions/",
            data=json.dumps(self._payload()),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="idem-1",
        )
        self.assertEqual(response.status_code, 202)

        duplicate = self.client.post(
            "/api/transactions/",
            data=json.dumps(self._payload()),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="idem-1",
        )
        self.assertEqual(duplicate.status_code, 409)

    @patch("learning.views.send_payment", return_value=(201, {"state": "completed"}, None))
    @patch("learning.views.is_third_party_healthy", return_value=True)
    def test_successful_gateway_response_is_cached(self, _mock_health, _mock_send):
        response = self.client.post(
            "/api/transactions/",
            data=json.dumps(self._payload()),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="idem-2",
        )
        self.assertEqual(response.status_code, 201)

        cached = self.client.post(
            "/api/transactions/",
            data=json.dumps(self._payload()),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="idem-2",
        )
        self.assertEqual(cached.status_code, 201)


# ============================================================================
# CHUNK 1: AUTHENTICATION AND AUTHORIZATION TESTS
# ============================================================================

class AuthenticationTests(TestCase):
    """Test login, logout, registration, and session auth."""

    def setUp(self):
        # Create a test user for auth checks.
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="securepassword123",
        )

    def _csrf_token(self) -> str:
        # Fetch CSRF token from a GET endpoint that requires CSRF protection.
        response = self.client.get("/api/login/")
        return response.cookies["csrftoken"].value

    def test_register_new_user(self):
        """
        Registration endpoint creates a new user and logs them in.
        Flow: POST /register -> validate -> create User -> login -> response.
        """
        csrf_token = self._csrf_token()
        response = self.client.post(
            "/api/register/",
            data=json.dumps({
                "email": "newuser@example.com",
                "password": "newpassword123",
                "first_name": "New",
            }),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["user"]["email"], "newuser@example.com")
        # User should exist in DB.
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_register_duplicate_email_rejected(self):
        """
        Registration with an existing email is rejected with 409 Conflict.
        """
        csrf_token = self._csrf_token()
        response = self.client.post(
            "/api/register/",
            data=json.dumps({
                "email": "testuser@example.com",  # Already exists.
                "password": "password123",
                "first_name": "Dup",
            }),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 409)

    def test_register_weak_password_rejected(self):
        """
        Passwords shorter than 8 chars are rejected.
        """
        csrf_token = self._csrf_token()
        response = self.client.post(
            "/api/register/",
            data=json.dumps({
                "email": "weakpass@example.com",
                "password": "short",  # Too short.
                "first_name": "Weak",
            }),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 400)

    def test_login_with_email_and_password(self):
        """
        Login using email and password via SimpleEmailBackend.
        Flow: POST /login -> authenticate(email, password) -> create session -> response.
        """
        csrf_token = self._csrf_token()
        response = self.client.post(
            "/api/login/",
            data=json.dumps({
                "email": "testuser@example.com",
                "password": "securepassword123",
            }),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["user"]["id"], self.user.id)
        self.assertEqual(payload["user"]["email"], "testuser@example.com")

    def test_login_invalid_password_rejected(self):
        """
        Login with wrong password returns 401 Unauthorized.
        """
        csrf_token = self._csrf_token()
        response = self.client.post(
            "/api/login/",
            data=json.dumps({
                "email": "testuser@example.com",
                "password": "wrongpassword",
            }),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 401)

    def test_login_nonexistent_user(self):
        """
        Login for non-existent user returns 401 Unauthorized.
        """
        csrf_token = self._csrf_token()
        response = self.client.post(
            "/api/login/",
            data=json.dumps({
                "email": "nonexistent@example.com",
                "password": "somepassword",
            }),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 401)

    def test_logout_clears_session(self):
        """
        Logout endpoint clears the session.
        Flow: POST /logout -> clear session -> response.
        """
        # First, log in.
        csrf_token = self._csrf_token()
        login_response = self.client.post(
            "/api/login/",
            data=json.dumps({
                "email": "testuser@example.com",
                "password": "securepassword123",
            }),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(login_response.status_code, 200)

        # Now log out.
        csrf_token = self._csrf_token()
        logout_response = self.client.post(
            "/api/logout/",
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(logout_response.status_code, 200)
        payload = logout_response.json()
        self.assertEqual(payload["status"], "logged out")

    def test_current_user_when_authenticated(self):
        """
        GET /me/ returns the current authenticated user.
        """
        # Log in first.
        csrf_token = self._csrf_token()
        self.client.post(
            "/api/login/",
            data=json.dumps({
                "email": "testuser@example.com",
                "password": "securepassword123",
            }),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        # Fetch current user.
        response = self.client.get("/api/me/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["user"]["email"], "testuser@example.com")

    def test_current_user_when_unauthenticated(self):
        """
        GET /me/ without session returns 401 Unauthorized.
        """
        response = self.client.get("/api/me/")
        self.assertEqual(response.status_code, 401)
        payload = response.json()
        self.assertIn("error", payload)

    def test_my_notes_requires_authentication(self):
        """
        GET /my-notes/ requires authentication.
        Unauthenticated: 401.
        Authenticated: 200 with filtered notes.
        """
        # Create a note.
        Note.objects.create(title="My Note", body="Private")

        # Unauthenticated request should fail.
        response = self.client.get("/api/my-notes/")
        self.assertEqual(response.status_code, 401)

        # Log in.
        csrf_token = self._csrf_token()
        self.client.post(
            "/api/login/",
            data=json.dumps({
                "email": "testuser@example.com",
                "password": "securepassword123",
            }),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        # Now authenticated request should succeed.
        response = self.client.get("/api/my-notes/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        # Should return notes (currently all notes; real app would filter by user).
        self.assertGreater(len(payload["notes"]), 0)
