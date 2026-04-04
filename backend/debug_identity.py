import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_management_token():
    domain = os.getenv("AUTH0_DOMAIN")
    client_id = os.getenv("AUTH0_CLIENT_ID")
    client_secret = os.getenv("AUTH0_CLIENT_SECRET")
    url = f"https://{domain}/oauth/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": f"https://{domain}/api/v2/",
        "grant_type": "client_credentials"
    }
    res = requests.post(url, json=payload)
    return res.json().get("access_token")

def debug_user(user_id):
    token = get_management_token()
    domain = os.getenv("AUTH0_DOMAIN")
    url = f"https://{domain}/api/v2/users/{user_id}"
    res = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if res.status_code == 200:
        data = res.json()
        print(f"User: {data.get('email')} ({data.get('user_id')})")
        for identity in data.get("identities", []):
            print(f"\nIdentity: {identity.get('connection')}")
            print(f"  - Provider: {identity.get('provider')}")
            print(f"  - Is Linked: {identity.get('isSocial')}")
            # Do NOT print the real tokens for security, just check if they exist
            print(f"  - Access Token Present: {'Yes' if 'access_token' in identity else 'No'}")
            print(f"  - Refresh Token Present: {'Yes' if 'refresh_token' in identity else 'No'}")
            print(f"  - Connection: {identity.get('connection')}")
    else:
        print(f"Failed to fetch user: {res.status_code} {res.text}")

if __name__ == "__main__":
    # User ID from the logs
    debug_user("google-oauth2|115860559711395850790")
