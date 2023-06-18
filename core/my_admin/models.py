from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User, PermissionsMixin

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password, is_active = True):
        """
        Function to create a user
        :param email:
        :param first_name:
        :param last_name:
        :param phone_num:
        :param password:
        :return:
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not first_name:
            raise ValueError('Users must have a first name')
        if not last_name:
            raise ValueError('Users must have a last name')
        if not password:
            raise ValueError('Users must have a password')
        
        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            is_active = is_active,
        )
        user.set_password(password) # hashes the password
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)




class CustomUser(AbstractBaseUser, PermissionsMixin):

    """Model represetation for a user"""
    first_name = models.CharField(max_length= 25, verbose_name="First Name")
    last_name = models.CharField(max_length= 25, verbose_name="Lase Name")
    email = models.EmailField(max_length= 50, unique=True, verbose_name="Email")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        ]
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

   
    def get_short_name(self):
        return self.first_name
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.get_full_name()
    


