from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from core.tests.test_models import (
    create_mock_tag, create_mock_ingredient, create_mock_recipe
)

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


MOCKED_USER = {
    'email': 'test@example.com',
    'password': 'test123',
    'name': 'Mona Lisa'
}

RECIPES_URL = reverse('recipe:recipe-list')


def get_detail_recipe_url(recipe_id):
    """Return the recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


class PublicRecipeApiTests(TestCase):
    """Public recipe api tests (unauthorized)"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """should fail to retrive tags due to login require"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Private recipe api tests (authenticated)"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(**MOCKED_USER)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_recipe_list(self):
        """should retrive user's recipe list"""
        create_mock_recipe(self.user)
        create_mock_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """
        should test that the retrived recipes are for the authenticated user
        """
        user = get_user_model().objects.create_user('test@gmail.com', '123456')

        create_mock_recipe(user)
        create_mock_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_review_recipe_detail(self):
        """should test detailed view of a recipe"""
        recipe = create_mock_recipe(self.user)
        recipe.tags.add(create_mock_tag(self.user, 'Meat'))
        recipe.ingredients.add(create_mock_ingredient(self.user, 'Steak'))

        url = get_detail_recipe_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
