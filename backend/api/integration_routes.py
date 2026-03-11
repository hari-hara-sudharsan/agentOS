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

@router.post("/connect/gmail")
def connect_gmail(token: str, user=Depends(get_current_user)):

    user_id = user["sub"]

    save_integration(
        user_id,
        "gmail",
        token
    )

    return {"status": "gmail_connected"}