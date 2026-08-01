from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.recruiters.models import RecruiterProfile
from apps.candidates.models import CandidateProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserMeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'full_name', 'company_name', 'phone']

    def get_full_name(self, obj):
        if obj.role == 'recruiter' and hasattr(obj, 'recruiter_profile'):
            return obj.recruiter_profile.full_name
        elif obj.role == 'candidate' and hasattr(obj, 'candidate_profile'):
            return obj.candidate_profile.full_name
        return ""

    def get_company_name(self, obj):
        if obj.role == 'recruiter' and hasattr(obj, 'recruiter_profile'):
            return obj.recruiter_profile.company_name
        return None

    def get_phone(self, obj):
        if obj.role == 'candidate' and hasattr(obj, 'candidate_profile'):
            return obj.candidate_profile.phone
        return None


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    full_name = serializers.CharField(write_only=True, max_length=255)
    company_name = serializers.CharField(write_only=True, max_length=255, required=False, allow_blank=True)
    phone = serializers.CharField(write_only=True, max_length=50, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'role', 'full_name', 'company_name', 'phone']

    def validate(self, attrs):
        role = attrs.get('role')
        company_name = attrs.get('company_name')

        if role == 'recruiter' and not company_name:
            raise serializers.ValidationError({
                "company_name": ["Company name is required for recruiter registration."]
            })
        return attrs

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        company_name = validated_data.pop('company_name', '')
        phone = validated_data.pop('phone', '')

        # Set username to email as email is unique identifier
        email = validated_data['email']

        with transaction.atomic():
            user = User.objects.create_user(
                username=email,
                email=email,
                password=validated_data['password'],
                role=validated_data['role']
            )

            if user.role == 'recruiter':
                RecruiterProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    company_name=company_name
                )
            elif user.role == 'candidate':
                CandidateProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    phone=phone
                )

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        data = super().validate(attrs)
        user_serializer = UserMeSerializer(self.user)
        full_name = user_serializer.data.get('full_name', '')

        data['user'] = {
            'id': str(self.user.id),
            'role': self.user.role,
            'email': self.user.email,
            'full_name': full_name
        }
        return data
