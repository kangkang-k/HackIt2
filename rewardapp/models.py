from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Category'


class Reward(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),  # 已被接单
        ('waiting', 'Waiting'),  # 挂单中
        ('in_progress', 'In Progress'),  # 开发中
        ('completed', 'Completed'),  # 开发完成
        ('payed', 'Payed'),  # 已结款
        ('cancelled', 'Cancelled'),  # 已取消
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='rewards')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_rewards')
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Reward'


class RewardApplication(models.Model):
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    application_date = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.applicant.username} - {self.reward.title}"

    class Meta:
        db_table = 'RewardApplication'


