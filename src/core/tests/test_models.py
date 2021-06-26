from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_mock_user(email='test@example.com', password='test123'):
    return get_user_model().objects.create_user(email, password)


def create_mock_tag(user, name) -> models.Tag:
    """Create and return a mock tag"""
    return models.Tag.objects.create(user=user, name=name)


def create_mock_ingredient(user, name) -> models.Ingredient:
    """Create and return a mock ingredient"""
    return models.Ingredient.objects.create(user=user, name=name)


def create_mock_recipe(user, **params) -> models.Recipe:
    """Create and return a mock recipe"""
    mock_recipe = {
        'title': 'Mock Recipe',
        'preperation_time': 5,
        'price': 10.5,
    }
    mock_recipe.update(params)

    return models.Recipe.objects.create(user=user, **mock_recipe)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """should create a user with an email"""
        email = 'test@example.com'
        password = 'test123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """should create a user with a normalized email address"""
        email = 'test@EXAMPLE.COM'
        password = 'test123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """should raise an error for invalid email address"""
        with self.assertRaises(ValueError):
            email = None
            password = 'test123'

            get_user_model().objects.create_user(
                email=email,
                password=password
            )

    def test_create_new_superuser(self):
        """should create a new superuser"""
        email = 'test@example.com'
        password = 'test123'

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """should test the tag string representation"""
        tag = models.Tag.objects.create(
            user=create_mock_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """should test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=create_mock_user(),
            name='Carrot'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """should test the recipe string representation"""
        user = create_mock_user()
        mock_recipe = {
            'title': 'Mushroom Steak',
            'user': user,
            'preperation_time': 90,
            'price': 100,
        }

        recipe = models.Recipe.objects.create(**mock_recipe)

        self.assertEqual(str(recipe), mock_recipe['title'])

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """should test that the image saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'test.jpg')

        expected_path = f"uploads/recipe/{uuid}.jpg"

        self.assertEqual(file_path, expected_path)
