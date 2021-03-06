from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

MOCKED_USER = {
    'email': 'test@example.com',
    'password': 'test123',
    'name': 'Mona Lisa'
}


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users api (unauthenticated requests)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """should create a user with valid payload"""
        res = self.client.post(CREATE_USER_URL, MOCKED_USER)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)

        self.assertTrue(user.check_password(MOCKED_USER['password']))
        self.assertNotIn('password', res.data)

    def test_create_user_and_user_exists(self):
        """should fail to create user if the user is already exists"""
        create_user(**MOCKED_USER)

        res = self.client.post(CREATE_USER_URL, MOCKED_USER)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """should fail to create user if the password is too short"""
        res = self.client.post(CREATE_USER_URL, {
            **MOCKED_USER,
            'password': 'pw'
        })
        user_exists = get_user_model().objects.filter(
            email=MOCKED_USER['email']
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exists)

    def test_bad_method_get_create_user(self):
        """should fail to complete a get request for create user"""
        res = self.client.get(CREATE_USER_URL, {
            **MOCKED_USER,
            'password': 'pw'
        })

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_token_for_user(self):
        """should create a token for the user"""
        create_user(**MOCKED_USER)
        res = self.client.post(TOKEN_URL, MOCKED_USER)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_invalid_credentials(self):
        """should not create a token for invalid credentials"""
        create_user(**MOCKED_USER)
        res = self.client.post(TOKEN_URL, {
            **MOCKED_USER,
            'password': 'WrongPass'
        })

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_without_user(self):
        """should not create a token for a non existing user"""
        res = self.client.post(TOKEN_URL, MOCKED_USER)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_missing_field(self):
        """should not create a token for a missing field"""
        res = self.client.post(TOKEN_URL, {
            **MOCKED_USER,
            'password': ''
        })

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_retrive_user_unauthorized(self):
        """should fail to retrive profile for unauthenticated user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test the users api (authenticated requests)"""

    def setUp(self):
        self.user = create_user(**MOCKED_USER)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_user_authorized(self):
        """should retrive profile for authenticated user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], MOCKED_USER['email'])
        self.assertEqual(res.data['name'], MOCKED_USER['name'])

    def test_post_profile_not_allowed(self):
        """should fail to POST on profile url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile_success(self):
        """should update the user's profile"""
        update_fields = {
            'password': 'newpassword',
            'name': 'Joule Vern',
        }
        res = self.client.patch(ME_URL, update_fields)

        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, update_fields['name'])
        self.assertTrue(self.user.check_password(update_fields['password']))
