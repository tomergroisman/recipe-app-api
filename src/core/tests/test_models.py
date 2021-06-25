from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_mock_user(email='test@example.com', password='test123'):
    return get_user_model().objects.create_user(email, password)


def create_mock_tag(user, name):
    return models.Tag.objects.create(user=user, name=name)


def create_mock_ingredient(user, name):
    return models.Ingredient.objects.create(user=user, name=name)


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
        # tags = [
        #     create_mock_tag(user, 'Meat'),
        #     create_mock_tag(user, 'Traditional'),
        # ]
        # ingredients = [
        #     create_mock_ingredient(user, 'Steak'),
        #     create_mock_ingredient(user, 'Mushroom'),
        #     create_mock_ingredient(user, 'Onion'),
        # ]
        mock_recipe = {
            'title': 'Mushroom Steak',
            'user': user,
            'preperation_time': 90,
            'price': 100,
            # 'tags': tags,
            # 'ingredients': ingredients,
        }

        recipe = models.Recipe.objects.create(**mock_recipe)

        self.assertEqual(str(recipe), mock_recipe['title'])
