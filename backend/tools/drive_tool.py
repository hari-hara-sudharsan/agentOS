from registry.tool_registry import tool_registry
from integrations.token_vault import get_service_token

import requests


def upload_to_drive(user_context, params):

    user_id = user_context["sub"]

    token = get_service_token(
        "https://www.googleapis.com",
        user_id
    )

    file_path = params.get("file_path")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    files = {
        "file": open(file_path, "rb")
    }

    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"

    response = requests.post(url, headers=headers, files=files)

    return response.json()


tool_registry.register("upload_to_drive", upload_to_drive)