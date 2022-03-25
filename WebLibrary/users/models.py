from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    MAIN = 1
    MODERATOR = 2
    SUPER = 3

    ROLE_CHOICES = (
        ('main', 'Main'),
        ('moderator', 'Moderator'),
        ('super', 'Super'),
    )
    role = models.CharField(choices=ROLE_CHOICES, default='main', max_length=100)

    class Meta:
        # app_label = 'auth'
        db_table = 'auth_user'



