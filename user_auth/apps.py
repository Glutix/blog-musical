from django.apps import AppConfig


class UserAuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_auth"

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals
