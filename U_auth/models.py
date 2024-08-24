from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from . manager import UserManager


class Country_codes(models.Model):
    country_code = models.CharField(max_length=10, unique=True)
    country_name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.country_name

class languages(models.Model):
    language_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.language_name


class costume_user(AbstractUser):
    email = models.EmailField(unique=True, max_length=100)
    phone = models.CharField(
        max_length=10, 
        unique=True, 
        validators=[RegexValidator(
            regex=r"^\d{10}$", 
            message="Phone number must be 10 digits only."
        )]
    )
    user_language = models.ForeignKey(languages, on_delete=models.SET_NULL, related_name="reverse_User_lang", null=True)
    country_details = models.ForeignKey(Country_codes, on_delete=models.SET_NULL, related_name="reverse_User_country", null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone', 'password']

    def __str__(self):
        return self.username if self.username else self.email


class OTP(models.Model):
    user = models.OneToOneField(costume_user, on_delete=models.CASCADE)
    otp_code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_validated = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.username} otpcode"


# ................model for user profile view............................