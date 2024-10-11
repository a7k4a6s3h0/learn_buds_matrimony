from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import FormView, ListView
from django.urls import reverse_lazy
from .forms import AdminLoginForm
from U_auth.permissions import *
from U_auth.models import UserPersonalDetails, Location
from .forms import UserPersonalDetailsForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class AdminHomeView(CheckSuperUserNotAuthendicated, TemplateView):
    template_name = "admin_home.html"

class UserManagementView(ListView):
    model = UserPersonalDetails
    template_name = 'user_manage.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        # Use select_related to optimize query and reduce DB hits
        return UserPersonalDetails.objects.select_related('user', 'user_location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Get the pagination object and handle the page request
            page_number = self.request.GET.get('page')
            paginator = Paginator(self.get_queryset(), self.paginate_by)
            page_obj = paginator.get_page(page_number)
            context['page_obj'] = page_obj
        except (PageNotAnInteger, EmptyPage):
            # If page is not an integer, deliver first page.
            # If page is out of range, deliver last page of results.
            context['page_obj'] = paginator.page(1 if isinstance(PageNotAnInteger) else paginator.num_pages)
        except Exception as e:
            # Handle unexpected exceptions (optional)
            context['error_message'] = f"An error occurred: {str(e)}"
        
        return context

  
@method_decorator(csrf_exempt, name='dispatch')
class BlockUnblockUserView(View):
    
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('userId')
        is_active = request.POST.get('isActive') == "true"  # Ensure proper boolean conversion
        block_reason = request.POST.get('blockReason', '')

        try:
            user_details = UserPersonalDetails.objects.get(id=user_id)
            user = user_details.user  # Get the related User instance
            
            # Update the user's active status
            user.is_active = is_active
            user_details.is_blocked = not is_active  # Reflect if the user is blocked or not

            # If the user is blocked, store the block reason
            if not is_active:
                user_details.block_reason = block_reason
            else:
                user_details.block_reason = None  # Clear the block reason when unblocked

            user.save()  # Save the related User model
            user_details.save()  # Save the UserPersonalDetails model

            print(f"User {user_id} block status: {user_details.is_blocked}, reason: {user_details.block_reason}")


            return JsonResponse({'status': 'success'})

        except UserPersonalDetails.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    
    

class AdminLoginView(CheckSuperUserAuthendicated ,FormView):
    template_name = 'admin_login.html'
    form_class = AdminLoginForm
    success_url = reverse_lazy('admin_home')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')

        user = authenticate(email=email, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Invalid credentials')
            return self.form_invalid(form)
    
class AdminLogoutView(CheckSuperUserNotAuthendicated ,TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('admin_login')

class FinancialManagement(TemplateView):
    template_name = "financial_management.html"


class NotifcationManagement(TemplateView):
    template_name = "notification_management.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['select_options'] = ['User 1', 'User 2', 'User 3']
        # Add other context variables if needed
        return context

def add_user(request):
    if request.method == 'POST':
        form = UserPersonalDetailsForm(request.Post, request.Files)
        if form.is_valid():
            form.save()
            messages.success(request, 'User added successfully!')
            return redirect('usr_mng')
        else:
            form = UserPersonalDetailsForm()
        return render(request, 'matrimony_admin/user_management.html', {'form': form})

def edit_user(request, pk):
    user_details = get_object_or_404(UserPersonalDetails, pk=pk)
    if request.method == 'POST':
        form = UserPersonalDeatilsForm(request.POST, request.FILES, instance=user_details)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('usr_mng')
    else:
        form = UserPersonalDetailsForm(instance=user_details)
    return render(request, 'matrimony_admin/user_management.html', {'form': form, 'user': user_details})

