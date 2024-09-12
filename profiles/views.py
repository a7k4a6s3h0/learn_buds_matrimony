import json
from django.http import JsonResponse
from django.shortcuts import redirect, render

#profile display imports :
from django.shortcuts import render, get_object_or_404
from U_auth.models import *
from django.http import JsonResponse

#for  interest-request
from .models import InterestRequest,Shortlist
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q  # Import Q for complex queries
from django.contrib import messages
from U_auth.permissions import RedirectNotAuthenticatedUserMixin
from typing import Any
from django.views.generic import TemplateView
from django.contrib import messages
from django.urls import reverse, reverse_lazy


# Create your views here.

class UserProfileView(TemplateView):
    template_name = 'users_pr_view.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id', None)
        if user_id:
            user = costume_user.objects.get(id=user_id)
            user_details = UserPersonalDetails.objects.get(user=user) 
            additional_details = AdditionalDetails.objects.get(user=user)
            pictures = Pictures.objects.filter(user=user_details)
            context['user'] = user
            context['user_details'] = user_details
            context['additional_details'] = additional_details
            context['pictures'] = pictures
            context['user'] = user
            return context


#Interest request View
class SendRequestView(RedirectNotAuthenticatedUserMixin, View):
    def post(self, request, *args, **kwargs):
        sender = request.user
        receiver = get_object_or_404(costume_user, id=self.kwargs['pk'])
        
        existing_request = InterestRequest.objects.filter(sender=sender, receiver=receiver).exists()
        
        if existing_request:
            messages.warning(request, "You have already sent a request to this user.")
            return redirect(reverse('profile', kwargs={'user_id': receiver.id}))
        else:
            try:
                InterestRequest.objects.create(sender=sender, receiver=receiver)
                messages.success(request, "Interest request sent successfully!")
                return redirect(reverse_lazy('sented_request'))
            except Exception as e:
                messages.error(request, f"Failed to send interest request: {str(e)}")
                return redirect(reverse('profile', kwargs={'user_id': receiver.id}))
            
        
class SentedRequestView(RedirectNotAuthenticatedUserMixin,ListView):
    model = InterestRequest
    template_name = 'send.html'
    context_object_name = 'sent_requests'
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = InterestRequest.objects.filter(sender=self.request.user, status="pending").order_by("-created_at")
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(receiver__username__icontains=search_query) |
                Q(receiver__first_name__icontains=search_query) |
                Q(receiver__user_details__bio__icontains=search_query)
            )
        return queryset
    
class ReceivedRequestView(RedirectNotAuthenticatedUserMixin,ListView):
    model = InterestRequest
    template_name = 'received.html'
    context_object_name = 'received_requests'
    
    def get_queryset(self):
        queryset = InterestRequest.objects.filter(receiver=self.request.user, status="pending").order_by("-created_at")
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(sender__username__icontains=search_query) |
                Q(sender__first_name__icontains=search_query) |
                Q(sender__user_details__bio__icontains=search_query)
            )
        return queryset

class HandleRequestView(RedirectNotAuthenticatedUserMixin, View):
    def post(self, request, *args, **kwargs):
        interest_request = get_object_or_404(InterestRequest, id=self.kwargs['pk'], receiver=request.user)
        action = self.kwargs.get('action')  # This fetches the value of 'action' from the URL ('accept' or 'reject').
        
        if action == 'accept':  # If 'action' is 'accept'
            interest_request.status = 'accepted'  # Set the request's status to 'accepted'
            messages.success(request, "Interest request has accepted successfully!")
        elif action == 'reject':  # Otherwise, if 'action' is 'reject'
            interest_request.status = 'rejected'  # Set the request's status to 'rejected'
            messages.success(request, "Interest request has rejected successfully!")

        interest_request.save()
        return redirect(reverse_lazy('received_request'))

class AcceptedRequestView(RedirectNotAuthenticatedUserMixin, ListView):
    model = InterestRequest
    template_name = 'accept.html'
    context_object_name = 'accepted_requests'
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = InterestRequest.objects.filter(
            Q(sender=self.request.user, status='accepted')|
            Q(receiver=self.request.user, status='accepted')
        )
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(sender__username__icontains=search_query) |
                Q(sender__first_name__icontains=search_query) |
                Q(sender__user_details__bio__icontains=search_query) |
                Q(receiver__username__icontains=search_query) |
                Q(receiver__first_name__icontains=search_query) |
                Q(receiver__user_details__bio__icontains=search_query)
            )
        return queryset
    

class RejectedRequestView(RedirectNotAuthenticatedUserMixin, ListView):
    model = InterestRequest
    template_name = 'reject.html'
    context_object_name = 'rejected_requests'
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = InterestRequest.objects.filter(
            Q(sender=self.request.user, status='accepted')|
            Q(receiver=self.request.user, status='accepted')
        )
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(sender__username__icontains=search_query) |
                Q(sender__first_name__icontains=search_query) |
                Q(sender__user_details__bio__icontains=search_query) |
                Q(receiver__username__icontains=search_query) |
                Q(receiver__first_name__icontains=search_query) |
                Q(receiver__user_details__bio__icontains=search_query)
            )
        return queryset
class DeleteRequestView(RedirectNotAuthenticatedUserMixin,View):
    def post (self, request, *args, **kwargs):
        interest_request = get_object_or_404(InterestRequest, sender= request.user, id=self.kwargs['pk'])

        try:
            interest_request.delete()
            messages.success(request,"Interest request deleted successfully!")
        except Exception as e:
            messages.error(request, f"Failed to delete interest request: {str(e)}")
        return redirect(reverse('sented_request'))


#shortlist view
class ShortlistView(LoginRequiredMixin, ListView):
    model = Shortlist
    template_name = 'shortlist.html'
    context_object_name = 'shortlist'
    ordering = ["-created at"]

    def get_queryset(self):
        return Shortlist.objects.filter(user=self.request.user)

class AddToShortlistView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        shortlisted_user = get_object_or_404(costume_user, id=self.kwargs['user_id'])
        user = request.user

        # Check if the user is already in the shortlist
        if Shortlist.objects.filter(user=user, shortlisted_user=shortlisted_user).exists():
            messages.warning(request, "You have already shortlisted this user.")
            return redirect(reverse('profile', kwargs={'user_id': shortlisted_user.id}))
        else:
            Shortlist.objects.create(user=user, shortlisted_user=shortlisted_user)
            messages.success(request, "User successfully added to your shortlist.")
            return redirect(reverse('shortlist'))

       
class RemoveFromShortlistView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        shortlist_entry = get_object_or_404(Shortlist, user=request.user, shortlisted_user_id=self.kwargs['user_id'])

        # try:
        shortlist_entry.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'User removed from your shortlist.'})
        else:
            messages.success(request, "User removed from your shortlist.")
            return redirect(reverse('shortlist'))
        # except Exception as e:
        #     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        #         return JsonResponse({'status': 'error', 'message': f'Error removing user: {str(e)}'})
        #     else:
        #         messages.error(request, f"Error removing user: {str(e)}")
      
        return redirect(reverse('shortlist'))

class ShortlistByView(LoginRequiredMixin, ListView):
    model = Shortlist
    template_name = 'shortlisted_by.html'
    context_object_name = 'shortlist_by'
    ordering = ["-created at"]

    def get_queryset(self):
        return Shortlist.objects.filter(shortlisted_user=self.request.user)
