from rest_framework.permissions import BasePermission

class IsRecruiter(BasePermission):
    """
    Permission check for Recruiter role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == 'recruiter'
        )

class IsCandidate(BasePermission):
    """
    Permission check for Candidate role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == 'candidate'
        )
