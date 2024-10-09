from django.apps import AppConfig


class UMessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'U_messages'

    def ready(self):
        import U_messages.signals  # Import the signals to connect them