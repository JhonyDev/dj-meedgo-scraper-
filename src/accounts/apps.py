from django.apps import AppConfig


class AccountsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.accounts'

    def ready(self):
        import src.accounts.models