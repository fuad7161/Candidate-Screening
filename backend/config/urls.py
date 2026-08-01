from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'Backend is running'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/', include('apps.jobs.urls')),
    path('api/', include('apps.screenings.urls')),
    path('api/', include('apps.recruiters.urls')),
    path('api/', include('apps.candidates.urls')),
    path('api/health/', health_check, name='health-check'),
]
