"""
Authentication app configuration for Kwantum Institute.
"""
from django.apps import AppConfig
from typing import ClassVar


class AuthenticationConfig(AppConfig):
    """Configuration for the authentication app."""
    
    default_auto_field: ClassVar[str] = 'django.db.models.BigAutoField'
    name: ClassVar[str] = 'authentication'
    verbose_name: ClassVar[str] = 'Authentication System'
    
    def ready(self) -> None:
        """Initialize app when ready."""
        try:
            import authentication.signals  # noqa: F401
        except ImportError:
            pass 