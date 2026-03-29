from fastapi import APIRouter, Depends, HTTPException
from security.auth0_client import get_current_user
from integrations.integration_service import (
    save_integration,
    get_integration_token,
    get_connection_reference,
    SERVICE_CONNECTION_MAP,
    _is_raw_token
)

router = APIRouter()


@router.get("")
def list_integrations(user=Depends(get_current_user)):

    services = ["gmail", "slack", "drive", "calendar"]
    result = []
    
    scopes_map = {
        "gmail": {
            "name": "Gmail (Read & Send)",
            "scopes": ["gmail.readonly", "gmail.compose"],
            "description": "Allows agent to read your inbox and send emails on your behalf."
        },
        "drive": {
            "name": "Google Drive",
            "scopes": ["drive.file"],
            "description": "Allows agent to upload files. Cannot delete existing files."
        },
        "calendar": {
            "name": "Google Calendar",
            "scopes": ["calendar.events"],
            "description": "Allows agent to view and schedule calendar events."
        },
        "slack": {
            "name": "Slack Channels",
            "scopes": ["chat:write", "channels:read"],
            "description": "Allows agent to read channels and post messages."
        }
    }

    from database.db import SessionLocal
    from database.models import Integration

    db = SessionLocal()
    try:
        for s in services:
            info = scopes_map.get(s, {})
            integration = db.query(Integration).filter(Integration.user_id == user["sub"], Integration.service == s).first()
            try:
                token = get_integration_token(user, s)
            except Exception:
                token = None

            consent_timestamp = integration.connected_at.isoformat() if integration and integration.connected_at else None
            granted_scopes = [
                {
                    "scope": sc,
                    "description": "Allowed" if sc in info.get("scopes", []) else "Extra"
                }
                for sc in info.get("scopes", [])
            ]

            result.append({
                "service": s,
                "connected": token is not None,
                "name": info.get("name", s),
                "scopes": info.get("scopes", []),
                "granted_scopes": granted_scopes,
                "consent_timestamp": consent_timestamp,
                "description": info.get("description", "")
            })
    finally:
        db.close()

    return result


from pydantic import BaseModel

class TokenRequest(BaseModel):
    token: str | None = None


@router.post("/connect/{service}")
def connect_service(service: str, req: TokenRequest, user=Depends(get_current_user)):
    user_id = user["sub"]

    if req.token and _is_raw_token(req.token):
        raise HTTPException(400, detail="Raw tokens are not accepted, use vault exchange flow and store non-sensitive references only.")

    connection_ref = get_connection_reference(user, service)
    if not connection_ref:
        raise HTTPException(400, detail="Unable to obtain Auth0 connection reference from Vault. Ensure you have completed OAuth flow and granted scopes.")

    save_integration(user_id, service, connection_ref)

    return {"status": f"{service}_connected", "reference": connection_ref}


@router.delete("/disconnect/{service}")
def disconnect_service(service: str, user=Depends(get_current_user)):
    user_id = user["sub"]
    from database.db import SessionLocal
    from database.models import Integration
    from integrations.integration_service import revoke_token_from_vault
    
    connection_map = {
        "gmail": "google-oauth2",
        "drive": "google-oauth2",
        "calendar": "google-oauth2",
        "slack": "slack"
    }
    
    # Job 6: Secure Vault Revocation
    revoke_token_from_vault(user, connection_map.get(service, service))
    
    db = SessionLocal()
    integration = db.query(Integration).filter(Integration.user_id == user_id, Integration.service == service).first()
    if integration:
        db.delete(integration)
        db.commit()
    db.close()
    return {"status": f"{service}_disconnected"}