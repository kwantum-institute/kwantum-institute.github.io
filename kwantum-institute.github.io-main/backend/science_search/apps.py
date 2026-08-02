"""Django app config for science search middleware."""

from django.apps import AppConfig


class ScienceSearchConfig(AppConfig):
    """Register the science_search application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "science_search"
    verbose_name = "Science Search"
