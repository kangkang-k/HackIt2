from django.db import transaction
from rest_framework import serializers, status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RewardSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.permissions import AllowAny
from .models import Category
from .serializers import CategorySerializer
from .permissions import IsSuperUser
from rest_framework import viewsets
from .models import RewardApplication, Reward
from .serializers import RewardApplicationSerializer
from .permissions import IsApplicantOrReadOnly
from rest_framework.permissions import IsAuthenticated


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperUser]


class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        return Reward.objects.filter(creator=self.request.user)


class PublicRewardListView(generics.ListAPIView):
    queryset = Reward.objects.filter(status='waiting')
    serializer_class = RewardSerializer
    permission_classes = [AllowAny]


class RewardApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = RewardApplicationSerializer
    permission_classes = [IsAuthenticated, IsApplicantOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return RewardApplication.objects.all()
        return RewardApplication.objects.filter(applicant=self.request.user)

    def perform_create(self, serializer):
        reward = serializer.validated_data['reward']
        if reward.creator == self.request.user or reward.status != 'waiting':
            raise serializers.ValidationError(
                "You cannot apply for this reward. Either it belongs to you or its status is not 'waiting'.")

        serializer.save(applicant=self.request.user)

        reward.receiver = self.request.user
        reward.status = 'applied'
        reward.save()

    def destroy(self, request, *args, **kwargs):
        application = self.get_object()
        reward = application.reward

        if application.is_accepted:
            raise serializers.ValidationError("Cannot delete an accepted application.")

        response = super().destroy(request, *args, **kwargs)

        if not reward.applications.exists():
            reward.receiver = None
            reward.status = 'waiting'
            reward.save()

        return response

    def update(self, request, *args, **kwargs):
        raise serializers.ValidationError("Modification of applications is not allowed.")

    def partial_update(self, request, *args, **kwargs):
        raise serializers.ValidationError("Modification of applications is not allowed.")


class ReviewApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, application_id):
        try:
            application = RewardApplication.objects.get(pk=application_id)
        except RewardApplication.DoesNotExist:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser and application.reward.creator != request.user:
            return Response({"detail": "You do not have permission to review this application."},
                            status=status.HTTP_403_FORBIDDEN)

        is_accepted = request.data.get('is_accepted')
        if is_accepted == "reject":
            application.reward.status = 'waiting'
            application.reward.save()
            return Response({"detail": "已拒绝申请"}, status=status.HTTP_200_OK)
        elif is_accepted == "accept":
            application.is_accepted = True
            application.save()

            application.reward.status = 'in_progress'
            application.reward.save()

            return Response({"detail": "已通过审核"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "不支持的参数"}, status=status.HTTP_404_NOT_FOUND)


class UpdateRewardStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, application_id):
        try:
            application = RewardApplication.objects.get(pk=application_id)
        except RewardApplication.DoesNotExist:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

        if application.applicant != request.user:
            return Response({"detail": "You do not have permission to update this reward."},
                            status=status.HTTP_403_FORBIDDEN)

        if not application.is_accepted:
            return Response({"detail": "This application has not been accepted."}, status=status.HTTP_400_BAD_REQUEST)

        application.reward.status = 'completed'
        application.reward.save()

        return Response({"detail": "Reward status updated to completed successfully."}, status=status.HTTP_200_OK)


class RewardPayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reward_id):
        try:
            reward = Reward.objects.get(pk=reward_id)
        except Reward.DoesNotExist:
            return Response({"detail": "悬赏未找到"}, status=status.HTTP_404_NOT_FOUND)

        if reward.creator != request.user:
            return Response({"detail": "此悬赏无审批权限"}, status=status.HTTP_403_FORBIDDEN)

        if reward.status != 'completed':
            return Response({"detail": "只允许审批已完成的悬赏"}, status=status.HTTP_400_BAD_REQUEST)

        new_status = request.data.get('status')
        if new_status not in ['payed', 'callback']:
            return Response({"detail": "参数错误"}, status=status.HTTP_400_BAD_REQUEST)

        if reward.creator.balance < reward.reward_amount:
            return Response({"detail": "余额不足，无法支付悬赏金额"}, status=status.HTTP_400_BAD_REQUEST)

        receiver = reward.receiver
        receiver.balance += float(reward.reward_amount)
        receiver.save()

        reward.creator.balance -= float(reward.reward_amount)
        reward.creator.save()

        reward.status = new_status
        reward.save()

        return Response({"detail": f"审批成功： {new_status} "}, status=status.HTTP_200_OK)
