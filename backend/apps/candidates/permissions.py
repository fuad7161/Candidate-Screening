from rest_framework import permissions

class IsApplicationOwnerOrJobOwner(permissions.BasePermission):
    """
    Object-level permission to allow:
    - Candidate who submitted the application
    - Recruiter who owns the job for this application
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # If user is candidate, check if candidate profile matches obj.candidate
        if user.role == 'candidate' and hasattr(user, 'candidate_profile'):
            if obj.candidate == user.candidate_profile:
                return True

        # If user is recruiter, check if recruiter profile matches obj.job.recruiter
        if user.role == 'recruiter' and hasattr(user, 'recruiter_profile'):
            if obj.job.recruiter == user.recruiter_profile:
                return True

        return False


class IsJobOwnerForApplication(permissions.BasePermission):
    """
    Permission check to ensure the recruiter owns the job related to the action/object.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == 'recruiter' and
            hasattr(request.user, 'recruiter_profile')
        )

    def has_object_permission(self, request, view, obj):
        # obj can be Job or Application
        job = getattr(obj, 'job', obj)
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'recruiter_profile') and
            job.recruiter == request.user.recruiter_profile
        )
