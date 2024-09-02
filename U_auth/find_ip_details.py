import ipapi
import threading
from .models import UserExtraDetails


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Get the first IP in the list
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def find_details(request):
    #get client ip address from get_client_ip function
    IP = get_client_ip(request)
    print(IP,"client ip adress...!!") #Debuging
    # get user ip details from ipapi
    # Fetch location details using ipapi
    location_data = ipapi.location(ip=IP, output='json')
    print(location_data, 'details..!!!!!!11')
    if location_data.get('error'):
        # Handle error in getting location data
        return {
            'error': True,
            'message': location_data.get('reason', 'Unable to retrieve location data.')
        }
    
                                                                   

