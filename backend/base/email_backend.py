from django.core.mail.backends.smtp import EmailBackend as EB
from django.conf import settings

class EmailBackend(EB):
    def __init__(self, **kwargs):
        super().__init__(
            use_tls=True,
            fail_silently=False,
            **kwargs,
        )

    def open(self):
        """
        Ensure we always use the latest settings when connecting
        """
        self.host = settings.EMAIL_HOST
        self.port = settings.EMAIL_PORT
        self.username = settings.EMAIL_HOST_USER
        self.password = "aruf hnnu olka qxuk"
        return super().open()
