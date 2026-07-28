from django.conf import settings
from django.db import models

from applications.models import Application


class Message(models.Model):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sent_at"]

    def __str__(self):
        return f"{self.sender} @ {self.sent_at:%Y-%m-%d %H:%M}"
