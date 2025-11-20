"""
SSO app configuration.
"""
from django.apps import AppConfig


class SsoConfig(AppConfig):
    """SSO app configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sso'
    verbose_name = 'Single Sign-On'

    def ready(self):
        """Import signals when app is ready."""
        import apps.sso.signals  # noqa
