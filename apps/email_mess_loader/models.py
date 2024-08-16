from django.db import models


class UserEmailAccount(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.email


class EmailMessage(models.Model):
    account = models.ForeignKey(UserEmailAccount, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sent_date = models.DateTimeField()
    received_date = models.DateTimeField()
    body = models.TextField()
    attachments = models.JSONField()  # Список прикрепленных файлов

    def __str__(self):
        return self.title
