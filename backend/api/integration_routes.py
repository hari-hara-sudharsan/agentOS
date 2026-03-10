from fastapi import APIRouter, Depends
from security.auth0_client import get_current_user
from integrations.integration_service import save_integration

router = APIRouter()


@router.get("/")
def list_integrations(user=Depends(get_current_user)):

    # placeholder integrations
    integrations = [
        {
            "service": "gmail",
            "connected": False
        },
        {
            "service": "slack",
            "connected": False
        },
        {
            "service": "google_drive",
            "connected": False
        }
    ]

    return {
        "user": user["sub"],
        "integrations": integrations
    }

@router.post("/connect/gmail")
def connect_gmail(token: str, user=Depends(get_current_user)):

    user_id = user["sub"]

    save_integration(
        user_id,
        "gmail",
        token
    )

    return {"status": "gmail_connected"}