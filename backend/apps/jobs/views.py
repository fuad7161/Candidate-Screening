from rest_framework import status, permissions, generics, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.jobs.models import Job
from apps.jobs.serializers import (
    JobListSerializer,
    JobDetailSerializer,
    JobCreateUpdateSerializer
)
from apps.jobs.permissions import IsJobOwner
from apps.authentication.permissions import IsRecruiter

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return JobCreateUpdateSerializer
        return JobDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            permission_classes = [IsRecruiter]
        elif self.action in ['update', 'partial_update', 'destroy', 'close']:
            permission_classes = [IsJobOwner]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = Job.objects.all()
        user = self.request.user
        mine = self.request.query_params.get('mine', '').lower() in ('true', '1')
        status_param = self.request.query_params.get('status')

        # Recruiter requesting their own jobs
        if mine and user.is_authenticated and getattr(user, 'role', None) == 'recruiter' and hasattr(user, 'recruiter_profile'):
            qs = qs.filter(recruiter=user.recruiter_profile)
            if status_param in ['open', 'closed']:
                qs = qs.filter(status=status_param)
            return qs

        # Filtering by status if provided
        if status_param in ['open', 'closed']:
            qs = qs.filter(status=status_param)
        else:
            # Default for public/candidates: only open jobs
            if not (user.is_authenticated and getattr(user, 'role', None) == 'recruiter'):
                qs = qs.filter(status='open')

        return qs

    def perform_create(self, serializer):
        recruiter_profile = self.request.user.recruiter_profile
        serializer.save(recruiter=recruiter_profile, status='open')

    @action(detail=True, methods=['patch'], permission_classes=[IsJobOwner], url_path='close')
    def close(self, request, pk=None):
        job = self.get_object()
        job.status = 'closed'
        job.save()
        serializer = JobDetailSerializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)
