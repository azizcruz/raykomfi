from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField


class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    country = CountryField()
    isBlocked = models.BooleanField(default=False)
