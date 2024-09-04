from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from . manager import UserManager


class Country_codes(models.Model):
    country_code = models.CharField(max_length=10, unique=True)
    country_name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.country_code

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


class Qualifications(models.Model):
    qualification = models.CharField(max_length=50, blank=False)


    def __str__(self):
        return f"Hobby: {self.qualification}"
    
class Hobbies(models.Model):
    hobby = models.CharField(max_length=100)

    def __str__(self):
        return f"Hobby: {self.hobby}"

class Interests(models.Model):
    interest = models.CharField(max_length=100)

    def __str__(self):
        return f"Interest: {self.interest}"



class Location(models.Model):
    longitude = models.FloatField()
    latitude = models.FloatField()
    address_details = models.JSONField(null=True, blank=True)

    def _str_(self):
        return self.longitude

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
    user_location = models.ForeignKey(Location, on_delete=models.CASCADE)
    smoking_habits = models.BooleanField(default=False, verbose_name="Smoking Habits")
    drinking_habits = models.BooleanField(default=False, verbose_name="Drinking Habits")
    interests = models.ManyToManyField(Interests)
    hobbies = models.ManyToManyField(Hobbies)
    qualifications = models.ManyToManyField(Qualifications)
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


class Job_Details(models.Model):

    EX_LEVEL = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
    ]

    user = models.OneToOneField(costume_user, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=False)
    job_title = models.CharField(max_length=100, blank=False)
    designation = models.CharField(max_length=50, blank=False)
    job_location = models.ForeignKey(Location, on_delete=models.CASCADE)
    experiences_level = models.CharField(max_length=50, choices=EX_LEVEL, blank=False)

    def __str__(self):
        return f"job_details_of_{self.user.username}"

class Relationship_Goals(models.Model):
    user = models.OneToOneField(costume_user, on_delete=models.CASCADE)
    is_short = models.BooleanField(default=False, blank=False)
    is_long = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return f"relation_type_of_{self.user.username}"

class Disabilities(models.Model):
    disability_type = models.CharField(max_length=50)

    def __str__(self) -> str:
        return super().__str__() + f"disability_type_of_{self.disability_type}"
    
class AdditionalDetails(models.Model):

    MARRIED_STATUS = [
        ('single', 'Single'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]

    FAMILY_TYPE_CHOICES = [
        ('joint', 'Joint'),
        ('nuclear', 'Nuclear'),
        ('extended', 'Extended'),
    ]

    RELIGION_CHOICES = [
        ('CH', 'Christianity'),
        ('IS', 'Islam'),
        ('HI', 'Hinduism'),
        ('BU', 'Buddhism'),
        ('JE', 'Judaism'),
        ('SI', 'Sikhism'),
        ('OT', 'Other'),
    ]

    user = models.OneToOneField(costume_user, on_delete=models.CASCADE)
    married_status = models.CharField(choices=MARRIED_STATUS, max_length=50, blank=False)
    annual_income = models.FloatField(blank=False)  
    family_type = models.CharField(choices=FAMILY_TYPE_CHOICES, max_length=50, blank=False)
    family_name = models.CharField(max_length=50, blank=False)
    father_name = models.CharField(max_length=50, blank=False)
    father_occupation = models.CharField(max_length=50, blank=False)
    mother_name = models.CharField(max_length=50, blank=False)
    mother_occupation = models.CharField(max_length=50, blank=False)
    total_siblings = models.IntegerField(blank=False)
    total_siblings_married = models.IntegerField(blank=False)
    height = models.FloatField(blank=False)
    weight = models.FloatField(blank=False)
    blood_group = models.CharField(max_length=50, blank=False)
    religion = models.CharField(choices=RELIGION_CHOICES, max_length=50, blank=False)
    caste_or_community = models.CharField(max_length=50, blank=False)
    user_disabilities = models.ManyToManyField(Disabilities, verbose_name='disabilities') 
    complexion = models.CharField(null=True, max_length=50, blank=False)

    class Meta:
        verbose_name = 'Additional Detail'
        verbose_name_plural = 'Additional Details'

    def __str__(self):
        return f"{self.user.username}_extra_details"


class Interest_and_Hobbie(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def _str_(self):
        return self.name

class LifestyleChoice(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def _str_(self):
        return self.name

class PartnerPreference(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    RELIGION_CHOICES = [
        ('CH', 'Christianity'),
        ('IS', 'Islam'),
        ('HI', 'Hinduism'),
        ('BU', 'Buddhism'),
        ('JE', 'Judaism'),
        ('SI', 'Sikhism'),
        ('OT', 'Other'),
    ]
    EDUCATION_LEVEL_CHOICES = [
        ('High School', 'High School'),
        ('Bachelors', 'Bachelors'),
        ('Masters', 'Masters'),
        ('Doctorate', 'Doctorate'),
    ]

    user = models.OneToOneField(costume_user, on_delete=models.CASCADE, related_name="partner_preference")

    age_min = models.IntegerField(default=18)
    age_max = models.IntegerField(default=35)

    preferred_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=False)
    preferred_location = models.ManyToManyField(Location)  # ForeignKey for locations
    interests_hobbies = models.ManyToManyField(Interest_and_Hobbie)
    education_level = models.CharField(max_length=50, choices=EDUCATION_LEVEL_CHOICES)
   
    height_min = models.IntegerField(default=100)  # in cm
    height_max = models.IntegerField(default=220)
    
    weight_min = models.IntegerField(default=40)  # in kg
    weight_max = models.IntegerField(default=150)


    lifestyle_choices = models.ManyToManyField(LifestyleChoice)

    religion = models.CharField(max_length=2, choices=RELIGION_CHOICES, blank=False)
    occupation = models.CharField(max_length=255, blank=False)


    def _str_(self):
        return f"{self.user.username}"

class OTP(models.Model):
    user = models.OneToOneField(costume_user, on_delete=models.CASCADE)
    otp_code = models.IntegerField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_validated = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.username}_otpcode"


class UserExtraDetails(models.Model):
    user = models.OneToOneField(costume_user, on_delete=models.CASCADE)
    device_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    continent = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=10, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    region_name = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    timezone = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    isp = models.CharField(max_length=255, blank=True, null=True)
    org = models.CharField(max_length=255, blank=True, null=True)
    as_name = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.BooleanField(default=False)
    proxy = models.BooleanField(default=False)
    hosting = models.BooleanField(default=False)
    query_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.device_name}"

# ...............-.model for user profile view............................




