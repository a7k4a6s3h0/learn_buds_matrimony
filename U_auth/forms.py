import random
from typing import Any
from django import forms
from .models import costume_user, Country_codes, OTP
import re



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
    
    def save(self, commit=True):
        # Call the custom create_user method
        user = costume_user.objects.create_user(
            email=self.cleaned_data['email'],
            username=self.cleaned_data['username'],
            phone=self.cleaned_data['phone'],
            password=self.cleaned_data['password'],
            
            country_details =Country_codes.objects.get(country_name=self.cleaned_data['country_code'])
        )
        if commit:
            user.save()
        return user

    # def __init__(self, *args, **kwargs):
    #     super(CreateUser, self).__init__(*args, **kwargs)
    #     self.fields['password'].widget = forms.PasswordInput()  # Ensure password is inputted securely
    #     self.fields['confirm_password'].widget = forms.PasswordInput()  # Secure input for confirm password

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

    # password = forms.CharField(widget=forms.PasswordInput(attrs={
    #     'class': 'form-control',
    #     'name': 'password',
    #     'placeholder': 'Password'
    # })
    # )
       
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