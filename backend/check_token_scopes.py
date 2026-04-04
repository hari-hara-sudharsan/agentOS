import requests

def check_token(access_token):
    print(f"Checking token starting with {access_token[:10]}...")
    url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        print(f"Scopes: {data.get('scope')}")
        print(f"Expires In: {data.get('expires_in')}")
        print(f"Email: {data.get('email')}")
    else:
        print(f"Failed to check token: {res.status_code} {res.text}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        check_token(sys.argv[1])
    else:
        # We need to get the token for the user from the backend
        print("Usage: python check_token_scopes.py <access_token>")
