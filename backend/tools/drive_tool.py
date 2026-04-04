from registry.tool_registry import tool_registry
from integrations.integration_service import get_integration_token
from security.auth0_client import check_mfa_and_consent
import requests
import os
import json


def upload_to_drive(user_context, params):
    """Upload a file to Google Drive. Requires step-up auth."""
    check_mfa_and_consent(user_context, params, tool="upload_to_drive")

    token = get_integration_token(user_context, "drive")

    if not token:
        return {
            "error": "drive_not_connected",
            "message": "Google Drive is not connected. Please authorize Drive access.",
            "steps": [
                "1. Go to the Integrations page",
                "2. Click 'Authorize Vault Access' on the Drive card",
                "3. Allow Drive permissions in the Google consent screen",
                "4. Try your request again"
            ]
        }

    if token == "auth0-vault-linked":
        return {
            "error": "drive_token_not_resolved",
            "message": "Drive integration is linked but token could not be resolved. Please reconnect.",
            "steps": [
                "1. Go to the Integrations page",
                "2. Click 'Disconnect' on Drive",
                "3. Click 'Authorize Vault Access' again"
            ]
        }

    file_path = params.get("file_path")
    
    if not file_path:
        return {
            "error": "missing_file_path",
            "message": "No file path provided. Please specify which file to upload.",
            "example": "Upload file C:/Users/Documents/report.pdf to Drive"
        }
    
    # Check if file exists
    if not os.path.exists(file_path):
        return {
            "error": "file_not_found",
            "message": f"File not found: {file_path}",
            "steps": ["Please check the file path and try again"]
        }

    file_name = os.path.basename(file_path)
    
    # Prepare metadata
    metadata = {
        "name": file_name
    }
    
    # Add folder_id if specified
    if params.get("folder_id"):
        metadata["parents"] = [params.get("folder_id")]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        with open(file_path, "rb") as f:
            # Use multipart upload
            files = {
                "metadata": (None, json.dumps(metadata), "application/json"),
                "file": (file_name, f)
            }
            
            url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
            print(f"DEBUG: Uploading {file_name} to Google Drive")
            
            response = requests.post(url, headers=headers, files=files)
    except Exception as e:
        return {
            "error": "file_read_error",
            "message": f"Could not read file: {str(e)}"
        }

    if response.status_code == 401:
        # Token expired
        try:
            from database.db import SessionLocal
            from database.models import Integration
            db = SessionLocal()
            db.query(Integration).filter(
                Integration.user_id == user_context["sub"],
                Integration.service == "drive"
            ).delete()
            db.commit()
            db.close()
        except:
            pass
        return {
            "error": "drive_token_expired",
            "message": "Your Drive access token has expired. Please reconnect.",
            "steps": [
                "1. Go to the Integrations page",
                "2. Click 'Authorize Vault Access' on Drive"
            ]
        }

    if response.status_code == 403:
        return {
            "error": "drive_permission_denied",
            "message": "Permission denied. Make sure you granted drive.file scope.",
            "details": response.text
        }

    if response.status_code not in [200, 201]:
        return {
            "error": "drive_api_error",
            "message": f"Drive API error: {response.status_code}",
            "details": response.text
        }

    result = response.json()
    return {
        "status": "success",
        "message": f"✅ File '{file_name}' uploaded successfully!",
        "file_id": result.get("id"),
        "file_name": result.get("name"),
        "mime_type": result.get("mimeType")
    }


def list_drive_files(user_context, params):
    """List files from Google Drive."""
    token = get_integration_token(user_context, "drive")
    
    print(f"DEBUG: list_drive_files - token type: {type(token)}, token: {str(token)[:50] if token else 'None'}...")

    if not token:
        return {
            "error": "drive_not_connected",
            "message": "Google Drive is not connected.",
            "steps": [
                "1. Go to the Integrations page",
                "2. Click 'Authorize Vault Access' on the Drive card",
                "3. Complete Google OAuth and allow Drive permissions"
            ]
        }

    if token == "auth0-vault-linked":
        return {
            "error": "drive_token_not_resolved", 
            "message": "Drive is linked but token couldn't be resolved. Please reconnect.",
            "steps": [
                "1. Go to Integrations page",
                "2. Disconnect Drive",
                "3. Reconnect and authorize again"
            ]
        }

    headers = {"Authorization": f"Bearer {token}"}
    
    # Build query
    query_params = {
        "pageSize": params.get("limit", 10),
        "fields": "files(id, name, mimeType, modifiedTime, size)"
    }
    
    # Filter by folder if specified
    if params.get("folder_id"):
        query_params["q"] = f"'{params.get('folder_id')}' in parents"
    
    # Filter by search term
    if params.get("search"):
        search_q = f"name contains '{params.get('search')}'"
        if query_params.get("q"):
            query_params["q"] += f" and {search_q}"
        else:
            query_params["q"] = search_q

    url = "https://www.googleapis.com/drive/v3/files"
    print(f"DEBUG: Drive API request - URL: {url}, params: {query_params}")
    print(f"DEBUG: Token being used (first 20 chars): {token[:20] if token else 'None'}...")
    response = requests.get(url, headers=headers, params=query_params)
    print(f"DEBUG: Drive API response - status: {response.status_code}, body: {response.text[:500]}")

    if response.status_code == 401:
        # Token expired - purge it
        try:
            from database.db import SessionLocal
            from database.models import Integration
            db = SessionLocal()
            db.query(Integration).filter(
                Integration.user_id == user_context["sub"],
                Integration.service == "drive"
            ).delete()
            db.commit()
            db.close()
        except:
            pass
        return {
            "error": "drive_token_expired", 
            "message": "Your Drive access token has expired. Please reconnect.",
            "steps": ["Go to Integrations and click 'Authorize Vault Access' on Drive"]
        }
    
    if response.status_code == 403:
        error_detail = response.text
        print(f"DEBUG: Drive 403 error: {error_detail}")
        return {
            "error": "drive_permission_denied",
            "message": "Permission denied. Make sure you granted Drive file access.",
            "details": error_detail,
            "steps": [
                "1. Go to Integrations page",
                "2. Disconnect and reconnect Drive",
                "3. Make sure to allow file access in the Google consent screen"
            ]
        }
    
    if response.status_code != 200:
        error_detail = response.text
        print(f"DEBUG: Drive API error {response.status_code}: {error_detail}")
        return {
            "error": "drive_api_error", 
            "message": f"Drive API returned error {response.status_code}",
            "details": error_detail
        }

    files = response.json().get("files", [])
    
    if not files:
        return {"message": "No files found in Drive.", "files": []}
    
    file_list = []
    for f in files:
        file_list.append({
            "id": f.get("id"),
            "name": f.get("name"),
            "type": f.get("mimeType"),
            "modified": f.get("modifiedTime")
        })
    
    return {
        "message": f"Found {len(files)} files in Drive",
        "files": file_list
    }


tool_registry.register("upload_to_drive", upload_to_drive)
tool_registry.register("list_drive_files", list_drive_files)