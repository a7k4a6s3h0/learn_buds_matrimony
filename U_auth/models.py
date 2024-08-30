from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from profiles.views import user_accept_pg
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
    is_online = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone', 'password']

    def __str__(self):
        return self.username if self.username else self.email


class UserPersonalDetails(models.Model):

    GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
    ]

    user = models.OneToOneField(costume_user, on_delete=models.CASCADE, related_name="user_details")
    age = models.IntegerField(blank=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=False)
    dob = models.DateField(auto_now=False, auto_now_add=False, blank=False)
    smoking_habits = models.BooleanField(default=False, verbose_name="Smoking Habits")
    drinking_habits = models.BooleanField(default=False, verbose_name="Drinking Habits")
    qualification = models.CharField(max_length=50, blank=False)
    profile_pic = models.ImageField(upload_to='images/', default='img/default_pic.png', blank=True)
    short_video = models.FileField(upload_to='videos/', null=True, blank=True)
    is_employer = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_jobseeker = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}_details"

    class Meta:
        verbose_name = "User Personal Detail"
        verbose_name_plural = "User Personal Details"

    @property
    def profile_pic_url(self):
        if self.profile_pic:
            return f"{settings.MEDIA_URL}{self.profile_pic}"
        return ""

    @property
    def short_video_url(self):
        if self.short_video:
            return f"{settings.MEDIA_URL}{self.short_video}"
        return ""

class Pictures(models.Model):

    user = models.ForeignKey(UserPersonalDetails, verbose_name= "reverse_user_pic", on_delete=models.CASCADE)
    photos = models.ImageField(upload_to='images/', blank=True)
    add_at = models.DateTimeField(auto_now_add=True)

    @property
    def profile_pic_url(self):
        if self.photos:
            return f"{settings.MEDIA_URL}{self.profile_pic}"
        return ""
    
    def __str__(self) -> str:
        return super().__str__() + f"photos_of_{self.user.user.username}"

class Hobbies(models.Model):
    user = models.ForeignKey(UserPersonalDetails, on_delete=models.CASCADE)
    hobby = models.CharField(max_length=100)

    def __str__(self):
        return f"hooby_of_{self.user.user.username}"
    

class Intrestes(models.Model):
    user = models.ForeignKey(UserPersonalDetails, on_delete=models.CASCADE)
    intrest = models.CharField(max_length=100)

    def __str__(self):
        return f"interest_of_{self.user.user.username}"

class Job_Details(models.Model):

    EX_LEVEL = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
    ]

    user = models.ForeignKey(costume_user, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=False)
    job_title = models.CharField(max_length=100, blank=False)
    designation = models.CharField(max_length=50, blank=False)
    location = models.CharField(max_length=100, blank=False)
    experiences_level = models.CharField(max_length=50, choices=EX_LEVEL, blank=False)

    def __str__(self):
        return f"job_details_of_{self.user.username}"

class Relationship_Goals(models.Model):
    user = models.OneToOneField(costume_user, on_delete=models.CASCADE)
    is_short = models.BooleanField(default=False, blank=False)
    is_long = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return f"relation_type_of_{self.user.username}"

class AdditionalDetails(models.Model):

    MARRIED_STATUS = [
        ('single', 'single'),
        ('married' , 'married'),
        ('divocred', 'divocred')
    ]

    user = models.ForeignKey(costume_user, on_delete=models.CASCADE)
    is_married = models.CharField(choices=MARRIED_STATUS, max_length=50,blank=False)
    auual_income = models.BigIntegerField(blank=False)
    family_type = models.CharField(max_length=50, blank=False)
    family_name = models.CharField(max_length=50, blank=False)
    father_name = models.CharField(max_length=50, blank=False)
    father_occupation = models.CharField(max_length=50, blank=False)
    mother_name = models.CharField(max_length=50, blank=False)
    mother_occupation = models.CharField(max_length=50, blank=False)
    total_siblings = models.IntegerField(blank=False)
    total_siblings_married = models.IntegerField(blank=False)
    height = models.IntegerField(blank=False)
    weight = models.IntegerField(blank=False)
    blood_group = models.CharField(max_length=50, blank=False)
    religion = models.CharField(max_length=50, blank=False)
    caste_or_community = models.CharField(max_length=50, blank=False)
    complexion = models.CharField(null=True,max_length=50, blank=False)


    class Meta:
        verbose_name = 'Additional Detail'
        verbose_name_plural = 'Additional Details'

    def __str__(self):
        return f"{self.user.username}_extra_details"


class UserDisabilities(models.Model):
    user = models.ForeignKey(AdditionalDetails, on_delete=models.CASCADE)
    disability_type = models.CharField(max_length=50)



class OTP(models.Model):
    user = models.OneToOneField(costume_user, on_delete=models.CASCADE)
    otp_code = models.IntegerField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_validated = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.username}_otpcode"


# ...............-.model for user profile view............................




