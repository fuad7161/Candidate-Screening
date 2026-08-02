from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.recruiters.models import RecruiterProfile
from apps.candidates.models import CandidateProfile, Application, FileUpload
from apps.jobs.models import Job

User = get_user_model()

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ApplicationAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Recruiter 1 (Job 1 & Job 2 owner)
        self.recruiter_user_1 = User.objects.create_user(
            username='recruiter1@acme.com',
            email='recruiter1@acme.com',
            password='Password123!',
            role='recruiter'
        )
        self.recruiter_profile_1 = RecruiterProfile.objects.create(
            user=self.recruiter_user_1,
            full_name='Alice Recruiter',
            company_name='Acme Corp'
        )

        # Recruiter 2
        self.recruiter_user_2 = User.objects.create_user(
            username='recruiter2@beta.com',
            email='recruiter2@beta.com',
            password='Password123!',
            role='recruiter'
        )
        self.recruiter_profile_2 = RecruiterProfile.objects.create(
            user=self.recruiter_user_2,
            full_name='Bob Recruiter',
            company_name='Beta Inc'
        )

        # Candidate 1
        self.candidate_user_1 = User.objects.create_user(
            username='candidate1@gmail.com',
            email='candidate1@gmail.com',
            password='Password123!',
            role='candidate'
        )
        self.candidate_profile_1 = CandidateProfile.objects.create(
            user=self.candidate_user_1,
            full_name='Charlie Candidate'
        )

        # Candidate 2
        self.candidate_user_2 = User.objects.create_user(
            username='candidate2@gmail.com',
            email='candidate2@gmail.com',
            password='Password123!',
            role='candidate'
        )
        self.candidate_profile_2 = CandidateProfile.objects.create(
            user=self.candidate_user_2,
            full_name='David Candidate'
        )

        # Jobs
        self.open_job = Job.objects.create(
            recruiter=self.recruiter_profile_1,
            title='Backend Engineer',
            description='Django + DRF experience required.',
            location='Remote',
            employment_type='full_time',
            status='open'
        )
        self.closed_job = Job.objects.create(
            recruiter=self.recruiter_profile_1,
            title='Frontend Lead',
            description='React experience required.',
            location='New York, NY',
            employment_type='full_time',
            status='closed'
        )

    def test_apply_to_open_job_success(self):
        self.client.force_authenticate(user=self.candidate_user_1)
        payload = {
            "resume_url": "https://example.com/resume.pdf",
            "cover_note": "Interested in backend role."
        }
        response = self.client.post(f'/api/jobs/{self.open_job.id}/apply/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "applied")
        self.assertEqual(response.data["resume_url"], "https://example.com/resume.pdf")

    def test_apply_to_closed_job_fails(self):
        self.client.force_authenticate(user=self.candidate_user_1)
        payload = {
            "resume_url": "https://example.com/resume.pdf"
        }
        response = self.client.post(f'/api/jobs/{self.closed_job.id}/apply/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_apply_duplicate_fails_conflict(self):
        # First application
        Application.objects.create(
            job=self.open_job,
            candidate=self.candidate_profile_1,
            resume_url="https://example.com/resume.pdf"
        )

        # Second application attempt
        self.client.force_authenticate(user=self.candidate_user_1)
        payload = {
            "resume_url": "https://example.com/resume.pdf"
        }
        response = self.client.post(f'/api/jobs/{self.open_job.id}/apply/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_apply_by_recruiter_forbidden(self):
        self.client.force_authenticate(user=self.recruiter_user_1)
        payload = {
            "resume_url": "https://example.com/resume.pdf"
        }
        response = self.client.post(f'/api/jobs/{self.open_job.id}/apply/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_candidate_my_applications_list(self):
        app = Application.objects.create(
            job=self.open_job,
            candidate=self.candidate_profile_1,
            resume_url="https://example.com/resume.pdf"
        )
        self.client.force_authenticate(user=self.candidate_user_1)
        response = self.client.get('/api/candidates/me/applications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["job_title"], self.open_job.title)

    def test_recruiter_job_applications_list_owner_only(self):
        app = Application.objects.create(
            job=self.open_job,
            candidate=self.candidate_profile_1,
            resume_url="https://example.com/resume.pdf"
        )
        # Owner recruiter gets applications
        self.client.force_authenticate(user=self.recruiter_user_1)
        response = self.client.get(f'/api/jobs/{self.open_job.id}/applications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["candidate_name"], self.candidate_profile_1.full_name)

        # Non-owner recruiter getting applications forbidden
        self.client.force_authenticate(user=self.recruiter_user_2)
        response = self.client.get(f'/api/jobs/{self.open_job.id}/applications/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_application_detail_access_permissions(self):
        app = Application.objects.create(
            job=self.open_job,
            candidate=self.candidate_profile_1,
            resume_url="https://example.com/resume.pdf"
        )

        # Candidate owner can view
        self.client.force_authenticate(user=self.candidate_user_1)
        response = self.client.get(f'/api/applications/{app.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Job owner recruiter can view
        self.client.force_authenticate(user=self.recruiter_user_1)
        response = self.client.get(f'/api/applications/{app.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Unrelated candidate forbidden
        self.client.force_authenticate(user=self.candidate_user_2)
        response = self.client.get(f'/api/applications/{app.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Unrelated recruiter forbidden
        self.client.force_authenticate(user=self.recruiter_user_2)
        response = self.client.get(f'/api/applications/{app.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_application_status_update_valid_and_invalid_transitions(self):
        app = Application.objects.create(
            job=self.open_job,
            candidate=self.candidate_profile_1,
            status='applied',
            resume_url="https://example.com/resume.pdf"
        )

        self.client.force_authenticate(user=self.recruiter_user_1)

        # Valid transition: applied -> shortlisted
        response = self.client.patch(f'/api/applications/{app.id}/status/', {"status": "shortlisted"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "shortlisted")

        # Invalid transition: shortlisted -> hired (must go through interview)
        response = self.client.patch(f'/api/applications/{app.id}/status/', {"status": "hired"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid transition: shortlisted -> interview
        response = self.client.patch(f'/api/applications/{app.id}/status/', {"status": "interview"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Valid transition: interview -> hired
        response = self.client.patch(f'/api/applications/{app.id}/status/', {"status": "hired"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.candidates.views.EmailService.send_status_update_email')
    def test_status_update_sends_email_without_blocking_response(self, send_email):
        app = Application.objects.create(
            job=self.open_job,
            candidate=self.candidate_profile_1,
            resume_url='https://example.com/resume.pdf',
        )
        self.client.force_authenticate(user=self.recruiter_user_1)

        response = self.client.patch(
            f'/api/applications/{app.id}/status/',
            {'status': 'shortlisted'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['email_notification_sent'])
        send_email.assert_called_once_with(
            candidate_name=self.candidate_profile_1.full_name,
            candidate_email=self.candidate_user_1.email,
            job_title=self.open_job.title,
            new_status='shortlisted',
        )

    @patch('apps.candidates.views.MinIOStorage')
    def test_direct_resume_upload_and_application(self, storage_class):
        storage = storage_class.return_value
        storage.upload_file.return_value = 'http://localhost:9000/bucket/resume.pdf'
        storage.generate_presigned_download_url.return_value = 'http://signed.example/resume.pdf'
        resume = SimpleUploadedFile(
            'resume.pdf', b'%PDF-1.4 test resume', content_type='application/pdf'
        )
        self.client.force_authenticate(user=self.candidate_user_1)

        upload_response = self.client.post('/api/upload-resume/', {'file': resume}, format='multipart')

        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        upload = FileUpload.objects.get(pk=upload_response.data['id'])
        self.assertEqual(upload.user, self.candidate_user_1)

        with patch(
            'apps.candidates.serializers.MinIOStorage.generate_presigned_download_url',
            return_value='http://signed.example/resume.pdf',
        ):
            apply_response = self.client.post(
                f'/api/jobs/{self.open_job.id}/apply/',
                {'resume_file': str(upload.id), 'cover_note': 'My note'},
                format='json',
            )
        self.assertEqual(apply_response.status_code, status.HTTP_201_CREATED)
        application = Application.objects.get(pk=apply_response.data['id'])
        self.assertEqual(application.resume_file, upload)

    @patch('apps.candidates.views.MinIOStorage')
    def test_resume_upload_rejects_invalid_extension(self, storage_class):
        self.client.force_authenticate(user=self.candidate_user_1)
        resume = SimpleUploadedFile('resume.exe', b'bad', content_type='application/octet-stream')

        response = self.client.post('/api/upload-resume/', {'file': resume}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        storage_class.assert_not_called()

    def test_candidate_cannot_apply_with_another_users_upload(self):
        upload = FileUpload.objects.create(
            user=self.candidate_user_2,
            file_type='resume',
            object_name='resumes/other.pdf',
            file_url='http://localhost:9000/bucket/other.pdf',
            file_name='other.pdf',
            file_size=100,
            mime_type='application/pdf',
        )
        self.client.force_authenticate(user=self.candidate_user_1)

        response = self.client.post(
            f'/api/jobs/{self.open_job.id}/apply/',
            {'resume_file': str(upload.id)},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
