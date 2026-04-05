from fastapi import Request, HTTPException
from security.jwt_validator import verify_jwt
from datetime import datetime, timedelta
from database.db import SessionLocal
from database.models import Approval
import uuid
import json


def _cleanup_expired_approvals():
    """Remove expired approvals from database."""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        db.query(Approval).filter(Approval.expires_at < now).delete()
        db.commit()
    finally:
        db.close()


def create_pending_approval(user_context, tool, params):
    """Create a new approval request in the database."""
    _cleanup_expired_approvals()

    approval_id = str(uuid.uuid4())
    user_id = user_context.get("sub")

    if tool == "create_calendar_event":
        title = params.get("title", "Untitled event")
        action = f"Create calendar event '{title}'"
    elif tool == "send_slack_message":
        channel = params.get("channel", "#general")
        message = params.get("message", "(no message)")
        action = f"Send Slack message to {channel}: '{message[:50]}...'" if len(params.get("message", "")) > 50 else f"Send Slack message to {channel}: '{message}'"
    elif tool == "upload_to_drive":
        destination = params.get("file_path", "<path>")
        action = f"Upload file to Drive at {destination}"
    elif tool == "send_gmail":
        to = params.get("to", "unknown")
        subject = params.get("subject", "No subject")
        action = f"Send email to {to} with subject '{subject}'"
    elif tool == "browser_login":
        site = params.get("url", "website")
        action = f"Login to {site} via browser automation"
    elif tool == "browser_download_file":
        action = f"Download file from website"
    elif tool == "complete_leetcode_daily":
        language = params.get("language", "python3")
        action = f"Submit solution to LeetCode daily challenge ({language})"
    else:
        action = f"Execute {tool}"

    binding_message = (
        f"🔐 STEP-UP AUTH REQUIRED: Agent requests high-stakes action: {action}. "
        "Please review and approve to continue."
    )

    db = SessionLocal()
    try:
        approval = Approval(
            approval_id=approval_id,
            user_id=user_id,
            tool=tool,
            params=json.dumps(params),
            binding_message=binding_message,
            approved=False,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)  # Extended to 24 hours
        )
        db.add(approval)
        db.commit()
    finally:
        db.close()

    return approval_id, binding_message


def get_pending_approvals(user_context):
    """Get all pending (unapproved) approvals for a user."""
    _cleanup_expired_approvals()
    user_id = user_context.get("sub")
    
    db = SessionLocal()
    try:
        approvals = db.query(Approval).filter(
            Approval.user_id == user_id,
            Approval.approved == False
        ).order_by(Approval.created_at.desc()).all()
        
        return [
            {
                "approval_id": ap.approval_id,
                "tool": ap.tool,
                "binding_message": ap.binding_message,
                "created_at": ap.created_at.isoformat(),
                "expires_at": ap.expires_at.isoformat(),
                "approved": ap.approved
            }
            for ap in approvals
        ]
    finally:
        db.close()


def get_approval_history(user_context, limit=50):
    """Get approval history (both approved and pending) for activity tracking."""
    user_id = user_context.get("sub")
    
    db = SessionLocal()
    try:
        approvals = db.query(Approval).filter(
            Approval.user_id == user_id
        ).order_by(Approval.created_at.desc()).limit(limit).all()
        
        return [
            {
                "approval_id": ap.approval_id,
                "tool": ap.tool,
                "binding_message": ap.binding_message,
                "approved": ap.approved,
                "approved_at": ap.approved_at.isoformat() if ap.approved_at else None,
                "created_at": ap.created_at.isoformat(),
                "expires_at": ap.expires_at.isoformat()
            }
            for ap in approvals
        ]
    finally:
        db.close()


def approve_pending_approval(approval_id, user_context):
    """Mark an approval as approved."""
    _cleanup_expired_approvals()
    user_id = user_context.get("sub")

    db = SessionLocal()
    try:
        approval = db.query(Approval).filter(Approval.approval_id == approval_id).first()
        
        if not approval:
            raise HTTPException(404, detail="Approval request not found or expired")

        if approval.user_id != user_id:
            raise HTTPException(403, detail="Unauthorized approval request")

        approval.approved = True
        approval.approved_at = datetime.utcnow()
        db.commit()
        
        return {
            "approval_id": approval.approval_id,
            "tool": approval.tool,
            "approved": True,
            "approved_at": approval.approved_at.isoformat()
        }
    finally:
        db.close()


def check_approval_status(approval_id, user_context):
    """Check if an approval exists and its status."""
    user_id = user_context.get("sub")
    
    db = SessionLocal()
    try:
        approval = db.query(Approval).filter(Approval.approval_id == approval_id).first()
        
        if not approval:
            return None
            
        if approval.user_id != user_id:
            return None
            
        return {
            "approved": approval.approved,
            "tool": approval.tool,
            "params": json.loads(approval.params) if approval.params else {},
            "binding_message": approval.binding_message
        }
    finally:
        db.close()


async def get_current_user(request: Request):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    parts = auth_header.split()

    if parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = parts[1]

    payload = verify_jwt(token)
    payload["auth0_access_token"] = token

    return payload


def get_user_role(payload):

    roles = payload.get("roles", [])

    if not roles:
        return "basic_user"

    return roles[0]


class ConsentRequiredException(Exception):
    def __init__(self, reason, approval_id=None, binding_message=None):
        self.reason = reason
        self.approval_id = approval_id
        self.binding_message = binding_message
        super().__init__(reason)


from integrations.integration_service import get_integration_token

TOOL_SERVICE_MAP = {
    "create_calendar_event": "calendar",
    "send_slack_message": "slack",
    "upload_to_drive": "drive",
    "send_gmail": "gmail",
    "create_image": "pic_tools",
    "complete_leetcode_daily": "leetcode"
}


def check_mfa_and_consent(user_context, params, tool=None):
    """
    Job 4: Async Step-up Auth (Human-in-the-loop).
    - Raises ConsentRequiredException with approval_id and binding_message for UI to show.
    - Accepts pre-approved state and approval_id resume.
    - Now persisted to database for durability across restarts.
    """
    approval_id = params.get("approval_id")
    consent_granted = params.get("consent_granted")

    if consent_granted:
        return True

    if tool in TOOL_SERVICE_MAP:
        service = TOOL_SERVICE_MAP[tool]
        token = get_integration_token(user_context, service)
        if token:
            # existing integration detected; bypass repeated manual consent
            return True

    if approval_id:
        _cleanup_expired_approvals()
        status = check_approval_status(approval_id, user_context)
        if status and status.get("approved"):
            return True
        raise ConsentRequiredException(
            "pending_approval_required",
            approval_id=approval_id,
            binding_message=status.get("binding_message") if status else "Pending approval record not found"
        )

    new_id, message = create_pending_approval(user_context, tool or "policy_action", params)
    raise ConsentRequiredException("pending_approval_required", approval_id=new_id, binding_message=message)
