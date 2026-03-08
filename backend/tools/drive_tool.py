from registry.tool_registry import tool_registry

import requests


def upload_to_drive(user_context, params):

    token = user_context.get("drive_token")

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