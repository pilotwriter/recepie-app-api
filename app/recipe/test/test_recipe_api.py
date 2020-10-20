from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models  import Recipe,Tag,Ingredient
from recipe.serializers import RecipeSerializer,RecipeDetailSerializer
import tempfile
import os


from PIL import Image

RECIPE_URL = reverse('recipe:recipe-list')

def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])



def detail_url(recipe_id):
    """return recipe detail url """
    return reverse('recipe:recipe-detail',args = [recipe_id])

def sample_tag(user,name='Main Course'):
    """create and return a sample tag """
    return Tag.objects.create(user=user ,name = name)

def sample_ingredient(user,name='Garlic'):
    """create sample ingredient and returns it"""
    return Ingredient.objects.create(user=user,name=name)

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

    def test_view_recipe_details(self):
        """test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user = self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data,serializer.data)

    def test_create_basic_recipe(self):
        """test creating simple recipe"""
        payload = {'title':'chocolate','price':15.00,'time_minutes':5}
        res = self.client.post(RECIPE_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key],getattr(recipe,key))


    def test_create_recipe_with_tags(self):
        """test creating a recipe with tags"""
        tag1 = sample_tag(user = self.user,name='Vegan')
        tag2 = sample_tag(user = self.user,name ='Dessert')
        payload = {
        'title':'avacado icecream',
        'tags':[tag1.id,tag2.id],
        'price':15.00,'time_minutes':5

        }
        res = self.client.post(RECIPE_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id= res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(),2)
        self.assertIn(tag1,tags)
        self.assertIn(tag2,tags)


    def test_create_recipe_with_ingredients(self):
        """test creating a recipe with ingredients """
        ingredient1 = sample_ingredient(user = self.user,name='Carrot')
        ingredient2 = sample_ingredient(user = self.user,name ='Kartuska')
        payload = {
        'title':'Irish stew',
        'price':'19.99',
        'ingredients':[ingredient1.id,ingredient2.id],
        'time_minutes':20
        }
        res = self.client.post(RECIPE_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(),2)
        self.assertIn(ingredient1,ingredients)
        self.assertIn(ingredient2,ingredients)

    def test_patial_update_recipe(self):
        """Test updating a recipe partially """
        recipe  = sample_recipe(user= self.user)
        tag = sample_tag(user = self.user)
        ingredient = sample_ingredient(user = self.user)

        new_tag= sample_tag(user=self.user,name='Dessert')
        new_ingredient = sample_ingredient(user = self.user,name= 'Sugar')

        url = detail_url(recipe.id)

        payload = {'title':'puding','tags':[new_tag.id],'ingredients':[new_ingredient.id]}

        res = self.client.patch(url,payload)
        recipe.refresh_from_db()

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn(recipe.title,payload['title'])
        tags = recipe.tags.all()
        ingredients = recipe.ingredients.all()
        self.assertEqual(len(tags),1)
        self.assertIn(new_tag,tags)
        self.assertIn(new_ingredient,ingredients)

    def test_full_update_recipe(self):
        """Test full update of a recipe"""
        recipe = sample_recipe(user=self.user)
        tag = sample_tag(user=self.user)
        ingredient =sample_ingredient(user = self.user)
        recipe.tags.add(tag)
        recipe.ingredients.add(ingredient)
        url = detail_url(recipe.id)
        payload = {'title':'Kavurma','time_minutes':25,'price':5.00}
        self.client.put(url,payload)

        recipe.refresh_from_db()
        self.assertEqual(payload['title'],recipe.title)
        self.assertEqual(payload['time_minutes'],recipe.time_minutes)
        self.assertEqual(payload['price'],recipe.price)

        tags = recipe.tags.all()
        self.assertEqual(len(tags),0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user', 'testpass')
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
