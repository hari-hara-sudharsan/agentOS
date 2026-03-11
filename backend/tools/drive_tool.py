from registry.tool_registry import tool_registry
from integrations.integration_service import get_integration_token

import requests


def upload_to_drive(user_context, params):

    user_id = user_context["sub"]

    token = get_integration_token(
        user_id,
        "drive"
    )

    if not token:
        return {"error": "drive not connected"}

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