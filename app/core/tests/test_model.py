from django.test import TestCase
from django.contrib.auth import get_user_model



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
