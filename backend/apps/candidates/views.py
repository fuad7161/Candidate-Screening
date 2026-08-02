from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.conf import settings
import logging
import os
import uuid

from apps.jobs.models import Job
from apps.candidates.models import Application, FileUpload
from apps.candidates.services.storage_service import MinIOStorage
from apps.authentication.services.email_service import EmailService
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

logger = logging.getLogger(__name__)

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
        return Application.objects.filter(candidate=candidate_profile).select_related(
            'job', 'job__recruiter', 'resume_file'
        )


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

        return Application.objects.filter(job=job).select_related('candidate', 'resume_file')


class ApplicationDetailView(generics.RetrieveAPIView):
    """
    GET /api/applications/{id}/ — Full application detail for job owner or candidate owner.
    """
    queryset = Application.objects.all().select_related('job', 'job__recruiter', 'candidate', 'resume_file')
    serializer_class = ApplicationDetailSerializer
    permission_classes = [IsApplicationOwnerOrJobOwner]


class ApplicationStatusUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/applications/{id}/status/ — Recruiter updates application status.
    """
    queryset = Application.objects.all().select_related(
        'job', 'job__recruiter', 'candidate__user'
    )
    serializer_class = ApplicationStatusUpdateSerializer
    permission_classes = [IsJobOwnerForApplication]
    http_method_names = ['patch']

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_data = dict(serializer.data)
        response_data['email_notification_sent'] = getattr(instance, '_email_notification_sent', False)
        return Response(response_data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            EmailService.send_status_update_email(
                candidate_name=instance.candidate.full_name,
                candidate_email=instance.candidate.user.email,
                job_title=instance.job.title,
                new_status=instance.status,
            )
            instance._email_notification_sent = True
        except Exception:
            instance._email_notification_sent = False
            logger.exception("Failed to send status update email for application %s", instance.pk)


class GetUploadTokenView(APIView):
    permission_classes = [IsCandidate]

    def get(self, request):
        file_name = os.path.basename(request.query_params.get('file_name', 'resume.pdf'))
        file_ext = os.path.splitext(file_name)[1].lower()
        if file_ext not in settings.ALLOWED_RESUME_EXTENSIONS:
            return Response(
                {"error": {"code": "invalid_file_type", "message": "Only PDF, DOC, and DOCX files are allowed."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }
        try:
            upload_data = MinIOStorage().generate_presigned_upload_url(
                file_name,
                content_type=mime_types[file_ext],
            )
        except Exception:
            logger.exception("Failed to generate a MinIO upload URL")
            return Response(
                {"error": {"code": "storage_unavailable", "message": "File storage is unavailable."}},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(upload_data)


class UploadResumeView(APIView):
    permission_classes = [IsCandidate]

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                {"error": {"code": "missing_file", "message": "No file was provided."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        safe_name = os.path.basename(file_obj.name)
        file_ext = os.path.splitext(safe_name)[1].lower()
        if file_ext not in settings.ALLOWED_RESUME_EXTENSIONS:
            return Response(
                {"error": {"code": "invalid_file_type", "message": "Only PDF, DOC, and DOCX files are allowed."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if file_obj.content_type not in settings.ALLOWED_RESUME_MIME_TYPES:
            return Response(
                {"error": {"code": "invalid_mime_type", "message": "The uploaded file type does not match an allowed resume format."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if file_obj.size > settings.MAX_RESUME_SIZE:
            return Response(
                {"error": {"code": "file_too_large", "message": "Resume size cannot exceed 5 MB."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        object_name = f"resumes/{request.user.id}/{uuid.uuid4()}{file_ext}"
        storage = MinIOStorage()
        try:
            file_url = storage.upload_file(file_obj, object_name, file_obj.content_type)
        except Exception:
            logger.exception("Failed to upload resume for user %s", request.user.pk)
            return Response(
                {"error": {"code": "upload_failed", "message": "Could not upload the resume. Please try again."}},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        upload = FileUpload.objects.create(
            user=request.user,
            file_type='resume',
            object_name=object_name,
            file_url=file_url,
            file_name=safe_name,
            file_size=file_obj.size,
            mime_type=file_obj.content_type,
        )
        return Response(
            {
                'id': str(upload.id),
                'file_url': storage.generate_presigned_download_url(object_name),
                'file_name': upload.file_name,
                'file_size': upload.file_size,
            },
            status=status.HTTP_201_CREATED,
        )
