from rest_framework import permissions

class IsJobOwner(permissions.BasePermission):
    """
    Object-level permission to allow only the owner of a job (the recruiter who created it)
    to edit or close it.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == 'recruiter' and
            hasattr(request.user, 'recruiter_profile')
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'recruiter_profile') and
            obj.recruiter == request.user.recruiter_profile
        )
