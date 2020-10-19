from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models  import Recipe
from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user,**params):
    """create and return a sample recipe"""
    defaults = {
    'title':'patates',
    'time_minutes':5,
    'price':10.00
    }
    defaults.update(params)
    return Recipe.objects.create(user=user,**defaults)


"""authentication,retrieve list of recipes,recieps belongs to auth user """

class PublicRecipeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()


    def test_auth_required(self):
        """checks every user must be authenticated"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTest(TestCase):
    """chech private functionalities of recipe api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user('email@email.com','123456789')
        self.client = APIClient()
        self.client.force_authenticate(user = self.user)



    def test_retrieve_recipes(self):
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes,many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)


    def test_recipes_limited_to_user(self):
        """test retrieving data of specific user """
        user2 = get_user_model().objects.create_user('kamil@kamil.com','123456789')
        payload= {'title':'carbonara','price':20.00}
        recipe1 = sample_recipe(user = self.user)
        recipe2 = sample_recipe(user = user2,**payload)

        res = self.client.get(RECIPE_URL)
        recipes  = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes,many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data,serializer.data)
