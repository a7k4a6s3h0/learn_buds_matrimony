import math
from django.shortcuts import get_object_or_404
from U_auth.models import UserPersonalDetails

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of Earth in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    
    return distance

def find_distance(logged_user, other_user):
    logged_user_personal = get_object_or_404(UserPersonalDetails, user=logged_user)
    other_user_personal = get_object_or_404(UserPersonalDetails, user=other_user)
    
    lat1 = logged_user_personal.user_location.latitude
    lon1 = logged_user_personal.user_location.longitude
    lat2 = other_user_personal.user_location.latitude
    lon2 = other_user_personal.user_location.longitude
    
    distance = haversine(lat1, lon1, lat2, lon2)
    
    return distance

def sort_users_by_distance(logged_user, users):
    # Calculate distances
    distances = [(other_user, find_distance(logged_user, other_user)) for other_user in users]
    
    # Sort by distance (from lowest to highest)
    sorted_distances = sorted(distances, key=lambda x: x[1])
    
    return sorted_distances