from rest_framework import serializers
from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['id', 'title', 'description', 'category', 'creator', 'reward_amount', 'created_at', 'updated_at',
                  'status']
        read_only_fields = ['creator', 'created_at', 'updated_at']


class RewardApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardApplication
        fields = ['id', 'reward', 'applicant', 'application_date', 'is_accepted']
        read_only_fields = ['applicant', 'application_date', 'is_accepted']
