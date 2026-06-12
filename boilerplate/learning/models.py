"""Database models used by the learning app."""
# A model is the single, definitive source of information about your data.
# It contains the essential fields and behaviors of the data you’re storing. Django follows the DRY Principle.
from django.contrib.auth.models import User
from django.db import models


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

    def __str__(self) -> str:
        # Human-readable representation for admin and logs.
        return f"Note(id={self.pk}, title={self.title!r})"


class NoteMembership(models.Model):
    """Link a user to a note and capture ownership plus effective role."""

    ROLE_EMPLOYEE = "Employee"
    ROLE_MANAGER = "Manager"
    ROLE_ADMIN = "Admin"
    ROLE_CHOICES = [
        (ROLE_EMPLOYEE, "Employee"),
        (ROLE_MANAGER, "Manager"),
        (ROLE_ADMIN, "Admin"),
    ]

    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="note_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_EMPLOYEE,
    )
    is_owner = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["note", "user"],
                name="unique_note_membership",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"NoteMembership(note_id={self.note_id}, user_id={self.user_id}, "
            f"role={self.role!r}, is_owner={self.is_owner})"
        )
