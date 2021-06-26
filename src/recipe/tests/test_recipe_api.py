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

    def test_create_basic_recipe(self):
        """should create a basic recipe (no tags or ingredients)"""
        mock_recipe = {
            'title': 'Cheese Cake',
            'price': 10,
            'preperation_time': 25,
        }

        res = self.client.post(RECIPES_URL, mock_recipe)

        recipe = Recipe.objects.get(id=res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in mock_recipe.keys():
            self.assertEqual(mock_recipe[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """should create a recipe with tags"""
        tag1 = create_mock_tag(self.user, 'Vegan')
        tag2 = create_mock_tag(self.user, 'Desert')
        mock_recipe = {
            'title': 'Vegan Cheese Cake',
            'price': 12,
            'preperation_time': 60,
            'tags': [tag1.id, tag2.id]
        }

        res = self.client.post(RECIPES_URL, mock_recipe)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """should create a recipe with ingredients"""
        ingredient1 = create_mock_ingredient(self.user, 'Corn')
        ingredient2 = create_mock_ingredient(self.user, 'Ginger')
        mock_recipe = {
            'title': 'Corny Ginger',
            'price': 2,
            'preperation_time': 10,
            'ingredients': [ingredient1.id, ingredient2.id]
        }

        res = self.client.post(RECIPES_URL, mock_recipe)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """should update a recipe with patch"""
        recipe = create_mock_recipe(user=self.user)
        update = {'title': 'New Test Title!'}

        url = get_detail_recipe_url(recipe.id)
        res = self.client.patch(url, update)

        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, update['title'])

    def test_full_update_recipe(self):
        """should update a recipe with put"""
        recipe = create_mock_recipe(user=self.user)
        update = {
            'title': 'New Test Title!',
            'preperation_time': 100,
            'price': 500,
        }

        url = get_detail_recipe_url(recipe.id)
        res = self.client.put(url, update)

        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, update['title'])
        self.assertEqual(recipe.preperation_time, update['preperation_time'])
        self.assertEqual(recipe.price, update['price'])
