from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals
        import users.audit_signals
        import users.schema  # noqa: F401 — registers drf-spectacular auth extension
