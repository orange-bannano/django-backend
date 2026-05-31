"""Tests for the learning app endpoints."""

from __future__ import annotations

import json

from django.test import Client, TestCase

from learning.models import Note


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
