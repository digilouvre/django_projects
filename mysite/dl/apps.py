from django.apps import AppConfig


class DlConfig(AppConfig):
    name = 'dl'

    def ready(self):
        # import signal handlers
        import dl.signals

# class EcommerceAppConfig(AppConfig):
#     name = 'ecommerce_app'

#     def ready(self):
#         # import signal handlers
#         import ecommerce_app.signals
