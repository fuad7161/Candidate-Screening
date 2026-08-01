from django.contrib import admin
from apps.recruiters.models import RecruiterProfile

@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'company_name', 'user', 'created_at')
    search_fields = ('full_name', 'company_name', 'user__email')
