"""Application configuration for the learning app."""

from django.apps import AppConfig


class LearningConfig(AppConfig):
    """Configures default settings for the learning app."""

    # Use big integers for primary keys by default.
    default_auto_field = "django.db.models.BigAutoField"
    # Django app label for discovery.
    name = "learning"
