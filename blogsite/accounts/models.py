from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    birth_date = models.DateField(blank=True, null=True, verbose_name="生日")
