import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

def check_auth0():
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
    if res.status_code != 200:
        print(f"Failed to get management token: {res.text}")
        return
        
    mgmt_token = res.json().get("access_token")
    print(f"Successfully got Management Token!")
    
    users_url = f"https://{domain}/api/v2/users"
    res2 = requests.get(users_url, headers={"Authorization": f"Bearer {mgmt_token}"})
    
    if res2.status_code != 200:
        print(f"Failed to get users: {res2.status_code} {res2.text}")
    else:
        users = res2.json()
        print(f"Found {len(users)} users.")
        for u in users:
            print(f"User ID: {u.get('user_id')}")
            for identity in u.get('identities', []):
                print(f"  Connection: {identity.get('connection')}")
                access_token = identity.get('access_token')
                if access_token:
                    print(f"    Has access_token starting with: {access_token[:10]}...")
                    
                    # Test against Google Token Info API
                    test_url = f"https://oauth2.googleapis.com/tokeninfo?access_token={access_token}"
                    test_res = requests.get(test_url)
                    print(f"    Google Token Info Response: {test_res.status_code}")
                    print(f"    Google Details: {test_res.text}")
                else:
                    print(f"    NO access_token")

if __name__ == "__main__":
    check_auth0()
