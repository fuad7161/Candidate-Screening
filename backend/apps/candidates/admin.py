from django.contrib import admin
from apps.candidates.models import CandidateProfile

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'user', 'created_at')
    search_fields = ('full_name', 'phone', 'user__email')
