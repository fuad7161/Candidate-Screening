import logging
import uuid
from datetime import timedelta

from django.conf import settings
from minio import Minio

logger = logging.getLogger(__name__)


class MinIOStorage:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

    def _ensure_bucket_exists(self):
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            logger.info("Created MinIO bucket %s", self.bucket_name)

    def generate_presigned_upload_url(self, file_name, content_type='application/pdf'):
        extension = file_name.rsplit('.', 1)[-1].lower()
        object_name = f"resumes/{uuid.uuid4()}.{extension}"
        self._ensure_bucket_exists()
        url = self.client.presigned_put_object(
            self.bucket_name,
            object_name,
            expires=timedelta(seconds=settings.PRESIGNED_URL_EXPIRY_SECONDS),
        )
        return {
            'upload_url': url,
            'object_name': object_name,
            'expires_in': settings.PRESIGNED_URL_EXPIRY_SECONDS,
            'content_type': content_type,
        }

    def generate_presigned_download_url(self, object_name):
        return self.client.presigned_get_object(
            self.bucket_name,
            object_name,
            expires=timedelta(seconds=settings.PRESIGNED_URL_EXPIRY_SECONDS),
        )

    def upload_file(self, file_obj, object_name, content_type='application/pdf'):
        self._ensure_bucket_exists()
        file_obj.seek(0, 2)
        file_size = file_obj.tell()
        file_obj.seek(0)
        self.client.put_object(
            self.bucket_name,
            object_name,
            file_obj,
            file_size,
            content_type=content_type,
        )
        return self.get_file_url(object_name)

    def get_file_url(self, object_name):
        return f"{settings.MINIO_PUBLIC_URL}/{self.bucket_name}/{object_name}"

    def delete_file(self, object_name):
        self.client.remove_object(self.bucket_name, object_name)

    def file_exists(self, object_name):
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except Exception:
            return False
