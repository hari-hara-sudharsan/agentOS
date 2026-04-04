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

    services = ["google", "github", "slack", "discord", "microsoft_azure", "salesforce", "linear", "gmail", "drive", "calendar", "pic_tools", "leetcode"]
    result = []
    
    scopes_map = {
        "google": {
            "name": "Google (Gmail/Drive/Calendar)",
            "scopes": ["gmail.readonly", "gmail.compose", "drive.file", "calendar.events"],
            "description": "Unified Google integration includes email, files and calendar operations."
        },
        "github": {
            "name": "GitHub",
            "scopes": [],
            "description": "Track repositories, issues, and pull request workflows. Requires a Personal Access Token."
        },
        "slack": {
            "name": "Slack",
            "scopes": ["chat:write", "channels:read"],
            "description": "Send and receive Slack messages through the agent."
        },
        "discord": {
            "name": "Discord",
            "scopes": [],
            "description": "Communicate with Discord channels via bot access token."
        },
        "microsoft_azure": {
            "name": "Microsoft/Azure",
            "scopes": [],
            "description": "Enterprise Azure integration for calendar, files, and app management."
        },
        "salesforce": {
            "name": "Salesforce",
            "scopes": [],
            "description": "CRM integration for leads, opportunities, and case workflows."
        },
        "linear": {
            "name": "Linear",
            "scopes": [],
            "description": "Linear issue tracking integration for product workflow tasks."
        },
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
        "pic_tools": {
            "name": "Pic Tools",
            "scopes": [],
            "description": "Provides AI image and media tooling. Add your service key to enable image workflows."
        },
        "leetcode": {
            "name": "LeetCode",
            "scopes": [],
            "description": "Automate LeetCode daily challenges. Store credentials securely to auto-submit solutions."
        }
    }

    from database.db import SessionLocal
    from database.models import Integration

    db = SessionLocal()
    try:
        for s in services:
            info = scopes_map.get(s, {})
            # Fast check: if it exists in our DB, we consider it 'connected' for the UI display.
            # We don't need to perform the expensive Token Vault exchange just to list services.
            integration = db.query(Integration).filter(
                Integration.user_id == user["sub"], 
                Integration.service == s
            ).first()
            
            connected = integration is not None
            consent_timestamp = integration.connected_at.isoformat() if connected and integration.connected_at else None

            result.append({
                "service": s,
                "connected": connected,
                "name": info.get("name", s),
                "scopes": info.get("scopes", []),
                "granted_scopes": [], # Simplified for now to ensure rendering stability
                "consent_timestamp": consent_timestamp,
                "description": info.get("description", "")
            })
    finally:
        db.close()

    print(f"DEBUG: list_integrations returning {len(result)} services for user {user['sub']}")
    return result


from pydantic import BaseModel

class TokenRequest(BaseModel):
    token: str | None = None
    username: str | None = None
    password: str | None = None


@router.post("/connect/{service}")
def connect_service(service: str, req: TokenRequest, user=Depends(get_current_user)):
    user_id = user["sub"]

    # LeetCode requires username and password
    if service == "leetcode":
        if not req.username or not req.password:
            raise HTTPException(400, detail="LeetCode requires both username and password.")
        import json
        # Store password in token_reference and username in extra_data
        from database.db import SessionLocal
        from database.models import Integration
        from datetime import datetime
        
        db = SessionLocal()
        try:
            existing = db.query(Integration).filter(
                Integration.user_id == user_id,
                Integration.service == service
            ).first()
            
            extra_data = json.dumps({"username": req.username})
            
            if existing:
                existing.token_reference = req.password  # Encrypted in production
                existing.extra_data = extra_data
                existing.connected_at = datetime.utcnow()
            else:
                new_integration = Integration(
                    user_id=user_id,
                    service=service,
                    token_reference=req.password,
                    extra_data=extra_data,
                    connected_at=datetime.utcnow()
                )
                db.add(new_integration)
            db.commit()
        finally:
            db.close()
        return {"status": "leetcode_connected", "message": "LeetCode credentials saved securely."}

    # Services that require manual API key/token input
    token_required_manually = ["pic_tools", "github", "discord", "microsoft_azure", "salesforce", "linear", "slack"]
    if service in token_required_manually:
        if not req.token:
            # For Slack, provide specific guidance
            if service == "slack":
                raise HTTPException(400, detail="Slack requires a Bot Token. Go to api.slack.com/apps → OAuth & Permissions → Bot User OAuth Token (starts with xoxb-)")
            raise HTTPException(400, detail=f"{service} requires an API key or connection token in request body.")
        # Allow slack bot tokens (xoxb-) and user tokens (xoxp-)
        if service == "slack" and not (req.token.startswith("xoxb-") or req.token.startswith("xoxp-")):
            raise HTTPException(400, detail="Invalid Slack token format. Token should start with xoxb- (bot) or xoxp- (user)")
        save_integration(user_id, service, req.token)
        return {"status": f"{service}_connected", "reference": f"{service}_token_ref"}

    # Keep OAuth-based services (google variants) to Auth0 Token Vault route
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
        "google": "google-oauth2",
        "gmail": "google-oauth2",
        "drive": "google-oauth2",
        "calendar": "google-oauth2",
        "slack": "slack"
    }
    
    # Job 6: Secure Vault Revocation (if supported)
    if service not in ["pic_tools", "github", "discord", "microsoft_azure", "salesforce", "linear"]:
        revoke_token_from_vault(user, connection_map.get(service, service))
    
    db = SessionLocal()
    integration = db.query(Integration).filter(Integration.user_id == user_id, Integration.service == service).first()
    if integration:
        db.delete(integration)
        db.commit()
    db.close()
    return {"status": f"{service}_disconnected"}