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
from .forms import *
from django.views import View
import httpagentparser
from .find_ip_details import find_details
# Create your views here.

# def demo(request):
    # return render(request, 'base_files/base.html')

def login_view(request):
    return render(request, 'login.html')
def perdet_view(request):
    return render(request, 'personal details.html')
def jobst(request):
    return render(request, 'job status.html')
def jobd(request):
    return render(request, 'Job Details.html')
def jobd1(request):
    return render(request, 'Job Details2.html')
def relation(request):
    return render(request, 'Relationship.html')
def interest(request):
    return render(request, 'Interested.html')
def adddet(request):
    return render(request, 'Additional details.html')

def user_details(request):
    return render(request, 'User_profile_templates/user_pr_1.html')

def user_details_2(request):
    return render(request, 'User_profile_templates/user_pr_2.html')


def user_details_3(request):
    return render(request, 'User_profile_templates/user_pr_3.html')

def user_details_4(request):
    return render(request, 'User_profile_templates/user_pr_4.html')


def user_details_5(request):
    return render(request, 'User_profile_templates/user_pr_5.html')

def user_details_6(request):
    return render(request, 'User_profile_templates/user_pr_6.html')


def AuthPage(request):

    context = {
        'experance_level': ['Beginner', 'Intermediate', 'Expert'],
        'marital_status': ['Unmarried', 'Divorced']
    }
    return render(request, 'auth/auth.html',context)

def multiselect(request):
    return render(request, 'auth/MultiSelect.html')

def error_404(request):
    return render(request, 'Errors/404.html')


def error_403(request):
    return render(request, 'Errors/403.html')


# ................................backend code starting..............................................


class SignupView(FormView):
    
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
            if response_status is not None:
                print(response_status, "response_status...................!!!!!!!!!!!!!")  # Debugging
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

            print(self.get_device_name(self.request))
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

class LoginView(FormView):

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

    def get(self, request: HttpRequest, *args: str, **kwargs: dict) -> HttpResponse:

        return super().get(request, *args, **kwargs)  # Call the parent's get method to render the form

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

class ForgotPassword(FormView):
    template_name = 'auth/auth.html'
    form_class = ForgotPasswordForm
    # success_url = reverse_lazy('check_otp')

    def form_valid(self, form):
        password = form.cleaned_data['current_password']
        current_user = costume_user.objects.get(password=password)
        if check_password(password, current_user.password):
            messages.error(self.request, "Not Found..!!!")
        else:
            current_user.set_password(password)  # Set the new password (Django will hash it)
            current_user.save()  # Save the updated user
            messages.success(self.request, "Password changed successfully.")

        return super().form_valid(form)
    
    def get_success_url(self):
        # sending message for otp useage
        messages.success(self.request, "Verification for Password Changing..!!")
        # Redirect to a success URL after form submission
        return reverse_lazy('auth_page')
    
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