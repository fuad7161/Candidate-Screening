from rest_framework import serializers
from apps.jobs.models import Job
from apps.recruiters.models import RecruiterProfile

class RecruiterSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruiterProfile
        fields = ['id', 'full_name', 'company_name']


class JobListSerializer(serializers.ModelSerializer):
    recruiter = RecruiterSummarySerializer(read_only=True)
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'location',
            'employment_type',
            'status',
            'created_at',
            'updated_at',
            'recruiter',
            'applications_count',
        ]

    def get_applications_count(self, obj):
        if hasattr(obj, 'applications'):
            return obj.applications.count()
        return 0


class JobDetailSerializer(serializers.ModelSerializer):
    recruiter = RecruiterSummarySerializer(read_only=True)
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'description',
            'location',
            'employment_type',
            'status',
            'created_at',
            'updated_at',
            'recruiter',
            'applications_count',
        ]

    def get_applications_count(self, obj):
        if hasattr(obj, 'applications'):
            return obj.applications.count()
        return 0


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, max_length=255)
    description = serializers.CharField(required=True)

    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'description',
            'location',
            'employment_type',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Job title cannot be empty.")
        return value.strip()

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError("Job description cannot be empty.")
        return value.strip()
