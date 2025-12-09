from django.apps import AppConfig


class RappisafeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rappiSafe'

    def ready(self):
        import rappiSafe.signals
