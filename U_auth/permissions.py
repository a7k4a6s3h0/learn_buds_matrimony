import U_auth.permissions
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy

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
