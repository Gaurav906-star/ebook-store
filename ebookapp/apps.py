from django.apps import AppConfig


class EbookappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ebookapp'
    
    
    def ready(self):
        import ebookapp.signals


