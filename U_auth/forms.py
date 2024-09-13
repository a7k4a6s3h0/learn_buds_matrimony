import json
import django.views.generic.edit
import os
import random
from typing import Any
from django import forms
from datetime import date
from .models import *
import re

class MultipleValueField(forms.CharField):
    def clean(self, value):
        # Split the input value into a list based on a delimiter
        value = super().clean(value)
        if value:
            return [item.strip() for item in value.split(',')]
        return []

class CreateUser(forms.ModelForm):
    country_code = forms.ModelChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        queryset=Country_codes.objects.all(),
        required=True,  
        empty_label="Select a country code"  # Optional: a placeholder for the dropdown
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }),
        label="Confirm Password", 
        required=True
    )


    class Meta:
        model = costume_user
        fields = ('username', 'email', 'password', 'phone', 'country_code')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }),
        }
    
    def save(self, commit):
        
        # Call the custom create_user method
        user = costume_user.objects.create_user(
            email=self.cleaned_data['email'],
            username=self.cleaned_data['username'],
            phone=self.cleaned_data['phone'],
            password=self.cleaned_data['password'],
            country_details =Country_codes.objects.get(calling_code=self.cleaned_data['country_code']),

        )
        if commit:
            user.save()

        return user

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not re.match(r'^(?=.*\d)(?=.*[a-zA-Z])[a-zA-Z\d]{8,}$', password):
            raise forms.ValidationError("Password must contain at least 8 characters, including both letters and digits")
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        email = cleaned_data.get('email')
        if not re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
            raise forms.ValidationError("Email address is not valid")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

class LoginForm(forms.Form):

    
    email_or_phone = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'name': 'email_or_phone',
        'placeholder': 'Email or Phone'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 'password',
            'placeholder': 'Password'
        })
    )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()  
        password = cleaned_data.get('password')
        email_or_phone = cleaned_data.get('email_or_phone')
        if not re.match(r'^(?=.*\d)(?=.*[a-zA-Z])[a-zA-Z\d]{8,}$', password):
            raise forms.ValidationError("Password must contain at least 8 characters, including both letters and digits")
        if not re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email_or_phone):
            raise forms.ValidationError("Email address is not valid")
        return cleaned_data  # Return the cleaned data

class GenerateOTP(forms.Form):
    digit1 = forms.CharField(max_length=1, widget=forms.NumberInput(attrs={'maxlength': '1', 'class': 'form-control'}))
    digit2 = forms.CharField(max_length=1, widget=forms.NumberInput(attrs={'maxlength': '1', 'class': 'form-control'}))
    digit3 = forms.CharField(max_length=1, widget=forms.NumberInput(attrs={'maxlength': '1', 'class': 'form-control'}))
    digit4 = forms.CharField(max_length=1, widget=forms.NumberInput(attrs={'maxlength': '1', 'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        digits = [
            cleaned_data.get('digit1', ''),
            cleaned_data.get('digit2', ''),
            cleaned_data.get('digit3', ''),
            cleaned_data.get('digit4', '')
        ]
        otp_code = ''.join(digits)

        if len(otp_code) != 4 or not otp_code.isdigit():
            raise forms.ValidationError("OTP must be exactly 4 digits long.")

        return cleaned_data


class ForgotPasswordForm(forms.Form):

    current_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'name': 'current_pass',
        'placeholder': 'Password'
    })
    )

    password_1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'name': 'password_1',
        'placeholder': 'Password'
    })
    )

    password_2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'name': 'password_2',
        'placeholder': 'Password'
    })
    )
       
    def clean(self):
        cleaned_data = super().clean()
        password_1 = cleaned_data.get('password_1')
        password_2 = cleaned_data.get('password_2')

        if password_1 and password_2:
            if password_1 != password_2:
                raise forms.ValidationError("Passwords do not match.")
            
            # Validate password strength
            if not re.match(r'^(?=.*\d)(?=.*[a-zA-Z])[a-zA-Z\d]{8,}$', password_1):
                raise forms.ValidationError("Password must contain at least 8 characters, including both letters and digits")

        return cleaned_data
    


class ResetPasswordForm(forms.Form):

    email_or_phone = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'name': 'email_or_phone',
        'placeholder': 'Enter email or phone number'
    })
    )
       
    def clean(self):
        cleaned_data = super().clean()
        # password = cleaned_data.get('password', None)
        email_or_phone = cleaned_data.get('email_or_phone', None)
        if not re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email_or_phone):
            raise forms.ValidationError("Email address is not valid")
        
        return cleaned_data    
    

class ResetPasswordForm_2(forms.Form):

    password_1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'name': 'password_1',
        'placeholder': 'Password'
    })
    )

    password_2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'name': 'password_2',
        'placeholder': 'Password'
    })
    )

    def clean(self):
        cleaned_data = super().clean()
        password_1 = cleaned_data.get('password_1')
        password_2 = cleaned_data.get('password_2')

        if password_1 and password_2:
            if password_1 != password_2:
                raise forms.ValidationError("Passwords do not match.")
            
            # Validate password strength
            if not re.match(r'^(?=.*\d)(?=.*[a-zA-Z])[a-zA-Z\d]{8,}$', password_1):
                raise forms.ValidationError("Password must contain at least 8 characters, including both letters and digits")

        return cleaned_data



class UserPersonalDetailsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get user from kwargs
        super().__init__(*args, **kwargs)


    photos = forms.FileField(required=False)
    hobbies = MultipleValueField(
        widget=forms.Textarea(),
        required=True
    )
    Intrestes = MultipleValueField(
        widget=forms.Textarea(),
        required=True
    )
    qualifications = MultipleValueField(
        widget=forms.Textarea(),
        required=True
    )

    location = forms.CharField(
        required=True,
        widget=forms.TextInput()
    )

    address_details = forms.CharField(
        required=True,
        widget=forms.Textarea()
    )
    
    class Meta:
        model = UserPersonalDetails
        fields = ['age', 'gender', 'dob', 'smoking_habits', 'drinking_habits', 'profile_pic', 'short_video', 'is_employer', 'is_employee', 'is_jobseeker']

    allowed_image_extensions = ['jpg', 'jpeg', 'png', 'webp', 'svg']
    allowed_video_extensions = ['mp4', 'mov']


    def clean_profile_pic(self):
        profile_pic = self.files.get('profile_pic')
        if profile_pic:
            if isinstance(profile_pic, str):
                ext = os.path.splitext(profile_pic)[1][1:].lower()  # Handle as a string
            else:
                ext = os.path.splitext(profile_pic.name)[1][1:].lower()  # Handle as a file
            if ext not in self.allowed_image_extensions:
                raise forms.ValidationError(f"Unsupported file extension for profile picture. Allowed extensions are: {', '.join(self.allowed_image_extensions)}")
        return profile_pic

    def clean_short_video(self):
        short_video = self.files.get('short_video')
        if short_video:
            ext = os.path.splitext(short_video.name)[1][1:].lower()
            if ext not in self.allowed_video_extensions:
                raise forms.ValidationError(f"Unsupported file extension for video. Allowed extensions are: {', '.join(self.allowed_video_extensions)}")
        return short_video
    
    def clean_photos(self):
        photos = self.files.getlist('photos', [])
        for photo in photos:
            ext = os.path.splitext(photo.name)[1][1:].lower()
            if ext not in self.allowed_image_extensions:
                raise forms.ValidationError(f"Unsupported file extension for photo '{photo.name}'. Allowed extensions are: {', '.join(self.allowed_image_extensions)}")
        return photos
    
    def clean(self):
        cleaned_data = super().clean()

        # check the required fields are not empty 
        required_fields = ['age', 'gender', 'dob', 'qualifications', 'Intrestes', 'hobbies']
    
        for field in required_fields:
            if not cleaned_data.get(field):
                raise forms.ValidationError(f"{field.replace('_', ' ').capitalize()} is required.")

        age = cleaned_data.get('age')
        dob = cleaned_data.get('dob')
        if age < 18:
            raise forms.ValidationError("Age must be at least 18 years old.")
        today = date.today()
        calculated_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if calculated_age != age:
            raise forms.ValidationError("Age does not match the date of birth.")
        
        
        # Ensure is_employee, is_jobseeker, and is_employer are set to appropriate boolean values
        smoking_habits = cleaned_data.get('smoking_habits', False)
        drinking_habits = cleaned_data.get('drinking_habits', False)
        is_employee = cleaned_data.get('is_employee', False)
        is_jobseeker = cleaned_data.get('is_jobseeker', False)
        is_employer = cleaned_data.get('is_employer', False)

        # Adjust values based on form input
        cleaned_data['smoking_habits'] = bool(smoking_habits)
        cleaned_data['drinking_habits'] = bool(drinking_habits)
        cleaned_data['is_employee'] = bool(is_employee)
        cleaned_data['is_jobseeker'] = bool(is_jobseeker)
        cleaned_data['is_employer'] = bool(is_employer)

        return cleaned_data
        
    def save(self, commit: bool = True) -> Any:
        """Save the form data to the database."""
        try:
            # Access the user from the form instance
            user = self.user

            # Create or update the UserPersonalDetails instance
            datas = UserPersonalDetails(
                user=user,
                age=self.cleaned_data['age'],
                gender=self.cleaned_data['gender'],
                dob=self.cleaned_data['dob'],
                smoking_habits=self.cleaned_data['smoking_habits'],
                drinking_habits=self.cleaned_data['drinking_habits'],
                short_video=self.files.get('short_video'),
                is_employer=self.cleaned_data['is_employer'],
                is_employee=self.cleaned_data['is_employee'],
                is_jobseeker=self.cleaned_data['is_jobseeker']
            )
            pic = self.files.get('profile_pic')
            if pic:
                datas.profile_pic = pic

            # Parse location
            locations = self.cleaned_data['location'].split(',')  # Split the single string into a list of lat and lng
            longitude = float(locations[1].strip())  # Extract and convert longitude
            latitude = float(locations[0].strip())   # Extract and convert latitude

            # Parse address_details
            address_details_str = self.cleaned_data['address_details']  # Extract the single string
            # Parse the JSON string into a Python dictionary
            address_details_json = json.loads(address_details_str)
            
            # Create Location instance
            location_details = Location.objects.create(
                longitude=longitude,
                latitude=latitude,
                address_details=address_details_json
            )

            # Assign to UserPersonalDetails
            datas.user_location = location_details
            if commit:

                # Save the main UserPersonalDetails instance
                datas.save()

                # Handle interests
                interests = self.cleaned_data.get('intrestes', [])
                print(interests,"datas")
                if interests:
                    interests_objects = Interests.objects.filter(interest__in=interests)
                    print(interests_objects,"datas obj")
                    datas.interests.set(interests_objects)  # Assign the interests to the UserPersonalDetails instance

                # Handle hobbies
                hobbies = self.cleaned_data.get('hobbies', [])
                if hobbies:
                    hobby_objects = Hobbies.objects.filter(hobby__in=hobbies)
                    datas.hobbies.set(hobby_objects)  # Assign the hobbies to the UserPersonalDetails instance

                # Handle qualifications
                qualifications = self.cleaned_data.get('qualifications', [])
                if qualifications:
                    qualification_objects = Qualifications.objects.filter(qualification__in=qualifications)
                    datas.qualifications.set(qualification_objects)  # Assign the qualifications to the UserPersonalDetails instance

                # Handle photos
                photos = self.files.getlist('photos', [])
                if photos:
                    for photo in photos:
                        Pictures.objects.create(user=datas, photos=photo)
                        
            return datas    

        except Exception as e:
            # Log the exception or handle it as needed
            raise forms.ValidationError(str(e))


class JobDetailsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # Capture the user instance passed via kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    location = forms.CharField(
        required=True,
        widget=forms.TextInput()
    )

    address_details = forms.CharField(
        required=True,
        widget=forms.Textarea()
    )
    
    class Meta:
        model = Job_Details
        fields = ('job_title', 'company_name', 'designation', 'experiences_level')

    
    def save(self, commit : bool) -> Any:
        job =  super().save(commit=False)
        # Assign the user if it's available
        if self.user:
            job.user = self.user
            # Parse location
            locations = self.cleaned_data['location'].split(',')  # Split the single string into a list of lat and lng
            longitude = float(locations[1].strip())  # Extract and convert longitude
            latitude = float(locations[0].strip())   # Extract and convert latitude

            # Parse address_details
            address_details_str = self.cleaned_data['address_details']  # Extract the single string
            # Parse the JSON string into a Python dictionary
            address_details_json = json.loads(address_details_str)

            # Create Location instance
            location_details = Location.objects.create(
                longitude=longitude,
                latitude=latitude,
                address_details=address_details_json
            )

            # Assign to UserPersonalDetails
            job.job_location = location_details
        if commit:
            job.save()
        return job


class RelationShipGoalForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # Capture the user instance passed via kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Relationship_Goals
        fields = ('is_short', 'is_long')

    def save(self, commit : bool) -> Any:
        relation_type =  super().save(commit=False)
        # Assign the user if it's available
        if self.user:
            relation_type.user = self.user
            relation_type.is_short = self.cleaned_data.get('is_short', False)
            relation_type.is_long = self.cleaned_data.get('is_long', False)
        if commit:
            relation_type.save()
        return relation_type
    

class AdditionalDetailsForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        # Capture the user instance passed via kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    disabilitys = MultipleValueField(widget=forms.Textarea(), required=False)

    class Meta:
        model = AdditionalDetails
        fields = ('married_status', 'annual_income', 'family_type', 'family_name','father_name', 'father_occupation','mother_name','mother_occupation',
                  'total_siblings', 'total_siblings_married', 'height', 'weight', 'blood_group', 'religion' , 'caste_or_community', 'complexion')

    def save(self, commit : bool) -> Any:
        addition_datas =  super().save(commit=False)
        # Assign the user if it's available
        if self.user:
            addition_datas.user = self.user
            
        if commit:
            addition_datas.save()
            self.user.is_completed = True
            self.user.save()
        
            disabilitys = self.cleaned_data.get('disabilitys', [])
            if disabilitys:
                print("yes..in..disabilities")
                types = Disabilities.objects.filter(disability_type__in=disabilitys)
                addition_datas.user_disabilities.set(types)  

        return addition_datas
    



class UserPartnerPreferenceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # Capture the user instance passed via kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = PartnerPreference
        fields = ('age_min', 'age_max', 'preferred_gender', 'preferred_location', 'interests_hobbies', 'education_level', 'height_min',
                  'height_max', 'weight_min', 'weight_max', 'lifestyle_choices', 'religion', 'occupation' )
    
    