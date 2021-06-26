from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from core.tests.test_models import create_mock_recipe, create_mock_tag

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
        """should fail to create new tag for authenticated user"""
        payload = {'name': ''}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_tags_assigned_to_recipe(self):
        """should filter tags that assigned to recipe"""
        assigned_tag = create_mock_tag(user=self.user, name='Mexican')
        unassigned_tag = create_mock_tag(user=self.user, name='Italian')

        recipe = create_mock_recipe(user=self.user)
        recipe.tags.add(assigned_tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        assigned_serializer = TagSerializer(assigned_tag)
        unassigned_serializer = TagSerializer(unassigned_tag)

        self.assertIn(assigned_serializer.data, res.data)
        self.assertNotIn(unassigned_serializer.data, res.data)

    def test_retrive_tags_assigned_unique(self):
        """should filter unique tags that assigned to recipe"""
        tag = create_mock_tag(user=self.user, name='Mexican')
        create_mock_tag(user=self.user, name='Italian')

        recipe1 = create_mock_recipe(user=self.user)
        recipe2 = create_mock_recipe(user=self.user)
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
