from django.contrib import admin
from apps.jobs.models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'recruiter', 'status', 'location', 'employment_type', 'created_at')
    list_filter = ('status', 'employment_type', 'created_at')
    search_fields = ('title', 'description', 'location', 'recruiter__company_name', 'recruiter__full_name')
