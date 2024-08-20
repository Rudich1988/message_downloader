from django.db import models

from apps.accounts.models import UserEmailAccount


class EmailMessage(models.Model):
    account = models.ForeignKey(UserEmailAccount, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    received_date = models.DateTimeField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    attachments = models.JSONField()
