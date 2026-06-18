"""URL routing for the learning app.

Organizes endpoints by learning chunk:
- Chunk 0: Basic CRUD and consistency (notes).
- Chunk 1: Authentication and authorization (login, logout, user).
- Chunk 2: Filtering, sorting, and pagination (notes with filters, cursor pagination).
"""

from django.urls import path

from learning import views, auth_views

urlpatterns = [
    # ========================================================================
    # CHUNK 0: BASIC CRUD AND CONSISTENCY
    # ========================================================================
    # Collection endpoint for listing and creating notes.
    path("notes/", views.notes_collection, name="notes-collection"),
    # Archive action for a single note.
    path("notes/<int:note_id>/archive/", views.archive_note_view, name="note-archive"),
    # Toggle the cache-backed idempotency feature flag.
    path("idempotency/", views.toggle_idempotency_view, name="toggle-idempotency"),
    # # Transactional forwarding endpoint to demonstrate idempotency.
    # path("transactions/", views.transactional_request, name="transactional-request"),
    # Say hello page.
    path("", views.say_hello, name="hello-world"),

    # ========================================================================
    # CHUNK 1: AUTHENTICATION AND AUTHORIZATION
    # ========================================================================
    # User registration endpoint.
    path("register/", auth_views.create_user_view, name="register"),
    # User login endpoint.
    path("login/", auth_views.login_view, name="login"),
    # User logout endpoint.
    path("logout/", auth_views.logout_view, name="logout"),
    # Get current user info.
    path("me/", auth_views.current_user_view, name="current-user"),

    path("delete/", auth_views.delete_own_account, name="hard-delete"),
    path("deactivate/", auth_views.deactivate_own_account, name="soft-delete"),
    path("reset/", auth_views.update_password, name="password-reset"),
    path("register-group/", auth_views.create_group_view, name="register-group"),
]
