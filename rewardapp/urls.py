from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'rewards', RewardViewSet, basename='rewards')
router.register(r'applications', RewardApplicationViewSet, basename='application')

urlpatterns = [
    path('', include(router.urls)),
    path('public-rewards/', PublicRewardListView.as_view(), name='public-reward-list'),
    path('review_application/<int:application_id>/', ReviewApplicationView.as_view(), name='review_application'),
    path('update_reward_status/<int:application_id>/', UpdateRewardStatusView.as_view(), name='update_reward_status'),
    path('rewardpay/<int:reward_id>/', RewardPayView.as_view(), name='pay_for_reward'),
]
