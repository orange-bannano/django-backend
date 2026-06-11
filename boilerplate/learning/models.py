"""Database models used by the learning app."""
from django.contrib.auth.models import User
# A model is the single, definitive source of information about your data.
# It contains the essential fields and behaviors of the data you’re storing. Django follows the DRY Principle.
from django.db import models

from boilerplate import settings


class Note(models.Model):
    """A minimal model used to demonstrate CRUD, validation, and consistency."""

    # Core content fields used by the JSON API.
    title = models.CharField(max_length=500)
    body = models.TextField(blank=True)
    # Archive flag lets us keep records without deleting.
    is_archived = models.BooleanField(default=False)
    # Timestamps help demonstrate ordering and updates.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField("UPDATED ON?", auto_now=True)
    # we’ve only defined a human-readable name for Note.updated_at, for other machine name is suffice.
    # NOTE: a relationship is defined, using ForeignKey.
    # after making changes to model run 'python manage.py makemigrations learning'
    # makemigrations packages your model updates into local Python blueprint files (changes migrations/0001_initial.py , detailing the explicit Python code needed to implement those changes)
    # while migrate executes those files to modify your actual live database table (modifies schema, creates or updates tables).
    # use 'python manage.py sqlmigrate polls 0001' to see SQL commands django gonna use, useful to check before migrating critical database.

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_notes",
    )

    shared_with = models.ManyToManyField(
        User,
        related_name="shared_notes",
        blank=True,
    )


    def __str__(self) -> str:
        # Human-readable representation for admin and logs.
        return f"Note(id={self.pk}, title={self.title!r})"