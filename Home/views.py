from django.shortcuts import render,redirect
from django.views.generic import TemplateView,ListView
from U_auth.permissions import RedirectAuthenticatedUserMixin, RedirectNotAuthenticatedUserMixin
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from U_auth.models import *
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.messages.views import SuccessMessageMixin
import math
from .find_distance import find_distance,sort_users_by_distance

# Create your views here.

class Home(RedirectNotAuthenticatedUserMixin,SuccessMessageMixin, ListView):
    model = UserPersonalDetails
    template_name = 'Home/home.html'
    context_object_name = 'users'
    success_message = "This is a success message."

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()  
        filter_value = self.request.GET.get('filter', 'Location')
        loged_user = get_object_or_404(UserPersonalDetails, user=user)
        # Apply filters based on the filter_value
        if filter_value == 'Location':
            queryset = queryset.filter(user__user_details__user_location=loged_user.user_location)
        elif filter_value == 'Designation':
            job_details = Job_Details.objects.filter(user=loged_user.user).first()
            if job_details:
                queryset = queryset.filter(user__job_details__designation=job_details.designation)

        elif filter_value == 'Qualification':
            user_qualifications = loged_user.qualifications.all()  # This returns a queryset of qualifications
            queryset = queryset.filter(qualifications__in=user_qualifications)
            # Exclude users based on gender preference
        if loged_user.gender == 'M':
            queryset = queryset.exclude(Q(user__user_details__gender='M') | Q(user__user_details__gender='O'))
        elif loged_user.gender == 'F':
            queryset = queryset.exclude(Q(user__user_details__gender='F') | Q(user__user_details__gender='O'))
        elif loged_user.gender == 'O':
            queryset = queryset.all()

        # Exclude the logged-in user from the queryset
        queryset = queryset.exclude(user=user)
        for i in queryset:
            print(i.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        try:
            user_details = UserPersonalDetails.objects.get(user=user)
            context['user_details'] = user_details
        except UserPersonalDetails.DoesNotExist:
            context['user_details'] = None
        return context




class Matches(LoginRequiredMixin, TemplateView):
    template_name = 'Home/matches.html'
    
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not isinstance(user, costume_user):
            return redirect('home')  # URL where non-authenticated users should go
        # Try to get the user's partner preferences
        try:
            PartnerPreference.objects.get(user=user)
        except PartnerPreference.DoesNotExist:
            # Inform the user that preferences are missing and redirect
            return redirect('home') 
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        sorted_users = None
        
        if not isinstance(user, costume_user):
            context['matches'] = []
            context['match_count'] = 0
            return context

        
        user_preference = get_object_or_404(PartnerPreference, user=user)
        user_personal = get_object_or_404(UserPersonalDetails, user=user)
        preferred_gender = user_preference.preferred_gender


        # Initial QuerySet based on preferred gender
        users = costume_user.objects.exclude(id=user.id).exclude(is_superuser=True)
        users = users.select_related('user_details').filter(user_details__gender=preferred_gender)
        # Apply Sorting
        if 'newest_member' in self.request.GET:
            users = users.order_by('-date_joined')
        elif 'last_active' in self.request.GET:
            users = users.order_by('-last_login')
        # Inside your view or method

        elif 'distance' in self.request.GET:
            # Order by some criteria, if needed
            sorted_users = sort_users_by_distance(user, users)
            # Iterate over sorted list and process
            # for other_user, distance in sorted_users:
            #     print(f"Distance to user {other_user}: {distance:.2f}km")

        elif 'age' in self.request.GET:
            users = users.order_by('-user_details__age')
        elif 'gender' in self.request.GET:
            users = users.order_by('-user_details__gender')
        elif 'location' in self.request.GET:
            users = users.order_by('-country_details')

        # Apply Filtering
        if 'interests/hobbies' in self.request.GET:
            try:
                # Get personal details of the logged-in user
                user_personal = UserPersonalDetails.objects.get(user=self.request.user)
                user_hobbies = set(user_personal.hobbies.values_list('hobby', flat=True))
                user_interests = set(user_personal.interests.values_list('interest', flat=True))

                # Get the IDs of users that match the criteria
                matching_users = UserPersonalDetails.objects.filter(
                    user__in=users,
                    hobbies__hobby__in=user_hobbies,
                    interests__interest__in=user_interests
                ).distinct()

                selected_ids = set(matching_users.values_list('user', flat=True))
                users = users.filter(id__in=selected_ids)
            except UserPersonalDetails.DoesNotExist:
                pass

        if 'languages_spoken' in self.request.GET:
            user_language = user.user_language
            users = users.filter(user_language=user_language)

        if 'relationship_goals' in self.request.GET:
            user_goal = get_object_or_404(Relationship_Goals, user=user)
            matching_users = Relationship_Goals.objects.filter(
                user__in=users,
                is_short=user_goal.is_short,
                is_long=user_goal.is_long,
            )
            selected_ids = set(matching_users.values_list('user', flat=True))
            users = users.filter(id__in=selected_ids)

        matches = [

        ]

        for other_user in users:
            score, max_score = self.calculate_match_score(user, other_user)
            distance = find_distance(user,other_user)
            matches.append({
                'user': other_user,
                'score': score,
                'max_score': max_score,
                'distance': distance,
                
            })
            
        # matches = sorted(matches, key=lambda x: x['score'], reverse=True)
        context['match_count'] = users.count()
        context['matches'] = matches
        context['sorted_users'] = sorted_users
        return context

    def calculate_match_score(self, user, other_user):
        score = 0
        max_score = 100
        try:
            # Retrieve the partner preferences
            user_preference = PartnerPreference.objects.get(user=user)
            other_user_preference = PartnerPreference.objects.get(user=other_user)

            # Retrieve other details
            other_users_additionals = AdditionalDetails.objects.get(user=other_user)
            other_user_personal = UserPersonalDetails.objects.get(user=other_user)
            other_user_jobs = Job_Details.objects.get(user=other_user)

            # Gender Preference
            if user_preference.preferred_gender == other_user_personal.gender:
                score += 10

            # Age Range
            if user_preference.age_min <= other_user_personal.age <= user_preference.age_max:
                score += 10

            # Location Preference
            preferred_locations = [location for location in user_preference.preferred_location.all()]

            if str(other_user.country_details) in preferred_locations:
                score += 10

            # Education Level
            if user_preference.education_level == other_user_personal.qualifications:
                score += 10

            # # Hobbies
            user_hobbies = set(user_preference.interests_hobbies.values_list('name', flat=True))
            other_user_hobbies = set(hobby.hobby for hobby in other_user_personal.hobbies.all())
            common_hobbies = user_hobbies.intersection(other_user_hobbies)
            score += min(len(common_hobbies) * 5, len(user_hobbies) * 5)

            # # Interests
            user_interests = set(user_preference.interests_hobbies.values_list('name', flat=True))
            other_user_interests = set(Interests.objects.filter(userpersonaldetails=other_user_personal).values_list('interest', flat=True))
            common_interests = user_interests.intersection(other_user_interests)
            score += min(len(common_interests) * 5, len(user_interests) * 5)

            # # Lifestyle Choices
            user_lifestyle_choices = set(user_preference.lifestyle_choices.all())
            other_user_lifestyle_choices = set(other_user_preference.lifestyle_choices.all())
            common_lifestyle_choices = user_lifestyle_choices.intersection(other_user_lifestyle_choices)
            score += min(len(common_lifestyle_choices) * 5, len(user_lifestyle_choices) * 5)

            # Religion
            if user_preference.religion == other_users_additionals.religion:
                score += 10

            # Height
            if user_preference.height_min <= other_users_additionals.height <= user_preference.height_max:
                score += 10

            # Weight
            if user_preference.weight_min <= other_users_additionals.weight <= user_preference.weight_max:
                score += 10

            # Occupation
            if user_preference.occupation == other_user_jobs.designation:
                score += 10

        except (PartnerPreference.DoesNotExist, AdditionalDetails.DoesNotExist, 
                UserPersonalDetails.DoesNotExist, Job_Details.DoesNotExist):
            pass

        # Ensure the score does not exceed the maximum
        score = min(score, max_score)
        percentage = (score / max_score) * 100
        return score, percentage





class Qualification(TemplateView):
    template_name='Home/qualification.html'

class Loaction(TemplateView):
    template_name='Home/loaction.html'


class Designation(TemplateView):
    template_name='Home/designation.html'


class FilterPrifles(TemplateView):
    template_name='Home/filter.html'

# class error404(TemplateView):
#     template_name='Home/error.html'    

    