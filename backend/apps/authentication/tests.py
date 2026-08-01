from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class AuthAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.refresh_url = '/api/auth/refresh/'
        self.me_url = '/api/auth/me/'

    def test_register_recruiter_success(self):
        payload = {
            "email": "recruiter@example.com",
            "password": "Password123!",
            "role": "recruiter",
            "full_name": "Jane Recruiter",
            "company_name": "Acme Corp"
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["email"], "recruiter@example.com")
        self.assertEqual(response.data["role"], "recruiter")

        # Verify profile created
        user = User.objects.get(email="recruiter@example.com")
        self.assertEqual(user.recruiter_profile.company_name, "Acme Corp")

    def test_register_recruiter_missing_company(self):
        payload = {
            "email": "recruiter2@example.com",
            "password": "Password123!",
            "role": "recruiter",
            "full_name": "Jane Recruiter"
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_candidate_success(self):
        payload = {
            "email": "candidate@example.com",
            "password": "Password123!",
            "role": "candidate",
            "full_name": "John Candidate",
            "phone": "+1234567890"
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], "candidate")

        user = User.objects.get(email="candidate@example.com")
        self.assertEqual(user.candidate_profile.phone, "+1234567890")

    def test_login_and_me(self):
        # Register candidate first
        reg_payload = {
            "email": "login_test@example.com",
            "password": "Password123!",
            "role": "candidate",
            "full_name": "Login Test User"
        }
        self.client.post(self.register_url, reg_payload, format='json')

        # Login
        login_payload = {
            "email": "login_test@example.com",
            "password": "Password123!"
        }
        login_resp = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_resp.data)
        self.assertIn("refresh", login_resp.data)
        self.assertEqual(login_resp.data["user"]["full_name"], "Login Test User")

        access_token = login_resp.data["access"]

        # Access /me with token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        me_resp = self.client.get(self.me_url)
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(me_resp.data["email"], "login_test@example.com")
        self.assertEqual(me_resp.data["full_name"], "Login Test User")
