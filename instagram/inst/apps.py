from django.apps import AppConfig


class InstConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inst'

    def ready(self):
        import inst.signals  # Import the signals when the app is ready