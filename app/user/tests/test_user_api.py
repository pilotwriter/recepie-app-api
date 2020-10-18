from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserApiTest(TestCase):
    """Test the user api """

    def setUp(self):
        self.client = APIClient()


    def test_create_valid_success(self):
        """check if it creates valid user and returns it """
        payload = {
        'email':'kamil@gmail.com',
        'password':'kamilsiler',
        'name':'kamil'
        }

        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_201_CREATED)


        user = get_user_model().objects.get(**res.data)
        # print()
        # print(user.password)
        # print(payload['password'])
        # print(user.check_password(r'kamilsiler'))
        #
        self.assertTrue(user.check_password(payload['password']))

        self.assertNotIn('password',res.data)


    def test_user_exist(self):
        """CHECK OF EXISTING USER"""
        payload = {'email':'kamil@gmail.com','password':'123456789','name':'kamil'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)



    def test_password_too_short(self):
        """Check if the password is too short"""

        payload = {'email':'kamil@camsilen.com','password':'pw','name':'kamil'}
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
        email = payload['email']
        ).exists()
        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """Tests if a token is created for a user"""
        payload = {'email':'kamil@kamil.com','password':'passwordisstrong'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL,payload)
        self.assertIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):


        """Tests if credentials are invalid"""
        create_user(email='kamil@kamil.com',password = 'kamilkamil')
        payload={ 'email':'kamil@kamil.com','password':'thisoneiswrongpass'}
        res = self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)


    def test_create_token_no_user(self):
        """test if it creates token for non existing user"""
        payload = {'email':'testuser@test.com','password':'passwordishere'}

        res = self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)


    def test_create_token_missing_data(self):
        """test that no token created for absent of data"""

        res = self.client.post(TOKEN_URL,{'email':'one','password':''})

        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)


    def test_retrieve_user_unauthorized(self):
        """Test that authentication required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)




class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@londonappdev.com',
            password='testpass',
            name='fname',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
