from rest_framework import serializers
from apps.candidates.models import Application, FileUpload
from apps.candidates.services.storage_service import MinIOStorage
from apps.jobs.models import Job

class ApplicationCreateSerializer(serializers.ModelSerializer):
    resume_url = serializers.URLField(required=False, max_length=500)
    resume_file = serializers.PrimaryKeyRelatedField(
        queryset=FileUpload.objects.filter(file_type='resume'),
        required=False,
        allow_null=True,
        write_only=True,
    )
    cover_note = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Application
        fields = ['id', 'job', 'status', 'resume_url', 'resume_file', 'cover_note', 'applied_at']
        read_only_fields = ['id', 'job', 'status', 'applied_at']

    def validate_resume_url(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("resume_url is required.")
        return value.strip()

    def validate(self, attrs):
        resume_file = attrs.get('resume_file')
        resume_url = attrs.get('resume_url')
        if not resume_file and not resume_url:
            raise serializers.ValidationError({'resume_file': ['A resume upload is required.']})
        request = self.context.get('request')
        if resume_file and request and resume_file.user_id != request.user.id:
            raise serializers.ValidationError({'resume_file': ['You may only use your own upload.']})
        if resume_file:
            attrs['resume_url'] = resume_file.file_url
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['resume_url'] = current_resume_url(instance)
        data['resume_file_id'] = str(instance.resume_file_id) if instance.resume_file_id else None
        return data


def current_resume_url(application):
    if application.resume_file_id:
        return MinIOStorage().generate_presigned_download_url(
            application.resume_file.object_name,
        )
    return application.resume_url


class CandidateApplicationListSerializer(serializers.ModelSerializer):
    job = serializers.IntegerField(source='job.id', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.recruiter.company_name', read_only=True)
    cover_letter = serializers.CharField(source='cover_note', read_only=True)
    resume_url = serializers.SerializerMethodField()

    def get_resume_url(self, obj):
        return current_resume_url(obj)

    class Meta:
        model = Application
        fields = ['id', 'job', 'job_title', 'company_name', 'cover_letter', 'resume_url', 'status', 'applied_at']


class JobApplicationListSerializer(serializers.ModelSerializer):
    candidate_id = serializers.IntegerField(source='candidate.id', read_only=True)
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    resume_url = serializers.SerializerMethodField()

    def get_resume_url(self, obj):
        return current_resume_url(obj)

    class Meta:
        model = Application
        fields = ['id', 'candidate_id', 'candidate_name', 'resume_url', 'cover_note', 'status', 'applied_at']


class ApplicationDetailSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField(source='job.id', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    candidate_id = serializers.IntegerField(source='candidate.id', read_only=True)
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    company_name = serializers.CharField(source='job.recruiter.company_name', read_only=True)
    resume_url = serializers.SerializerMethodField()

    def get_resume_url(self, obj):
        return current_resume_url(obj)

    class Meta:
        model = Application
        fields = [
            'id',
            'job_id',
            'job_title',
            'company_name',
            'candidate_id',
            'candidate_name',
            'resume_url',
            'cover_note',
            'status',
            'applied_at',
            'updated_at'
        ]


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Application.STATUS_CHOICES)

    class Meta:
        model = Application
        fields = ['id', 'status']

    def validate_status(self, new_status):
        instance = self.instance
        current_status = instance.status

        if current_status == new_status:
            return new_status

        # Valid transitions:
        # applied -> shortlisted, rejected
        # shortlisted -> interview, rejected
        # interview -> hired, rejected
        # Any state can transition to rejected
        # Otherwise, invalid transition
        valid_transitions = {
            'applied': ['shortlisted', 'rejected'],
            'shortlisted': ['interview', 'rejected'],
            'interview': ['hired', 'rejected'],
            'rejected': [],
            'hired': []
        }

        allowed_next = valid_transitions.get(current_status, [])
        if new_status not in allowed_next:
            raise serializers.ValidationError(
                f"Cannot transition application status from '{current_status}' to '{new_status}'."
            )
        return new_status
