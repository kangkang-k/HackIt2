from rest_framework import serializers
from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class RewardSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    creator_username = serializers.SerializerMethodField()
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), allow_null=True)

    class Meta:
        model = Reward
        fields = ['id', 'title', 'description', 'category', 'category_name', 'creator_username', 'reward_amount',
                  'created_at',
                  'updated_at', 'status']
        read_only_fields = ['creator', 'created_at', 'updated_at']

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_creator_username(self, obj):
        return obj.creator.username if obj.creator else None


class RewardApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardApplication
        fields = ['id', 'reward', 'applicant', 'application_date', 'is_accepted']
        read_only_fields = ['applicant', 'application_date', 'is_accepted']
