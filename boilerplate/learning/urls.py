"""URL routing for the learning app.

Organizes endpoints by learning chunk:
- Chunk 0: Basic CRUD and consistency (notes).
- Chunk 1: Authentication and authorization (login, logout, user).
- Chunk 2: Filtering, sorting, and pagination (notes with filters, cursor pagination).
"""

from django.urls import path

from learning import views

urlpatterns = [
    # ========================================================================
    # CHUNK 0: BASIC CRUD AND CONSISTENCY
    # ========================================================================
    # Health check for load balancers.
    path("health/", views.health_check, name="health-check"),
    # Collection endpoint for listing and creating notes.
    path("notes/", views.notes_collection, name="notes-collection"),
    # Archive action for a single note.
    path("notes/<int:note_id>/archive/", views.archive_note_view, name="note-archive"),
    # # Transactional forwarding endpoint to demonstrate idempotency.
    # path("transactions/", views.transactional_request, name="transactional-request"),
    # Say hello page.
    path("", views.say_hello, name="hello-world"),

    # ========================================================================
    # CHUNK 1: AUTHENTICATION AND AUTHORIZATION
    # ========================================================================
    # User registration endpoint.
    path("register/", views.create_user_view, name="register"),
    # User login endpoint.
    path("login/", views.login_view, name="login"),
    # User logout endpoint.
    path("logout/", views.logout_view, name="logout"),
    # Get current user info.
    path("me/", views.current_user_view, name="current-user"),

    path("delete/", views.delete_own_account, name="hard-delete"),
    path("deactivate/", views.deactivate_own_account, name="soft-delete"),
    path("reset/", views.update_password, name="password-reset"),
    path("register-group/", views.create_group_view, name="register-group"),

    # ========================================================================
    # CHUNK 2: FILTERING, SORTING, AND PAGINATION ENHANCEMENTS
    # ========================================================================
    # # List only authenticated user's notes.
    # path("my-notes/", views.my_notes_view, name="my-notes"),
    # # Cursor-based pagination alternative to offset.
    # path("notes-cursor/", views.notes_with_cursor_pagination, name="notes-cursor"),
    # # Simple web UI for interacting with the learning API (developer convenience).
    # # Serves an HTML page with JavaScript controls so you can exercise endpoints
    # # without manually crafting JSON for each request. Accessible at /api/ui/.
    path("ui/", views.frontend_ui, name="ui"),
]
