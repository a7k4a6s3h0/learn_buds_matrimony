from typing import Any
from django import forms
from U_messages.models import NotificationDetails,AmidUsers
from U_auth.models import costume_user

# import get_object_or_404()
from django.shortcuts import get_object_or_404

class AdminLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class AdminProfileForm(forms.Form):
    pass



class NotificationDetailsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        id_input = kwargs.pop('get_id', None)  # Use pop to remove it from kwarg
        print(id_input)
        self.user_id = id_input  # Store id_input for later use
        super().__init__(*args, **kwargs)  # Call the parent class's __init__

    class Meta:
        model = NotificationDetails
        fields = [
            'user',  # ForeignKey, use a ModelChoiceField by default
            'title',  # CharField
            'description',  # CharField
            'image',  # ImageField
            'targeted_audiences',  # CharField with choices
            'target_specific',  # CharField with choices
            'other_service',  # CharField with choices
            'start_at',  # DateField
            'end_at',  # DateField
        ]
    
    user = forms.ModelChoiceField(
        queryset=costume_user.objects.all(),  # Update queryset as per your logic
        widget=forms.Select(attrs={'class': 'form-control'})  # Add Bootstrap class
    )
    title = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Enter notification title','class':'form-control'}))
    description = forms.CharField(max_length=250, widget=forms.Textarea(attrs={'placeholder': 'Enter notification description','class':'form-control'}))
    mage = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))

    targeted_audiences = forms.ChoiceField(
        choices=NotificationDetails.AIMED_AUDIENCES,
        widget=forms.Select(attrs={'id': 'audience_type','class':'form-control'})
    )
    target_specific = forms.ChoiceField(choices=NotificationDetails.TARGETED_MODULE
            ,widget=forms.Select(attrs={'id': 'target_specific','class':'form-control'}))
                                
    other_service = forms.ChoiceField(choices=NotificationDetails.SEND_VIA,
                                      widget=forms.Select(attrs={'id': 'target_specific','class':'form-control'}))
                                      

    start_at = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class':'form-control'}))
    end_at = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class':'form-control'}))


    def save(self, commit: bool = True) -> NotificationDetails:
        # First, save the NotificationDetails instance
        obj = super().save(commit=False)  # Create an instance but don't save to the database yet

        if commit:
            obj.save()  # Save the NotificationDetails instance if commit is True

        # Check if targeted_audiences is "id" and process accordingly
        if self.cleaned_data['targeted_audiences'] == "id":
            user = get_object_or_404(costume_user, id=2)  # Get the user or return a 404 if not found
            
            # Create the AmidUsers instance and link it to the notification
            aim_user = AmidUsers.objects.create(
                notification_obj=obj  # Link the created NotificationDetails instance
            )
            
            # Assuming user is a single instance, you would usually use add() instead of set()
            aim_user.users.add(user)  # Add the user to the many-to-many field

            aim_user.save()  # Save the AmidUsers instance

        return obj  # Return the saved NotificationDetails instance



#arjun


# forms.py

from .models import Add_expense

class AddExpenseForm(forms.ModelForm):
    class Meta:
        model = Add_expense
        fields = ['date', 'invoice_number', 'category', 'description', 'remark','dr', 'cr', 'invoice']  # Add other fields as necessary
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'invoice': forms.ClearableFileInput(attrs={'multiple': False}),  # Adjust if needed
        }

from django import forms
from U_auth.models import costume_user, Job_Details

class AdminProfileEditForm(forms.ModelForm):
    designation = forms.CharField(max_length=100, required=False)
    job_location = forms.ModelChoiceField(queryset=Job_Details.objects.all(), required=False)  # Add this field
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        required=False,  # Optional for edits
    )

    class Meta:
        model = costume_user
        fields = ['username', 'email', 'phone', 'country_details']  # Add any other fields needed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('instance'):
            try:
                job_details = Job_Details.objects.get(user=kwargs['instance'])
                self.fields['designation'].initial = job_details.designation
                self.fields['job_location'].initial = job_details.job_location  # Populate initial value
            except Job_Details.DoesNotExist:
                self.fields['designation'].initial = ''
                self.fields['job_location'].initial = None  # Set initial to None if no job location found

    def save(self, commit=True):
        user = super().save(commit)
        designation = self.cleaned_data.get('designation')
        job_location = self.cleaned_data.get('job_location')  # Get job_location
        password = self.cleaned_data.get('password')

        if commit:
            job_details, created = Job_Details.objects.get_or_create(user=user)
            job_details.designation = designation
            job_details.job_location = job_location  # Assign job_location here
            job_details.save()

            if password:
                user.set_password(password)
                user.save()

        return user
