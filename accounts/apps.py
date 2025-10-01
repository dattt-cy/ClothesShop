from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'
    verbose_name = 'Accounts'

    def ready(self):
        # Import signal handlers; guard so that missing module during certain
        # operations (like collectstatic) doesn't crash startup.
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Logically safe to ignore; signals simply won't be active.
            pass