from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from U_auth.permissions import RedirectNotAuthenticatedUserMixin, check_permissions
from . permissions import RedirectAuthenticatedUserMixin
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.urls import reverse_lazy
from django.urls import reverse
from .otp import generate_otp, validate_otp
from .models import AdditionalDetails, costume_user, Disabilities, OTP, UserPersonalDetails
from django.contrib.sessions.models import Session
from .forms import *
from django.views import View
import httpagentparser
from .find_ip_details import find_details
from django.views.generic import TemplateView
# Create your views here.


def error_404(request, exception):
    return render(request, 'Errors/404.html', status=404)

def error_403(request):
    return render(request, 'Errors/403.html')

def error_500(request):
    return render(request, 'Errors/500.html', status=500)


def trigger_500_error(request):
    # Deliberately raise an exception to simulate a server error
    raise ValueError("This is a manually triggered 500 error for testing purposes!")

# ................................backend code starting..............................................


class SignupView(RedirectAuthenticatedUserMixin, FormView):
    
    template_name = 'auth/auth.html'  # The template to render
    form_class = CreateUser
    user_email = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        interest_list = []
        hobbies_list = []
        qualifications_list = []
        disabilities_list = []
        interests = Interests.objects.all()
        hobbies = Hobbies.objects.all()
        for interest in interests:
            interest_list.append(interest.interest)
        for hobbie in hobbies:
            hobbies_list.append(hobbie.hobby)
        qualifications_obj = Qualifications.objects.all()
        for qualification in qualifications_obj:
            qualifications_list.append(qualification.qualification)
        disabilities_obj = Disabilities.objects.all()
        for disabilitie in disabilities_obj:
            disabilities_list.append(disabilitie.disability_type)    
        context['interest_lists'] = interest_list
        context['hobbie_lists'] = hobbies_list
        context['qualifications'] = qualifications_list
        context['disabilities_list'] = disabilities_list
        context['experance_level'] = ['entry', 'mid', 'senior']
        context['marital_status'] = ['Unmarried', 'Divorced']
        return context
    
    def get_form_kwargs(self):
        """
        Passes the request data to the form.
        """
        # Get the default form kwargs
        kwargs = super().get_form_kwargs()

        # Extract email from the request's POST data
        self.user_email = self.request.POST.get('email', None)

        # Debugging: Print the extracted email
        print(f"Extracted email: {self.user_email}")
        self.request.session['user'] = self.user_email


        print(kwargs, "***********************************")

        return kwargs
    
    def get(self, request: HttpRequest, *args: str, **kwargs: dict) -> HttpResponse:
        if self.request.user.is_authenticated:
            obj = check_permissions(self.request, self.request.user.email)
            response_status = obj.get_model()
            print(response_status, "response_status...................!!!!!!!!!!!!!")  # Debugging
            if response_status is not None:
                for key, value in response_status.items():
                    if key != 'status':
                        model_name = key
                        print(model_name,"model name...................")

                context = self.get_context_data()
                context.update({model_name: True})  # Passing the context variable 
                return self.render_to_response(context)
            
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Handle form validation and user creation here

        
        user = form.save(commit=True)  # Save the form data to create a new user
        print(f"User created: {user}")  # Debugging

        if user:
            # Generate OTP after the user is created
            otp_code = generate_otp(user)
            print(f"Generated OTP: {otp_code}")  # Debugging
            
            # Add a message to the context that OTP was generated successfully
            messages.success(self.request, "OTP generated successfully.")

            # print(self.get_device_name(self.request))
            # find_details(self.request)


        response = super().form_valid(form)

        print(response, "response...................!!!!!!!!!!!!!")  # Debugging
        return response
    
    def get_device_name(self, request):
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            parsed_agent = httpagentparser.detect(user_agent)
            if 'platform' in parsed_agent and 'browser' in parsed_agent:
                device_name = f"{parsed_agent['platform']['name']} - {parsed_agent['browser']['name']} {parsed_agent['browser']['version']}"
            elif 'platform' in parsed_agent:
                device_name = f"{parsed_agent['platform']['name']}"
            elif 'browser' in parsed_agent:
                device_name = f"{parsed_agent['browser']['name']} {parsed_agent['browser']['version']}"
            else:
                device_name = "Unknown Device"
            return device_name
    
    def form_invalid(self, form):
        # Check if the specific error related to "user already exists" is present
        print(self.user_email, "in invalid_form")
        
        if costume_user.objects.filter(email=self.user_email).exists():
            # Handle the "user already exists" error
            print("User already exists error detected")

            obj = check_permissions(self.request, self.user_email)
            response_status = obj.get_model()
            print(response_status, "response_status...................!!!!!!!!!!!!!")  # Debugging

            if response_status is not None:
                if response_status.get('model', None) == 'OTP':
                    # If OTP is already generated, trigger the OTP modal
                    messages.error(self.request, response_status['message'])
                    # Generate OTP after the user is created
                    user = costume_user.objects.get(email=self.user_email)
                    otp_code = generate_otp(user)
                    print(f"Generated OTP: {otp_code}")  # Debugging
                    return redirect(self.get_success_url())
                
                for key, value in response_status.items():
                    if key != 'status':
                        model_name = key
                        print(model_name,"model name...................")

                context = self.get_context_data()
                context.update({model_name: True})  # Passing the context variable 
                return self.render_to_response(context)

        return self.render_to_response(self.get_context_data(form=form, show_signup_modal=True))


    # Redirect to the CheckOTPView URL
    def get_success_url(self):
        # Store context data in the session
        self.request.session['purpose'] = 'newuser_verification'
        # sending message for otp useage
        messages.success(self.request, "For user verification..!!")
        return reverse('check_otp')
    
# code need to change remember
class CheckOTPView(FormView):
    purpose_1 : str = ''
    template_name = 'auth/otp_input.html'  # The template to render
    form_class = GenerateOTP


    def get_url(self, purpose):
        url_dict = {
            'newuser_verification':'auth_page',
            'pass_verification':'auth_page',
            'reset_pass_verification': 'pass_reset_2'
        }
        return url_dict.get(purpose, None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve context data from the session
        context['purpose'] = self.request.session.get('purpose', None)
        return context

    # If no request purpose is found, redirect to the login page (or any other page)
    def get(self, request: HttpRequest, *args: str, **kwargs: dict) -> HttpResponse:

        self.purpose_1 = self.request.session.get('purpose', None)   # Retrieve purpose from session
        
        if not self.purpose_1:
            # If no purpose is found, redirect to the login page (or any other page)
            messages.error(self.request, "Unauthorized access. Please try again.")
            return redirect(reverse('auth_page'))
        
        return super().get(request, *args, **kwargs)  # Call the parent's get method
    
    def form_valid(self, form):
        
        # Retrieve the cleaned data from the form
        User_otp_code = ''.join([form.cleaned_data['digit1'],
                            form.cleaned_data['digit2'],
                            form.cleaned_data['digit3'],
                            form.cleaned_data['digit4']])  
        
        # Retrieve the purpose from the session
        purpose = self.request.session.get('purpose', None)
        boolen, msg, = validate_otp(User_otp_code)
        if boolen:
            # create session for user
            current_user = OTP.objects.get(otp_code=User_otp_code)
            if purpose == 'newuser_verification':
                print("in session creation")
                login(self.request, current_user.user)
            # OTP is valid
            # messages.success(self.request, msg)
            
            return super().form_valid(form)
        else:
            # OTP is invalid
            form.add_error(None, msg)
            return self.form_invalid(form)

    
    def get_success_url(self):
        
        purpose = self.request.session.pop('purpose', None)  

        # Get the URL name from the purpose
        url_name = self.get_url(purpose)
        
        if url_name:
            # If the URL name is valid, reverse it
            return reverse_lazy(url_name)
        else:
            # If the URL name is None, redirect to a default page or raise an error
            messages.error(self.request, "Unable to determine the redirect URL. Please try again.")
            return reverse_lazy('auth_page')


class ResendOTPView(FormView):
    template_name = 'auth/otp_input.html'
    # success_url = reverse_lazy('check_otp')  # URL to redirect to after successful OTP generation

    # Define a dummy form class if your view requires a form but you don't need any input
    class DummyForm(forms.Form):
        pass

    form_class = DummyForm  # Specify a form class even if it's a dummy one

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve context data from the session
        context['purpose'] = self.request.session.get('purpose', None)
        return context


    def get(self, request, *args, **kwargs):
        # Retrieve the purpose and user email from the session
        purpose = self.request.session.get('purpose')
        user_email = self.request.session.get('user')

        if not purpose:
            # If no purpose is found, redirect to the login page (or any other page)
            messages.error(self.request, "No purpose found. Please try again.")
            return redirect(reverse('auth_page'))
        elif not user_email:
            # If no user email is found, redirect to the login page (or any other page)
            messages.error(self.request, "No user email found. Please try again.")
            return redirect(reverse('auth_page'))

        try:
            current_user = costume_user.objects.get(email=user_email)  # Ensure you're using the correct model
            # Generate OTP after the user is found
            otp_code = generate_otp(current_user)
            print(f"Generated OTP: {otp_code}")  # Debugging
            messages.success(self.request, "Resend OTP generated successfully")
            return super().get(request, *args, **kwargs)  # Call the parent's get method to render the form

        except costume_user.DoesNotExist:
            # If the user does not exist, redirect to the login page (or any other page)
            messages.error(self.request, "User does not exist. Please try again.")
            return redirect(reverse('auth_page'))

class LoginView(RedirectAuthenticatedUserMixin, FormView):

    template_name = 'auth/auth.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')
    user_email = None

    def get_form_kwargs(self):
        """
        Passes the request data to the form.
        """
        # Get the default form kwargs
        kwargs = super().get_form_kwargs()

        # Extract email from the request's POST data
        self.user_email = self.request.POST.get('email', None)

        # Debugging: Print the extracted email
        print(f"Extracted email: {self.user_email}")
        self.request.session['user'] = self.user_email


        print(kwargs, "**********************************")

        return kwargs


    def form_valid(self, form):
        """
        If the form is valid, authenticate and log in the user.
        """
        email_or_phone = form.cleaned_data['email_or_phone']
        password = form.cleaned_data['password']

        user = authenticate(email=email_or_phone, password=password)

        if user is not None:
            login(self.request, user)
            return super().form_valid(form)  # Redirects to success_url
        else:
            # Add a non-field error to the form
            form.add_error(None, "Invalid username or password.")
            return self.form_invalid(form)  # Redirects to error handling
    
    def form_invalid(self, form):
        # Render the form with errors and trigger the login modal
        if costume_user.objects.filter(email=self.user_email).exists():
            user = costume_user.objects.get(email=self.user_email)
            if not user.is_verified:
                # Handle the "user already exists" error
                print(self.user_email, "in invalid_form")
                print("User is not verified error detected")

                messages.error(self.request, "You Need to verify yourself. Please check your email for OTP.")
                # Generate OTP after the user is created
                user = costume_user.objects.get(email=self.user_email)
                otp_code = generate_otp(user)
                print(f"Generated OTP: {otp_code}")  # Debugging
                self.request.session['purpose'] = 'newuser_verification'
                return redirect('check_otp')
                    
        return self.render_to_response(self.get_context_data(form=form, show_login_modal=True))
    
    def get_success_url(self):
        # check user completed basic steps firest
        if not self.request.user.is_completed:
            messages.error(self.request, "First complete basic steps..")
            return reverse('auth_page')
        # Redirect to a success URL after form submission
        return reverse_lazy('home')
    

class UserLogout(LoginRequiredMixin,View):
    login_url = 'auth_page'
    def get(self, request):
        logout(request)
        # Redirect to the login page or any other page after logout
        return redirect('auth_page')

    
class ResetPassword(RedirectAuthenticatedUserMixin, FormView):
    template_name = 'auth/auth.html'
    form_class = ResetPasswordForm
    items = ['email', 'phone']

    def form_valid(self, form):
        email_or_phone = form.cleaned_data.get('email_or_phone', None)
        
        try:
            if '@' in email_or_phone:
                user = costume_user.objects.get(email=email_or_phone)
            else:
                user = costume_user.objects.get(phone=email_or_phone)
            self.request.session['user'] = user.email
            otp_code = generate_otp(user)
            print(f"Generated OTP: {otp_code}")  # Debugging
            messages.success(self.request, f"OTP sent to your {self.items}")
            
            # Redirect to the OTP verification page
            return super().form_valid(form)
        
        except costume_user.DoesNotExist:
            # Handle the case where the user does not exist
            messages.error(self.request, "User doesn't exist..!!")
            # Render the form with errors without redirecting
            # return self.form_invalid(form)
            return self.render_to_response(self.get_context_data(form=form, show_resetPass_modal=True))

    def get_success_url(self):
        # Store context data in the session
        self.request.session['purpose'] = 'reset_pass_verification'
        
        # Sending message for OTP usage
        messages.success(self.request, "Verification for password changing..!!")
        # Redirect to a success URL after form submission
        return reverse_lazy('check_otp')

class ResetPassword_2(FormView):

    template_name = 'auth/get_pass.html'
    form_class = ResetPasswordForm_2
    # success_url = reverse('auth_page')

    # If no request purpose is found, redirect to the login page (or any other page)
    def get(self, request: HttpRequest, *args: str, **kwargs: dict) -> HttpResponse:

        # Perform validation here
        user_email = request.session.get('user', None)

        if not user_email:
            # If no user is found in the session, redirect to the login page with an error message
            messages.error(request, "Unauthorized access. Please try again.")
            return redirect(reverse('auth_page'))

        return super().get(request, *args, **kwargs)  # type: ignore

    def form_valid(self, form):
        # Retrieve the user from the session
        try:
            password = form.cleaned_data.get('password_2')
            user_email = self.request.session.pop('user', None)            
            user = costume_user.objects.get(email=user_email)
            user.set_password(password)
            user.save()
            messages.success(self.request, "Password changed successfully")
            return super().form_valid(form)
        except costume_user.DoesNotExist:
            # Handle the case where the user does not exist
            messages.error(self.request, "User doesn't exist..!!")
            # Render the form with errors without redirecting
            return self.form_invalid(form)
        
    def get_success_url(self):
        # Redirect to a success URL after form submission
        self.request.session.pop('user', None) # remove user data from session 
        self.request.session.pop('purpose', None)
        return reverse_lazy('auth_page')


class UserPersonalDetailsView(FormView):
    template_name = 'auth/auth.html'
    form_class = UserPersonalDetailsForm

    def get_context_data(self, **kwargs: dict) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        interest_list = []
        hobbies_list = []
        qualifications_list = []
        qualifications_obj = Qualifications.objects.all()
        for qualification in qualifications_obj:
            qualifications_list.append(qualification.qualification)
        interests = Interests.objects.all()
        hobbies = Hobbies.objects.all()
        for interest in interests:
            interest_list.append(interest.interest)
        for hobbie in hobbies:
            hobbies_list.append(hobbie.hobby)
        context['interest_lists'] = interest_list
        context['hobbie_lists'] = hobbies_list
        context['qualifications'] = qualifications_list
        return context
    
    def get_form_kwargs(self):
        """
        Passes the request data to the form.
        """
        kwargs = super().get_form_kwargs()
        # Get the default form kwargs
        kwargs['user'] = self.request.user  # Pass the user to the form

        print(kwargs, "***********************************")

        return kwargs


    def form_valid(self, form):
        photos = form.files.getlist('photos', None)
        print(photos,"***************************************")
        details = form.save()
        print(details,"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        return super().form_valid(form)
    
    def form_invalid(self, form: Any) -> HttpResponse:
        print("in")
        return self.render_to_response(self.get_context_data(form=form, show_personaldetails_modal=True))
    
    def get_success_url(self) -> str:
        return reverse_lazy('auth_page')
    

class JobDetailsView(FormView):
    template_name = 'auth/auth.html'
    form_class = JobDetailsForm    

    def get_form_kwargs(self):
        """
        Passes the request data to the form.
        """
        kwargs = super().get_form_kwargs()
        # Pass the user to the form
        kwargs['user'] = self.request.user

        print(kwargs, "***********************************")

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['experance_level'] = ['entry', 'mid', 'senior']
        return context

    def form_valid(self, form: Any) -> HttpResponse:
        job = form.save(commit=True)
        return super().form_valid(form)
    
    def form_invalid(self, form: Any) -> HttpResponse:
        
        return self.render_to_response(self.get_context_data(form=form, show_jobdetails_modal=True))
    
    def get_success_url(self) -> str:
        return reverse_lazy('auth_page')

class RelationShipGoalView(FormView):

    template_name = 'auth/auth.html'    
    form_class = RelationShipGoalForm

    def get_form_kwargs(self):
        """
        Passes the request data to the form.
        """
        kwargs = super().get_form_kwargs()
        # Pass the user to the form
        kwargs['user'] = self.request.user
    
        print(kwargs, "***********************************")

        return kwargs

    def form_valid(self, form):
        form.save(commit=True)
        self.request.session['check_type'] = True
        return super().form_valid(form)
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form, show_relationmodel_modal=True))

    def get_success_url(self) -> str:
        return reverse_lazy('auth_page')

def UserType(request):
    
    choose_type = request.GET.get('type')
    print(request.GET, choose_type)
    choices = {}
    
    if choose_type:
        try:
            relation_goal = Relationship_Goals.objects.get(user=request.user)
            choices['Matrimony'] = ('is_long',relation_goal.is_long)
            choices['Dating'] = ('is_short',relation_goal.is_short)
            for value, iteam in choices.items():
                if iteam[1] and iteam[0] == choose_type:
                    # context['show_addition_details_model'] = True
                    request.session.pop('check_type', None)
                    return redirect('auth_page')
                    
            messages.error(request, "Wrong type...!!")
            # context['show_relationship_model'] = True
            return redirect('auth_page')

        except Relationship_Goals.DoesNotExist:
            messages.error(request, "Relationship goals not found for this user.")
            return redirect('auth_page')

    # context['show_relationship_model'] = True    
    messages.error(request, "You Must choose correct one from above option")
    return redirect('auth_page')


class AdditionalDetailsView(FormView):
    template_name = 'auth/auth.html'
    form_class = AdditionalDetailsForm

    def get_context_data(self, **kwargs: dict) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        disabilities_list = []
        disabilities_obj = Disabilities.objects.all()
        for disabilitie in disabilities_obj:
            disabilities_list.append(disabilitie.disability_type)   
        context['disabilities_list'] = disabilities_list
        return context

    def get_form_kwargs(self):
        """
        Passes the request data to the form.
        """
        kwargs = super().get_form_kwargs()
        # Pass the user to the form
        kwargs['user'] = self.request.user
        
        print(kwargs, "***********************************")

        return kwargs

    
    def form_valid(self, form: Any) -> HttpResponse:
        form.save(commit=True)
        return super().form_valid(form)
    
    def form_invalid(self, form: Any) -> HttpResponse:
        return self.render_to_response(self.get_context_data(form=form, show_additionaldetails_modal=True))

    
    def get_success_url(self) -> str:
        return reverse_lazy('auth_page')


class UserProfile(RedirectNotAuthenticatedUserMixin,TemplateView):
    template_name = 'User_profile_templates/profile_view.html'

    
    def get(self, request: HttpRequest, *args: str, **kwargs: dict) -> HttpResponse:
        # Fetch user details and extra photos
        user_details = UserPersonalDetails.objects.get(user=request.user)
        extra_photos = Pictures.objects.filter(user=user_details) 
        
        # Add the details to context
        context = self.get_context_data(user_details=user_details, extra_photos=extra_photos)
        
        # Return the rendered template with the context
        return self.render_to_response(context)

    
class ProfileEdit(RedirectNotAuthenticatedUserMixin, TemplateView):
    template_name = 'User_profile_templates/profile_edit.html'

    def get(self, request: HttpRequest, *args: str, **kwargs: dict) -> HttpResponse:
        # Fetch user details and extra photos
        user_details = UserPersonalDetails.objects.get(user=request.user)
        extra_photos = Pictures.objects.filter(user=user_details) 
        print(extra_photos)
        # Add the details to context
        context = self.get_context_data(user_details=user_details, extra_photos=extra_photos)
        
        # Return the rendered template with the context
        return self.render_to_response(context)
    
    
    def post(self, request: HttpRequest, *args: str, **kwargs: dict) -> HttpResponse:
        # Handle POST data (like form submission)
        field_dict = [(costume_user, 'username', 'email', 'phone'), 
                    (UserPersonalDetails, 'profile_pic', 'bio', 'short_video'), 
                    (Pictures, 'photos')]
        
        # Loop through request.POST items
        for key, value in request.POST.items():
            if value:  # If the POST value is not empty
                # print(f"{key}: {value}")  # Debugging

                # Loop through field_dict and check only the fields 'username', 'email', 'phone'
                for fields in field_dict:
                    if key in fields[1:]:  # fields[1:] to skip the model name and only check field names
                        print(f"{fields[0]}: Matched field '{key}' in the model...")  # Output the matched model

                        # Handle user_data based on the model
                        if fields[0] == costume_user:
                            user_data = fields[0].objects.get(id=request.user.id)
                        else:
                            user_data = fields[0].objects.get(user=request.user)

                        recieved_value = request.POST.get(key)    
                        # Use setattr to dynamically update the model's field
                        setattr(user_data, key, value)  # Dynamically set the field value
                        user_data.save()  # Save the changes
                        
                        print(f"Updated {user_data, key} with {recieved_value}")  # Output the          
        
        # Print all uploaded files  
        print("Files:")
        # print(request.FILES.getlist('photos'))

        for key, value in request.FILES.items():
            print(f"{key}: {value}")
            if value:  # If the POST value is not empty
                for fields in field_dict:
                    if key in fields[1:]:  # fields[1:] to skip the model name and only check field names
                        print(f"{fields[0]}: Matched field '{key}' in the model...")

                        if fields[0] == Pictures:
                            user_details = UserPersonalDetails.objects.get(user=request.user)
                            
                            # Handle file uploads
                            photo_list = request.FILES.getlist(key)  # Retrieve list of files for the key
                            if photo_list:
                                for photo in photo_list:
                                    # Create a new record for each uploaded photo
                                    fields[0].objects.create(user=user_details, photos=photo)
                                messages.success(request, "Photos updated successfully")
                                return redirect('profile_edit')
                        else:
                            # Handle other models (e.g., costume_user, UserPersonalDetails)
                            user_data = fields[0].objects.get(user=request.user)

                            recieved_value = request.FILES.getlist(key)  # Retrieve list of files for the key
                            if recieved_value:
                                for val in recieved_value:
                                    # Use setattr to dynamically update the model's field
                                    setattr(user_data, key, val)  # Dynamically set the field value
                                    user_data.save()  # Save the changes

                            print(f"Updated {user_data} with {recieved_value}")          

        messages.success(request, "Data Updated Sucessfully")
        return redirect('profile_edit')

class RemoveFiles(RedirectNotAuthenticatedUserMixin, View):
    
    def post(self, request: HttpRequest, *args: str, **kwargs: dict) -> HttpResponse:
        # Handle POST data (like form submission)
        id = kwargs.get('id')
        print(f"ID: {id}")
        which_one = kwargs.get('type')
        print(f"Which one: {which_one}")
        user_details = UserPersonalDetails.objects.get(user=request.user)
        if which_one == 'photos':
            # Get the user's profile picture
            extra_photos = Pictures.objects.filter(user=user_details)
            for photo in extra_photos:
                if photo.id == int(id):
                    photo.delete()
                    print(f"Deleted photo with id: {id}")
                    messages.success(request, "Photo deleted successfully")

        if which_one == 'reel':
            # Get the user's reel
            user_details.short_video = None
            user_details.save()
            messages.success(request, "reel deleted successfully")

        return redirect('profile_edit')

class ForgotPassword(RedirectNotAuthenticatedUserMixin, FormView):
    template_name = 'User_profile_templates/change_password.html'
    form_class = ForgotPasswordForm

    def form_valid(self, form):
        password = form.cleaned_data['current_password']
        new_password = form.cleaned_data['password_2']
        try:
            current_user = costume_user.objects.get(password=password)
            if check_password(password, current_user.password):
                messages.error(self.request, "Incorrect Password..!!!")

            else:
                # current_user.set_password(new_password)  # Set the new password (Django will hash it)
                # current_user.save()  # Save the updated user
                messages.success(self.request, "Password changed successfully.")

            return super().form_valid(form)
        except costume_user.DoesNotExist:
            messages.error(self.request, "User does not exist.")
            return super().form_invalid(form)
    
    def get_success_url(self):
        # Redirect to a success URL after form submission
        return reverse_lazy('change_pass')


class UserSetting(RedirectNotAuthenticatedUserMixin, TemplateView):
    template_name = 'User_profile_templates/user_setting.html'

    def get_context_data(self, **kwargs: dict) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class UserPrivacySetting(RedirectNotAuthenticatedUserMixin, TemplateView):

    template_name = 'User_profile_templates/privacy_setting.html'


    def get_context_data(self, **kwargs: dict) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['location_details'] = UserPersonalDetails.objects.get(user=self.request.user)
        context['device_name'] = self.get_device_name(self.request)
        context['active_sessions_count'] = self.get_active_sessions_count(self.request.user)  # Active sessions count
        return context

    def get_device_name(self, request):
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            parsed_agent = httpagentparser.detect(user_agent)
            if 'platform' in parsed_agent and 'browser' in parsed_agent:
                device_name = f"{parsed_agent['platform']['name']} - {parsed_agent['browser']['name']} {parsed_agent['browser']['version']}"
            elif 'platform' in parsed_agent:
                device_name = f"{parsed_agent['platform']['name']}"
            elif 'browser' in parsed_agent:
                device_name = f"{parsed_agent['browser']['name']} {parsed_agent['browser']['version']}"
            else:
                device_name = "Unknown Device"
            return device_name

    def get_active_sessions_count(self, user):
        # Get all sessions
        sessions = Session.objects.filter(expire_date__gte=timezone.now())

        # Filter sessions by user ID
        count = 0
        for session in sessions:
            data = session.get_decoded()  # Get session data
            if str(user.id) == str(data.get('_auth_user_id')):  # Compare user ID
                count += 1
        return count 


    def post(self, request: HttpRequest, *args: str, **kwargs: dict) -> HttpResponse:
        self.clear_other_sessions(request.user)
        return redirect('privacy_setting')

    def clear_other_sessions(self, user):
        current_session_key = self.request.session.session_key
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        
        # Loop through all sessions and delete those that belong to the user but are not the current session
        for session in sessions:
            data = session.get_decoded()
            if str(user.id) == str(data.get('_auth_user_id')) and session.session_key != current_session_key:
                session.delete()

class UserPartnerPreferenceView_2(RedirectNotAuthenticatedUserMixin, FormView):
    template_name = 'User_profile_templates/privacy_setting_2.html'
    form_class = UserPartnerPreferenceForm

    def get_context_data(self, **kwargs: dict) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        interst_hobbies_list = []
        qualification_list = []
        locations_list = []
        LifestyleChoice_list = []
        interst_obj = Interests.objects.all()
        hobbies_obj = Hobbies.objects.all()
        qualification_obj = Qualifications.objects.all()
        locations_obj = Location.objects.all()
        LifestyleChoice_obj =  LifestyleChoice.objects.all()
        for Lifestyle in LifestyleChoice_obj:
            LifestyleChoice_list.append(Lifestyle.name)
        for interst in interst_obj:
            interst_hobbies_list.append(interst.interest)
        for hobbie in hobbies_obj:
            interst_hobbies_list.append(hobbie.hobby)
        for qualifiction in qualification_obj:
            qualification_list.append(qualifiction.qualification)
        for location in locations_obj:
            if location.address_details['state_district'] not in locations_list :
                locations_list.append(location.address_details['state_district'])
        print(interst_hobbies_list, qualification_list, locations_list)
        context['interest_hobbies_list'] = interst_hobbies_list
        context['qualifications_list'] = qualification_list
        context['location_list'] = locations_list
        context['LifestyleChoice_list'] = LifestyleChoice_list
        context['occupation'] = [occupation.job_title for occupation in Job_Details.objects.all()]
        return context

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        print(kwargs,"datas............!!!!!!!!!!!!!!11")
        return kwargs
    
    def form_valid(self, form: Any) -> HttpResponse:
        details = form.save(commit = True)
        print(details)
        return super().form_valid(form)
    

    def get_success_url(self) -> str:
        return redirect('privacy_setting_sec')

