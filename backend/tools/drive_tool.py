from registry.tool_registry import tool_registry
from integrations.integration_service import get_integration_token

import requests


from security.auth0_client import check_mfa_and_consent

def upload_to_drive(user_context, params):
    check_mfa_and_consent(user_context, params)

    token = get_integration_token(
        user_context,
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