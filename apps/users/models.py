from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.get_full_name()
