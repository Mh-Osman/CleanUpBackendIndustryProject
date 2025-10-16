from django.apps import AppConfig


class InvoiceRequestFromClientConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invoice_request_from_client'
    def ready(self):
        import invoice_request_from_client.signals 



 # import your signals here
