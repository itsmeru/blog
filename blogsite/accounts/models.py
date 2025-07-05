from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    birth_date = models.DateField(blank=True, null=True, verbose_name="生日")
    REQUIRED_FIELDS = ['email', 'first_name']
    def __str__(self):
        return self.username