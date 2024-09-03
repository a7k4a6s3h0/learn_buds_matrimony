from django.shortcuts import render

#profile display imports :
from django.shortcuts import render, get_object_or_404
from U_auth.models import costume_user, UserPersonalDetails, Job_Details, AdditionalDetails, Pictures, Hobbies, Interests, Relationship_Goals

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


def user_send_pg(request):
    return render(request, 'send.html')


def user_accept_pg(request):
    return render(request, 'accept.html')


def user_reject_pg(request):
    return render(request, 'reject.html')


def user_recieved_pg(request):
    return render(request, 'recieved.html')

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