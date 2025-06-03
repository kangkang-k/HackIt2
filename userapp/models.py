from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    completed_tasks = models.IntegerField(default=0)
    bio = models.TextField(blank=True, null=True)
    code_age = models.IntegerField(default=0)
    balance = models.FloatField(default=0)

    groups = models.ManyToManyField(
        Group,
        related_name='HackUser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='HackUser_set',
        blank=True
    )

    class Meta:
        db_table = 'HackUser'
