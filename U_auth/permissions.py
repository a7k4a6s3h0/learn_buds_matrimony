from django.contrib import messages
import U_auth.permissions
import django.contrib
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from U_auth.models import (AdditionalDetails, costume_user, Job_Details, OTP, Relationship_Goals,
    UserPersonalDetails)

#...................................custom permission class...................................

'''Explanation:
1) test_func: This method checks if the user is authenticated. 
If they are, it returns False, preventing access to the view.

2) handle_no_permission: This method defines what happens if the test fails. 
In this case, it redirects the authenticated user to the home page (or any page you choose).

3) Usage in Views: The RedirectAuthenticatedUserMixin is applied to both the login and signup views, 
preventing logged-in users from accessing these pages.
'''

class RedirectAuthenticatedUserMixin(UserPassesTestMixin):
    def test_func(self):
        # This will return False if the user is authenticated, blocking access to the view.
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        # If the user is authenticated and tries to access the page like login or signup, redirect them
        return redirect(reverse_lazy('home'))  # Redirect to home page or any other page
    
class RedirectNotAuthenticatedUserMixin(UserPassesTestMixin):
    def test_func(self):
        # This will return True if the user is not authenticated, blocking access to the view.
        return self.request.user.is_authenticated
    
    def handle_no_permission(self):
        # If the user is not authenticated and tries to access the authendication need pages like home or signup, redirect them
        print(self.request.user,"in per..")

        return redirect(reverse_lazy('auth_page'))

class check_permissions:
    def __init__(self, get_response, user_email):
        self.get_response = get_response
        self.user_email = user_email
        self.user_obj = costume_user.objects.get(email=self.user_email)
        self.otp_obj = None
        self.model_dict = {}

        self.db_models_to_check = [(UserPersonalDetails, 'show_personaldetails_modal'), (Job_Details, 'show_jobdetails_modal'), (Relationship_Goals, 'show_relationmodel_modal'), (AdditionalDetails, 'show_additionaldetails_modal')]
        

    def check_user_authendicated(self):
        return self.get_response.user.is_authenticated

    def check_userexists(self):
        try:
            self.otp_obj = OTP.objects.get(user=self.user_obj)
            return True
        except OTP.DoesNotExist:
            return False

    def get_model(self):
        
            if self.check_userexists():
                print(self.otp_obj.is_validated)
                if not self.otp_obj.is_validated:
                    self.model_dict['status'] = False
                    self.model_dict['model'] = 'OTP'
                    return self.model_dict
                
                for model in self.db_models_to_check:
                    
                    if self.check_user_authendicated():

                        if not model[0].objects.filter(user=self.user_obj).exists():
                            self.model_dict['status'] = False
                            self.model_dict[model[1]] = True
                            return self.model_dict
                    else:
                        # messages.error(self.get_response, "user not audenticated...!!")
                        self.model_dict['status'] = False
                        self.model_dict['model'] = 'OTP'
                        return self.model_dict
                    

                # If all models exist
                self.model_dict['status'] = True
                self.model_dict['show_login_modal'] = True
                return self.model_dict
            
            else:
                return None