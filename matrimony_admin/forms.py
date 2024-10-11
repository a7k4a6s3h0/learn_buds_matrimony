from django import forms
from U_auth.models import UserPersonalDetails

class AdminLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserPersonalDetailsForm (forms.ModelForm):
    class Meta:
        fields = ['age', 'gender', 'dob', 'user_location', 'smoking_habits', 'drinking_habits', 'interests', 'hobbies', 'qualifications', 'profile_pic', 'short_video', 'bio']
