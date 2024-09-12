import requests

def get_google_phone_number(access_token):
    url = 'https://people.googleapis.com/v1/people/me?personFields=phoneNumbers'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response JSON: {data}")
            phone_numbers = data.get('phoneNumbers', [])
            if phone_numbers:
                return phone_numbers[0].get('value')  # Return the first phone number
            else:
                print("No phone numbers found.")
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
    elif response.status_code == 401:
        print("Unauthorized: Check if the access token is valid or expired.")
    elif response.status_code == 403:
        print("Forbidden: Check API permissions and scopes.")
    else:
        print(f"Unexpected error: {response.status_code}")
    
    return None
