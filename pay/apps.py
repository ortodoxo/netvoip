from django.apps import AppConfig

class PayConfig(AppConfig):
    name = 'pay'
    verbose_name = 'Pay aplications'

    def ready(self):
        import pay.signals