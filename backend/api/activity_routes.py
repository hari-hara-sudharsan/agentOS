from fastapi import APIRouter, Depends
from security.auth0_client import get_current_user

router = APIRouter()


@router.get("/")
def get_activity_log(user=Depends(get_current_user)):

    activity = [
        {
            "time": "10:02 AM",
            "action": "gmail_accessed"
        },
        {
            "time": "10:03 AM",
            "action": "email_summary_generated"
        }
    ]

    return {
        "user": user["sub"],
        "activity": activity
    }