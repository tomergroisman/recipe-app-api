from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from core.tests.test_models import create_mock_ingredient, create_mock_recipe

from recipe.serializers import IngredientSerializer


MOCKED_USER = {
    'email': 'test@example.com',
    'password': 'test123',
    'name': 'Mona Lisa'
}

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Public ingredients api tests (unauthorized)"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """should fail to retrive ingredients due to login require"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Private ingredients api tests (authenticated)"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(**MOCKED_USER)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_ingredient_list(self):
        """should retrive user's ingredient list"""
        Ingredient.objects.create(user=self.user, name='Carrot')
        Ingredient.objects.create(user=self.user, name='Beans')
        Ingredient.objects.create(user=self.user, name='Chocolate')

        res = self.client.get(INGREDIENTS_URL)

        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """
        should test that the retrived ingredients
        are for the authenticated user
        """
        user = get_user_model().objects.create_user('test@gmail.com', '123456')
        Ingredient.objects.create(user=user, name='Diary')
        ingredient = Ingredient.objects.create(user=self.user, name='Fish')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successfull(self):
        """should create a new ingredient for authenticated user"""
        payload = {'name': 'Test Tag'}

        res = self.client.post(INGREDIENTS_URL, payload)

        is_exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(is_exists)

    def test_create_ingredient_invalid(self):
        """should fail to create new ingredient for authenticated user"""
        payload = {'name': ''}

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_ingredients_assigned_to_recipe(self):
        """should filter ingredients that assigned to recipe"""
        assigned_ingredient = create_mock_ingredient(
            user=self.user,
            name='Sugar'
        )
        unassigned_ingredient = create_mock_ingredient(
            user=self.user,
            name='Burbon'
        )

        recipe = create_mock_recipe(user=self.user)
        recipe.ingredients.add(assigned_ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        assigned_serializer = IngredientSerializer(assigned_ingredient)
        unassigned_serializer = IngredientSerializer(unassigned_ingredient)

        self.assertIn(assigned_serializer.data, res.data)
        self.assertNotIn(unassigned_serializer.data, res.data)

    def test_retrive_ingredients_assigned_unique(self):
        """should filter unique ingredients that assigned to recipe"""
        ingredient = create_mock_ingredient(user=self.user, name='Apple')
        create_mock_ingredient(user=self.user, name='Beer')

        recipe1 = create_mock_recipe(user=self.user)
        recipe2 = create_mock_recipe(user=self.user)
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
