
from django.shortcuts import redirect, render

#profile display imports :
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from U_auth.models import costume_user, UserPersonalDetails, Job_Details, AdditionalDetails, Pictures, Hobbies, Interests, Relationship_Goals

from U_auth.models import costume_user
from .models import InterestRequest
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q  # Import Q for complex queries
from django.contrib import messages
# Create your views here.
def demo_pr(request, user_id):
    # Fetch the user and related data
    user = get_object_or_404(costume_user, id=user_id)
    personal_details = get_object_or_404(UserPersonalDetails, user=user)
    additional_details = get_object_or_404(AdditionalDetails, user=user)
    pictures = Pictures.objects.filter(user=personal_details)
    
    # Use the correct relationship to UserPersonalDetails
    hobbies = Hobbies.objects.filter(userpersonaldetails=personal_details)
    interests = Interests.objects.filter(userpersonaldetails=personal_details)
    
    # Create context to pass to the template
    context = {
        'user': user,
        'personal_details': personal_details,
        'additional_details': additional_details,
        'pictures': pictures,
        'hobbies': hobbies,
        'interests': interests,
        'family_type': additional_details.family_type,
        'family_name': additional_details.family_name,
        'father_name': additional_details.father_name,
        'father_occupation': additional_details.father_occupation,
        'mother_name': additional_details.mother_name,
        'mother_occupation': additional_details.mother_occupation,
        'total_siblings': additional_details.total_siblings,
        'total_siblings_married': additional_details.total_siblings_married,
    }

    # Render the template with the context
    return render(request, 'users_pr_view.html', context)




def messages_pg(request):
    return render(request, 'messages.html')


# def user_send_pg(request):
#     return render(request, 'send.html')


# def user_accept_pg(request):
#     return render(request, 'accept.html')


# def user_reject_pg(request):
#     return render(request, 'reject.html')


# def user_recieved_pg(request):
#     return render(request, 'recieved.html')

def user_chat_pg(request):
    return render(request, 'col_chat.html')


def user_shortlist_pg(request):
    return render(request, 'shortlist.html')

def user_shortlisted_pg(request):
    return render(request, 'shortlisted_by.html')

def user_contacted_pg(request):
    return render(request, 'contacted.html')

def user_viewed_pg(request):
    return render(request, 'pr_viewed.html')


class SendRequestView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        sender = request.user
        receiver = get_object_or_404(costume_user, id=self.kwargs['pk'])
        
        # Check if a request already exists
        existing_request = InterestRequest.objects.filter(sender=sender, receiver=receiver).exists()
        
        if existing_request:
            messages.warning(request, "You have already sent a request to this user.")
        else:
            try:
                InterestRequest.objects.create(sender=sender, receiver=receiver)
                messages.success(request, "Interest request sent successfully!")
            except Exception as e:
                messages.error(request, f"Failed to send interest request: {str(e)}")
            
        return redirect(reverse_lazy('sented_request'))

class SentedRequestView(LoginRequiredMixin,ListView):
    model = InterestRequest
    template_name = 'send.html'
    context_object_name = 'sent_requests'

    def get_queryset(self):
        return InterestRequest.objects.filter(sender=self.request.user)
    
class ReceivedRequestView(LoginRequiredMixin,ListView):
    model = InterestRequest
    template_name = 'received.html'
    context_object_name = 'received_requests'
    
    def get_queryset(self):
        return InterestRequest.objects.filter(receiver=self.request.user)

class RequestHandleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        interest_request = get_object_or_404(InterestRequest, id=self.kwargs['pk'], receiver=request.user)
        action = self.kwargs.get('action')  # This fetches the value of 'action' from the URL ('accept' or 'reject').

        if action == 'accept':  # If 'action' is 'accept'
            interest_request.status = 'accepted'  # Set the request's status to 'accepted'
        elif action == 'reject':  # Otherwise, if 'action' is 'reject'
            interest_request.status = 'rejected'  # Set the request's status to 'rejected'

        interest_request.save()
        return redirect(reverse_lazy('received_requests'))

class AcceptedRequestView(LoginRequiredMixin, ListView):
    model = InterestRequest
    template_name = 'accept.html'
    context_object_name = 'accepted_requests'

    def get_queryset(self):
        return InterestRequest.objects.filter(
            Q(sender=self.request.uesr, status='accepted')|
            Q(receiver=self.request.user, status='accepted')
        )

class RejectedRequestView(LoginRequiredMixin, ListView):
    model = InterestRequest
    template_name = 'reject.html'
    context_object_name = 'rejected_requests'

    def get_queryset(self):
        return InterestRequest.objects.filter(
            Q(sender=self.request.uesr, status='rejected')|
            Q(receiver=self.request.user, status='rejected')
        )

