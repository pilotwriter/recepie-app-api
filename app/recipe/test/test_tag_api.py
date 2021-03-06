from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models  import Tag,Recipe
from recipe.serializers import TagSerializer



TAGS_URL = reverse('recipe:tag-list')



class PublicTagApiTest(TestCase):
    """tests public tags"""

    def setUp(self):
        self.client = APIClient()



    def test_login_required(self):
        """test that login is required to retrieve tag"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTest(TestCase):
    def setUp(self):
        self.user  = get_user_model().objects.create_user('kamil@kamil.com','123456789qwe')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_retrieve_tags(self):
        """test retrieving tags"""
        Tag.objects.create(user=self.user,name='Vegan')
        Tag.objects.create(user=self.user,name='Meat')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')

        serializer = TagSerializer(tags,many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)


    def test_tags_limited_to_user(self):
        """Test that tags returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@londonappdev.com',
            'testpass'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test it succesfully create a tag"""
        payload = {'name':'Desserts'}
        res = self.client.post(TAGS_URL,payload)

        exist = Tag.objects.filter(
        user = self.user,
        name = payload['name']
        ).exists()

        self.assertTrue(exist)
        #self.assertEqual(res.status_code,status.HTTP_200_OK)
    def test_create_tag_invalid(self):
        """test it does not create a tag with empty name"""
        payload = {'name':''}
        res = self.client.post(TAGS_URL,payload)

        # exist = Tag.objects.filter(
        # user = self.user,
        # name = payload['name']
        # ).exist()
        # self.assertFalse(exist)
        self.assertEqual(res.status_code , status.HTTP_400_BAD_REQUEST)


    def test_retrieve_tags_assigned_to_recipes(self):
        tag1 = Tag.objects.create(user = self.user,name='Breakfast')
        tag2 = Tag.objects.create(user=self.user,name='Lunch')

        recipe1 = Recipe.objects.create(user=self.user,title='Goose Liver on toast',price=5.00,time_minutes=15)

        recipe1.tags.add(tag1)

        res = self.client.get(TAGS_URL,{'assigned_only':1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data,res.data)
        self.assertNotIn(serializer2.data,res.data)


    def test_retrieve_tags_assigned_unique(self):
        """test filtering tags are unique"""
        tag1 = Tag.objects.create(user = self.user,name='Breakfast')
        tag2 = Tag.objects.create(user=self.user,name='Lunch')

        recipe1 = Recipe.objects.create(user=self.user,title='Goose Liver on toast',price=5.00,time_minutes=15)
        recipe2 = Recipe.objects.create(user = self.user,title='Egg Benedict',price=5.00,time_minutes=15)
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)

        res = self.client.get(TAGS_URL,{'assigned_only':1})
        self.assertEqual(len(res.data),1)
