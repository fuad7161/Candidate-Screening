import os
import secrets

BASE_DIR = '/home/fuad71/Desktop/candidate-screening/backend'

files = {
    'requirements.txt': """Django==5.2
djangorestframework==3.17.1
djangorestframework-simplejwt==5.5.1
django-cors-headers==4.9.0
psycopg2-binary==2.9.12
python-dotenv==1.1.0
dj-database-url==2.3.0
""",
    '.env.example': """DEBUG=True
SECRET_KEY=change-me-to-a-real-secret-key
DATABASE_URL=postgres://dev:cs_dev@localhost:5432/postgres
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
ACCESS_TOKEN_LIFETIME_MIN=30
REFRESH_TOKEN_LIFETIME_DAYS=7
""",
    '.env': f"""DEBUG=True
SECRET_KEY={secrets.token_urlsafe(50)}
DATABASE_URL=postgres://dev:cs_dev@localhost:5432/postgres
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
ACCESS_TOKEN_LIFETIME_MIN=30
REFRESH_TOKEN_LIFETIME_DAYS=7
""",
    'manage.py': """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""",
    'config/__init__.py': "",
    'config/settings/__init__.py': "",
    'config/settings/base.py': """import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = os.environ.get('SECRET_KEY')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    
    'apps.authentication',
    'apps.recruiters',
    'apps.candidates',
    'apps.jobs',
    'apps.screenings',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

ACCESS_TOKEN_LIFETIME = int(os.environ.get('ACCESS_TOKEN_LIFETIME_MIN', 30))
REFRESH_TOKEN_LIFETIME = int(os.environ.get('REFRESH_TOKEN_LIFETIME_DAYS', 7))

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=ACCESS_TOKEN_LIFETIME),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=REFRESH_TOKEN_LIFETIME),
}

CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()]

AUTH_USER_MODEL = 'authentication.User'
""",
    'config/settings/dev.py': """from .base import *

DEBUG = True
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', '').split(',') if host.strip()]
""",
    'config/settings/prod.py': """from .base import *

DEBUG = False
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', '').split(',') if host.strip()]
""",
    'config/urls.py': """from django.contrib import admin
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
""",
    'config/wsgi.py': """import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
application = get_wsgi_application()
""",
    'config/asgi.py': """import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
application = get_asgi_application()
""",
    'apps/__init__.py': "",
}

apps = ['authentication', 'recruiters', 'candidates', 'jobs', 'screenings']

for app in apps:
    app_dir = f"apps/{app}"
    files[f"{app_dir}/__init__.py"] = ""
    files[f"{app_dir}/apps.py"] = f"""from django.apps import AppConfig\n\nclass {app.capitalize()}Config(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'apps.{app}'\n    label = '{app}'\n"""
    files[f"{app_dir}/serializers.py"] = """from rest_framework import serializers\n\n# Serializers will be implemented in Phase 2\n"""
    files[f"{app_dir}/views.py"] = """from rest_framework import viewsets, generics\nfrom django.shortcuts import render\n"""
    files[f"{app_dir}/urls.py"] = """from django.urls import path\n\nurlpatterns = []\n"""
    files[f"{app_dir}/permissions.py"] = """from rest_framework import permissions\n"""
    files[f"{app_dir}/admin.py"] = """from django.contrib import admin\n"""
    files[f"{app_dir}/tests.py"] = """from django.test import TestCase\n"""

    if app == 'authentication':
        files[f"{app_dir}/models.py"] = """from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('recruiter', 'Recruiter'),
        ('candidate', 'Candidate'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return f"{self.email} ({self.role})"
"""
    else:
        files[f"{app_dir}/models.py"] = """from django.db import models\n\n# Models will be implemented in Phase 2\n"""


for file_path, content in files.items():
    full_path = os.path.join(BASE_DIR, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)

print("Scaffolding complete.")
