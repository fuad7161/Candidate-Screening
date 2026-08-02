from django.contrib import admin
from apps.candidates.models import Application, CandidateProfile, FileUpload

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'user', 'created_at')
    search_fields = ('full_name', 'phone', 'user__email')


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'user', 'file_type', 'file_size', 'uploaded_at')
    list_filter = ('file_type', 'mime_type')
    search_fields = ('file_name', 'user__email', 'object_name')
    readonly_fields = ('id', 'uploaded_at')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'candidate', 'job', 'status', 'applied_at')
    list_filter = ('status',)
    search_fields = ('candidate__full_name', 'candidate__user__email', 'job__title')
