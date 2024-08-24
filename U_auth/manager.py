from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
import re

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValidationError("Email is required.")
        
        if not password:
            raise ValueError("Password must be provided.")
        
        # Normalize the email address
        email = self.normalize_email(email)
        print("login.....................................")
        # Set is_active to False if the user is not a superuser
        if not extra_fields.get('is_superuser', False):
            extra_fields.setdefault('is_active', False)

        user = self.model(email=email,password=password, **extra_fields)
        user.set_password(password)  # This will hash the password
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
    
        return self.create_user(email, password, **extra_fields)
