from fastapi import APIRouter, Depends
from security.auth0_client import get_current_user
from integrations.integration_service import save_integration, get_integration_token

router = APIRouter()


@router.get("/")
def list_integrations(user=Depends(get_current_user)):

    user_id = user["sub"]

    services = ["gmail","slack","drive","calendar"]

    result = []

    for s in services:

        token = get_integration_token(user_id, s)

        result.append({
            "service": s,
            "connected": token is not None
        })

    return result

from pydantic import BaseModel

class TokenRequest(BaseModel):
    token: str

@router.post("/connect/{service}")
def connect_service(service: str, req: TokenRequest, user=Depends(get_current_user)):

    user_id = user["sub"]

    save_integration(
        user_id,
        service,
        req.token
    )

    return {"status": f"{service}_connected"}


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