from django.apps import AppConfig


class UAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'U_auth'

    #def ready(self):
    #    from jobs import updater
    #    updater.start()


