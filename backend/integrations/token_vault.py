import requests
from config import config


AUTH0_DOMAIN = config.AUTH0_DOMAIN
AUTH0_CLIENT_ID = config.AUTH0_CLIENT_ID
AUTH0_CLIENT_SECRET = config.AUTH0_CLIENT_SECRET


def get_service_token(service, user_id):

    url = f"https://{AUTH0_DOMAIN}/oauth/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": service
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise Exception("Failed to retrieve token from vault")

    data = response.json()

    return data["access_token"]