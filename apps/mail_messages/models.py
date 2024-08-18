from django.db import models

from apps.accounts.models import UserEmailAccount


class EmailMessage(models.Model):
    account = models.ForeignKey(UserEmailAccount, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sent_date = models.DateTimeField()
    received_date = models.DateTimeField()
    body = models.TextField()
    attachments = models.JSONField()

    def __str__(self):
        return self.title
