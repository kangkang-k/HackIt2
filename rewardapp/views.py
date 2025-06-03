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

        reward.status = 'applied'
        reward.save()

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
            return Response({"detail": "You do not have permission to update this reward."}, status=status.HTTP_403_FORBIDDEN)

        if not application.is_accepted:
            return Response({"detail": "This application has not been accepted."}, status=status.HTTP_400_BAD_REQUEST)

        application.reward.status = 'completed'
        application.reward.save()

        return Response({"detail": "Reward status updated to completed successfully."}, status=status.HTTP_200_OK)