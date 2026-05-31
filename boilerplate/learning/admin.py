"""Admin registrations for the learning app."""

from django.contrib import admin

from learning.models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Expose a friendly view of notes in the Django admin."""

    # Show key fields in the list view for quick scanning.
    list_display = ("id", "title", "is_archived", "created_at")
    # Make it easy to filter by archive status.
    list_filter = ("is_archived",)
    # Enable simple search by title.
    search_fields = ("title",)
