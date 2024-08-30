import datetime
import random
from django.utils import timezone
from .models import OTP, costume_user


def generate_otp(user):
    otp = random.randint(1000, 9999)
    
    # Check if an OTP entry already exists for the user
    if OTP.objects.filter(user=user).exists():
        otp_data = OTP.objects.get(user=user)
        otp_data.otp_code = otp
        otp_data.created_at = timezone.now()  # Use Django's timezone utility
        otp_data.is_validated = False
        otp_data.save()
    else:
        OTP.objects.create(user=user, otp_code=otp, created_at=timezone.now())

    return otp


# Validate the OTP code 
def validate_otp(user_otp_code ):
        
        try:
            otp_data = OTP.objects.get(otp_code=user_otp_code)
            
            # Check if the OTP was already validated
            if otp_data.is_validated:
                message = "OTP already validated."
                return False, message
            
            # Check if the OTP was created within the last 1 minute
            time_difference = timezone.now() - otp_data.created_at
            if time_difference > datetime.timedelta(minutes=1):
                message = "OTP expired. Please request a new one."
                return False, message
            
            # If the OTP is valid and within time, return True
            otp_data.is_validated = True
            otp_data.save()

            # change user is_active to true
            user = otp_data.user
            user.is_active = True
            user.is_verified = True
            user.save()

            return True, "OTP is valid."
        
        except OTP.DoesNotExist:
            # If the OTP doesn't exist
            message = "Invalid OTP. Please try again."
            return False, message 

def send_otp(phone_number):
    pass