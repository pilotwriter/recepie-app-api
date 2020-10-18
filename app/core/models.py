from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.contrib.auth.hashers import make_password


class UserManager(BaseUserManager):
    def create_user(self,email,password=None, **extra_fields):
        """Create user and saves it """
        if not email:
            raise ValueError('All users must have an email adress!')
        user = self.model(email =self.normalize_email(email) ,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password):
        """creates and saves new superuser"""
        user = self.create_user(email,password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user




class User(AbstractBaseUser,PermissionsMixin):
    """Custom user Model"""
    email = models.EmailField(max_length=255, unique=True)
    name =models.CharField(max_length=255)
    is_active=models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects =  UserManager()


    USERNAME_FIELD = "email"
