from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


MOCKED_USER = {
    'email': 'test@example.com',
    'password': 'test123',
    'name': 'Mona Lisa'
}

TAGS_URL = reverse('recipe:tag-list')


class PublicClassApiTests(TestCase):
    """Public tags api tests (unauthorized)"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """should fail to retrive tags due to login require"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateClassApiTests(TestCase):
    """Private tags api tests (authenticated)"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(**MOCKED_USER)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_tag_list(self):
        """should retrive user's tag list"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Mexican')
        Tag.objects.create(user=self.user, name='Grill')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """should test that the retrived tags are for the authenticated user"""
        user = get_user_model().objects.create_user('test@gmail.com', '123456')
        Tag.objects.create(user=user, name='Diary')
        tag = Tag.objects.create(user=self.user, name='Mexican')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successfull(self):
        """should create a new tag for authenticated user"""
        payload = {'name': 'Test Tag'}

        res = self.client.post(TAGS_URL, payload)

        is_exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(is_exists)

    def test_create_tag_invalid(self):
        """should create a new tag for authenticated user"""
        payload = {'name': ''}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
