import requests


def upload_to_drive(user_context, params):

    token = user_context.get("drive_token")

    if not token:
        return {"error": "google drive not connected"}

    file_path = params.get("file_path")

    if not file_path:
        return {"error": "file path missing"}

    headers = {
        "Authorization": f"Bearer {token}"
    }

    files = {
        "file": open(file_path, "rb")
    }

    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"

    response = requests.post(url, headers=headers, files=files)

    return response.json()