from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.jobs.views import JobViewSet

router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='job')

urlpatterns = [
    path('', include(router.urls)),
]
