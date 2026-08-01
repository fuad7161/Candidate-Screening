from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.recruiters.models import RecruiterProfile
from apps.candidates.models import CandidateProfile
from apps.jobs.models import Job

User = get_user_model()

class JobAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Recruiter 1
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

        # Candidate
        self.candidate_user = User.objects.create_user(
            username='candidate@gmail.com',
            email='candidate@gmail.com',
            password='Password123!',
            role='candidate'
        )
        self.candidate_profile = CandidateProfile.objects.create(
            user=self.candidate_user,
            full_name='Charlie Candidate'
        )

        # Pre-populate jobs
        self.open_job_1 = Job.objects.create(
            recruiter=self.recruiter_profile_1,
            title='Backend Engineer',
            description='Django + DRF experience required.',
            location='Remote',
            employment_type='full_time',
            status='open'
        )
        self.closed_job_1 = Job.objects.create(
            recruiter=self.recruiter_profile_1,
            title='Frontend Lead',
            description='React experience required.',
            location='New York, NY',
            employment_type='full_time',
            status='closed'
        )
        self.open_job_2 = Job.objects.create(
            recruiter=self.recruiter_profile_2,
            title='DevOps Engineer',
            description='AWS + Docker required.',
            location='Remote',
            employment_type='contract',
            status='open'
        )

    def test_public_job_list_returns_only_open_jobs(self):
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        
        # Candidate/public sees open_job_1 and open_job_2, but not closed_job_1
        job_ids = [j['id'] for j in results]
        self.assertIn(self.open_job_1.id, job_ids)
        self.assertIn(self.open_job_2.id, job_ids)
        self.assertNotIn(self.closed_job_1.id, job_ids)

    def test_recruiter_mine_filter_returns_only_own_jobs(self):
        self.client.force_authenticate(user=self.recruiter_user_1)
        response = self.client.get('/api/jobs/?mine=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        
        job_ids = [j['id'] for j in results]
        self.assertIn(self.open_job_1.id, job_ids)
        self.assertIn(self.closed_job_1.id, job_ids)
        self.assertNotIn(self.open_job_2.id, job_ids)

    def test_create_job_by_recruiter(self):
        self.client.force_authenticate(user=self.recruiter_user_1)
        payload = {
            "title": "Full Stack Developer",
            "description": "Building cool products with Python and React.",
            "location": "San Francisco, CA",
            "employment_type": "full_time"
        }
        response = self.client.post('/api/jobs/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Full Stack Developer")
        self.assertEqual(response.data["status"], "open")

    def test_create_job_by_candidate_forbidden(self):
        self.client.force_authenticate(user=self.candidate_user)
        payload = {
            "title": "Hacker Job",
            "description": "Should fail",
            "location": "Nowhere"
        }
        response = self.client.post('/api/jobs/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_job_by_owner_success(self):
        self.client.force_authenticate(user=self.recruiter_user_1)
        payload = {
            "title": "Senior Backend Engineer",
            "description": "Updated description with Django & FastAPI.",
            "location": "Remote",
            "employment_type": "full_time"
        }
        response = self.client.put(f'/api/jobs/{self.open_job_1.id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Senior Backend Engineer")

    def test_edit_job_by_non_owner_recruiter_forbidden(self):
        # Recruiter 2 trying to edit Recruiter 1's job
        self.client.force_authenticate(user=self.recruiter_user_2)
        payload = {
            "title": "Malicious Update",
            "description": "Trying to edit someone else's job.",
            "location": "Remote"
        }
        response = self.client.put(f'/api/jobs/{self.open_job_1.id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_close_job_by_owner_success(self):
        self.client.force_authenticate(user=self.recruiter_user_1)
        response = self.client.patch(f'/api/jobs/{self.open_job_1.id}/close/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "closed")

        # Verify DB updated
        self.open_job_1.refresh_from_db()
        self.assertEqual(self.open_job_1.status, "closed")

    def test_close_job_by_candidate_forbidden(self):
        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.patch(f'/api/jobs/{self.open_job_1.id}/close/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
