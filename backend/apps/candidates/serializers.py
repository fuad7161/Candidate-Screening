from rest_framework import serializers
from apps.candidates.models import Application
from apps.jobs.models import Job

class ApplicationCreateSerializer(serializers.ModelSerializer):
    resume_url = serializers.URLField(required=True, max_length=500)
    cover_note = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Application
        fields = ['id', 'job', 'status', 'resume_url', 'cover_note', 'applied_at']
        read_only_fields = ['id', 'job', 'status', 'applied_at']

    def validate_resume_url(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("resume_url is required.")
        return value.strip()


class CandidateApplicationListSerializer(serializers.ModelSerializer):
    job = serializers.IntegerField(source='job.id', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.recruiter.company_name', read_only=True)
    cover_letter = serializers.CharField(source='cover_note', read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'job', 'job_title', 'company_name', 'cover_letter', 'resume_url', 'status', 'applied_at']


class JobApplicationListSerializer(serializers.ModelSerializer):
    candidate_id = serializers.IntegerField(source='candidate.id', read_only=True)
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'candidate_id', 'candidate_name', 'resume_url', 'cover_note', 'status', 'applied_at']


class ApplicationDetailSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField(source='job.id', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    candidate_id = serializers.IntegerField(source='candidate.id', read_only=True)
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    company_name = serializers.CharField(source='job.recruiter.company_name', read_only=True)

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
