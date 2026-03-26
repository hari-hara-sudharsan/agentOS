from fastapi import APIRouter, Depends
from security.auth0_client import get_current_user, get_pending_approvals, approve_pending_approval

router = APIRouter()


@router.get("/")
def list_approvals(user=Depends(get_current_user)):
    return get_pending_approvals(user)


@router.post("/approve/{approval_id}")
def approve(approval_id: str, user=Depends(get_current_user)):
    ap = approve_pending_approval(approval_id, user)
    return {"status": "approved", "approval_id": approval_id, "binding_message": ap.get("binding_message")}
