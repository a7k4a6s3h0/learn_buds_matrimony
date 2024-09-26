# adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .get_userPhonenumber import get_google_phone_number
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super(CustomSocialAccountAdapter, self).save_user(request, sociallogin, form=form)

        # Extract additional data from the Google response
        extra_data = sociallogin.account.extra_data
        print(extra_data,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # Get the access token
        access_token = sociallogin.token.token
        print(access_token,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        # Fetch phone number via People API
        phone_number = get_google_phone_number(access_token)
        print(phone_number, "new number....................")
        
        # # Get the full name (Google may return both name or given_name + family_name)
        # full_name = extra_data.get('name')
        # if not full_name:  # In case 'name' is not available, combine 'given_name' and 'family_name'
        #     full_name = f"{extra_data.get('given_name', '')} {extra_data.get('family_name', '')}".strip()
        
        # # Set the full name in the user or profile model
        # user.full_name = full_name

        # # Get phone number if available (Google provides it inside the `phoneNumbers` field)
        # phone_numbers = extra_data.get('phoneNumbers')
        # if phone_numbers and len(phone_numbers) > 0:
        #     phone_number_data = phone_numbers[0].get('value')  # First phone number
        #     user.profile.phone_number = phone_number_data  # Save phone number
        
        # # Optional: Extract country code from phone number (if needed)
        # if phone_number_data and phone_number_data.startswith('+'):
        #     user.profile.country_code = phone_number_data.split(' ')[0]  # Extract the country code

        # # Save user or profile with the new data
        # user.profile.save()
        return user
