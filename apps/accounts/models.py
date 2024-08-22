from django.db import models

from apps.users.models import CustomUser


class UserEmailAccount(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
