from fastapi import Request, HTTPException
from security.jwt_validator import verify_jwt
from datetime import datetime, timedelta
import uuid

pending_approvals = {}


def _cleanup_pending_approvals():
    now = datetime.utcnow()
    for approval_id in list(pending_approvals.keys()):
        if pending_approvals[approval_id]["expires_at"] < now:
            del pending_approvals[approval_id]


def create_pending_approval(user_context, tool, params):
    _cleanup_pending_approvals()

    approval_id = str(uuid.uuid4())
    user_id = user_context.get("sub")

    if tool == "create_calendar_event":
        title = params.get("title", "Untitled event")
        action = f"Create calendar event '{title}'"
    elif tool == "send_slack_message":
        channel = params.get("channel", "#general")
        message = params.get("message", "(no message)")
        action = f"Send Slack message to {channel}: '{message}'"
    elif tool == "upload_to_drive":
        destination = params.get("file_path", "<path>")
        action = f"Upload file to Drive at {destination}"
    else:
        action = f"Execute {tool}"

    binding_message = (
        f"AUTH0 STEP-UP REQUIRED: Agent requests high-stakes action: {action}. "
        "Please verify identity and grant explicit consent in Auth0 to continue."
    )

    pending_approvals[approval_id] = {
        "user_id": user_id,
        "tool": tool,
        "params": params,
        "binding_message": binding_message,
        "approved": False,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=30)
    }

    return approval_id, binding_message


def get_pending_approvals(user_context):
    _cleanup_pending_approvals()
    user_id = user_context.get("sub")
    return [
        {
            "approval_id": aid,
            "tool": info["tool"],
            "binding_message": info["binding_message"],
            "created_at": info["created_at"].isoformat(),
            "expires_at": info["expires_at"].isoformat(),
            "approved": info["approved"]
        }
        for aid, info in pending_approvals.items()
        if info["user_id"] == user_id and not info["approved"]
    ]


def approve_pending_approval(approval_id, user_context):
    _cleanup_pending_approvals()
    user_id = user_context.get("sub")

    if approval_id not in pending_approvals:
        raise HTTPException(404, detail="Approval request not found")

    ap = pending_approvals[approval_id]
    if ap["user_id"] != user_id:
        raise HTTPException(403, detail="Unauthorized approval request")

    ap["approved"] = True
    return ap


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


def check_mfa_and_consent(user_context, params, tool=None):
    """
    Job 4: Async Step-up Auth (Human-in-the-loop).
    - Raises ConsentRequiredException with approval_id and binding_message for UI to show.
    - Accepts pre-approved state and approval_id resume.
    """
    approval_id = params.get("approval_id")
    consent_granted = params.get("consent_granted")

    if consent_granted:
        return True

    if approval_id:
        _cleanup_pending_approvals()
        approval = pending_approvals.get(approval_id)
        if approval and approval.get("approved") and approval.get("user_id") == user_context.get("sub"):
            del pending_approvals[approval_id]
            return True
        raise ConsentRequiredException(
            "pending_approval_required",
            approval_id=approval_id,
            binding_message=approval.get("binding_message") if approval else "Pending approval record not found"
        )

    new_id, message = create_pending_approval(user_context, tool or "policy_action", params)
    raise ConsentRequiredException("pending_approval_required", approval_id=new_id, binding_message=message)
