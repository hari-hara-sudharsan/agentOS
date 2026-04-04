from fastapi import APIRouter, Depends
from security.auth0_client import (
    get_current_user, 
    get_pending_approvals, 
    approve_pending_approval,
    get_approval_history
)

router = APIRouter()


@router.get("")
def list_approvals(user=Depends(get_current_user)):
    """Get all pending approvals for the current user."""
    return get_pending_approvals(user)


@router.get("/history")
def list_approval_history(user=Depends(get_current_user), limit: int = 50):
    """Get approval history (both approved and pending) for the current user."""
    return get_approval_history(user, limit)


@router.post("/approve/{approval_id}")
def approve(approval_id: str, user=Depends(get_current_user)):
    """Approve a pending approval request."""
    ap = approve_pending_approval(approval_id, user)
    return {"status": "approved", "approval_id": approval_id, "binding_message": ap.get("binding_message")}
