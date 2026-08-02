from django.urls import path
from apps.candidates.views import (
    ApplyToJobView,
    CandidateMyApplicationsView,
    JobApplicationsListView,
    ApplicationDetailView,
    ApplicationStatusUpdateView,
    GetUploadTokenView,
    UploadResumeView,
)

urlpatterns = [
    path('jobs/<int:job_id>/apply/', ApplyToJobView.as_view(), name='job-apply'),
    path('candidates/me/applications/', CandidateMyApplicationsView.as_view(), name='candidate-my-applications'),
    path('jobs/<int:job_id>/applications/', JobApplicationsListView.as_view(), name='job-applications-list'),
    path('applications/<int:pk>/', ApplicationDetailView.as_view(), name='application-detail'),
    path('applications/<int:pk>/status/', ApplicationStatusUpdateView.as_view(), name='application-status-update'),
    path('upload-token/', GetUploadTokenView.as_view(), name='upload-token'),
    path('upload-resume/', UploadResumeView.as_view(), name='upload-resume'),
]
