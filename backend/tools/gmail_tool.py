import requests


def read_gmail(user_context, params):

    token = user_context.get("gmail_token")

    if not token:
        return {"error": "gmail not connected"}

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": "gmail api failed"}

    return response.json()