from fastapi import APIRouter, Depends
from security.auth0_client import get_current_user

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