from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email='kamil@kamil.com',password = '1234567980'):
    return get_user_model().objects.create_user(email,password)
class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with email and password """
        email = "kamil@gmail.com"
        password ="kamilinrenklidünyası"

        user = get_user_model().objects.create_user(
        email=email,
        password=password
        )

        self.assertEqual(user.email , email)
        self.assertTrue(user.check_password(password))

    def test_user_email_normalized(self):
        email ='kamil@GMAIL.COM'
        password = "kamil123"
        user = get_user_model().objects.create_user(email, password)

        self.assertEqual(user.email,email.lower())


    def test_user_email_valid(self):
        """Test creating user with no email raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None,"pass1234")


    def test_create_super_user(self):
        """Test creation of superuser"""
        user=get_user_model().objects.create_superuser(
        "kamil@gmail.com",
        "asldalşdald"
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    def test_tag_str(self):
        """Test the tag representaiton """
        tag = models.Tag.objects.create(
        user = sample_user(),
        name = 'Vegan'
        )

        self.assertEqual(str(tag),tag.name)


    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """test the recipe string representation"""
        recipe = models.Recipe.objects.create(
        user = sample_user(),
        title='Steak and mushroom souce',
        time_minutes = 5,
        price = 5.00,)
        self.assertEqual(str(recipe),recipe.title)
