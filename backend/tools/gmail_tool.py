from registry.tool_registry import tool_registry
from integrations.integration_service import get_integration_token
import requests


def read_gmail(user_context, params):

    user_id = user_context["sub"]

    token = get_integration_token(
        user_id,
        "gmail"
    )

    if not token:
        return {"error": "gmail not connected"}

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": "gmail api error"}

    return response.json()


tool_registry.register("read_gmail", read_gmail)
