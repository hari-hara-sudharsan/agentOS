from registry.tool_registry import tool_registry
from integrations.token_vault import get_service_token
import requests


def read_gmail(user_context, params):

    user_id = user_context["sub"]

    token = get_service_token(
        "https://gmail.googleapis.com",
        user_id
    )

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"

    response = requests.get(url, headers=headers)

    return response.json()


tool_registry.register("read_gmail", read_gmail)
