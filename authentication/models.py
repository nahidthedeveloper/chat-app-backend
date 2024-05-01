from django.contrib.auth.models import AbstractUser
from django.db import models

from authentication.manager import AccountManager


class Account(AbstractUser):
    username = None
    email = models.EmailField(max_length=100, unique=True)
    profile_picture = models.FileField(upload_to='profile_pictures')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = AccountManager()

    def __str__(self):
        return self.email


class UserSignupEmailSenderModel(models.Model):
    uid = models.CharField(max_length=55)
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=1000)

    def __str__(self):
        return self.token
