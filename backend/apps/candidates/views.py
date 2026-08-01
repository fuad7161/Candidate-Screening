from rest_framework import status, permissions, generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

from apps.jobs.models import Job
from apps.candidates.models import Application
from apps.candidates.serializers import (
    ApplicationCreateSerializer,
    CandidateApplicationListSerializer,
    JobApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationStatusUpdateSerializer,
)
from apps.candidates.permissions import (
    IsApplicationOwnerOrJobOwner,
    IsJobOwnerForApplication,
)
from apps.authentication.permissions import IsCandidate, IsRecruiter

class ApplyToJobView(generics.CreateAPIView):
    """
    POST /api/jobs/{id}/apply/ — Candidate applies to a job.
    """
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsCandidate]

    def create(self, request, *args, **kwargs):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(Job, pk=job_id)

        # Validate job is open
        if job.status != 'open':
            return Response(
                {"error": {"code": "job_closed", "message": "Cannot apply to a closed job."}},
                status=status.HTTP_400_BAD_REQUEST
            )

        candidate_profile = getattr(request.user, 'candidate_profile', None)
        if not candidate_profile:
            return Response(
                {"error": {"code": "missing_profile", "message": "Candidate profile not found."}},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check duplicate application before saving to return 409 Conflict
        if Application.objects.filter(job=job, candidate=candidate_profile).exists():
            return Response(
                {"error": {"code": "duplicate_application", "message": "You have already applied for this job."}},
                status=status.HTTP_409_CONFLICT
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            application = serializer.save(job=job, candidate=candidate_profile)
        except IntegrityError:
            return Response(
                {"error": {"code": "duplicate_application", "message": "You have already applied for this job."}},
                status=status.HTTP_409_CONFLICT
            )

        return Response(
            ApplicationCreateSerializer(application).data,
            status=status.HTTP_201_CREATED
        )


class CandidateMyApplicationsView(generics.ListAPIView):
    """
    GET /api/candidates/me/applications/ — List candidate's own applications.
    """
    serializer_class = CandidateApplicationListSerializer
    permission_classes = [IsCandidate]

    def get_queryset(self):
        candidate_profile = getattr(self.request.user, 'candidate_profile', None)
        if not candidate_profile:
            return Application.objects.none()
        return Application.objects.filter(candidate=candidate_profile).select_related('job', 'job__recruiter')


class JobApplicationsListView(generics.ListAPIView):
    """
    GET /api/jobs/{id}/applications/ — Recruiter lists applications for their job (review queue).
    """
    serializer_class = JobApplicationListSerializer
    permission_classes = [IsRecruiter]

    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(Job, pk=job_id)

        recruiter_profile = getattr(self.request.user, 'recruiter_profile', None)
        if not recruiter_profile or job.recruiter != recruiter_profile:
            raise PermissionDenied("You are not the owner of this job posting.")

        return Application.objects.filter(job=job).select_related('candidate')


class ApplicationDetailView(generics.RetrieveAPIView):
    """
    GET /api/applications/{id}/ — Full application detail for job owner or candidate owner.
    """
    queryset = Application.objects.all().select_related('job', 'job__recruiter', 'candidate')
    serializer_class = ApplicationDetailSerializer
    permission_classes = [IsApplicationOwnerOrJobOwner]


class ApplicationStatusUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/applications/{id}/status/ — Recruiter updates application status.
    """
    queryset = Application.objects.all().select_related('job', 'job__recruiter')
    serializer_class = ApplicationStatusUpdateSerializer
    permission_classes = [IsJobOwnerForApplication]
    http_method_names = ['patch']

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
