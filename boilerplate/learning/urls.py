"""URL routing for the learning app."""

from django.urls import path

from learning import views

urlpatterns = [
    # Health check for load balancers.
    path("health/", views.health_check, name="health-check"),
    # Collection endpoint for listing and creating notes.
    path("notes/", views.notes_collection, name="notes-collection"),
    # Archive action for a single note.
    path("notes/<int:note_id>/archive/", views.archive_note_view, name="note-archive"),
    # Say hello
    path("", views.say_hello, name="Hello world"),
]
