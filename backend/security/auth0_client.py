from fastapi import Request, HTTPException
from security.jwt_validator import verify_jwt
from datetime import datetime, timedelta
from database.db import SessionLocal
from database.models import Approval
import uuid
import json
import logging

logger = logging.getLogger(__name__)


def _cleanup_expired_approvals():
    """Remove expired approvals from database."""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        db.query(Approval).filter(Approval.expires_at < now).delete()
        db.commit()
    finally:
        db.close()


def _run_consent_guardian_analysis(tool: str, params: dict):
    """Run Consent Guardian analysis with OpenClaw if available."""
    try:
        from agents.consent_guardian import analyze_action_with_openclaw
        analysis = analyze_action_with_openclaw(tool, params)
        return analysis
    except Exception as e:
        logger.warning(f"Consent Guardian analysis failed: {e}")
        return None


def create_pending_approval(user_context, tool, params):
    """
    Create a new approval request in the database.
    Enhanced with Consent Guardian AI analysis for intelligent explanations.
    """
    _cleanup_expired_approvals()

    approval_id = str(uuid.uuid4())
    user_id = user_context.get("sub")
    
    # Run Consent Guardian analysis
    guardian_analysis = _run_consent_guardian_analysis(tool, params)

    # Build action description
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

    # Use AI explanation if available, fallback to standard message
    if guardian_analysis:
        ai_explanation = guardian_analysis.plain_english_explanation
        risk_level = guardian_analysis.risk_level.value
        recommended_scopes = guardian_analysis.minimal_scopes
        analysis_json = json.dumps(guardian_analysis.to_dict())
        confidence = str(guardian_analysis.analysis_confidence)
        
        # Build enhanced binding message with AI explanation
        risk_emoji = {
            "low": "🟢",
            "medium": "🟡", 
            "high": "🟠",
            "critical": "🔴"
        }.get(risk_level, "⚪")
        
        binding_message = (
            f"🔐 STEP-UP AUTH REQUIRED\n\n"
            f"🤖 AI ANALYSIS (Consent Guardian):\n"
            f"{ai_explanation}\n\n"
            f"Risk Level: {risk_emoji} {risk_level.upper()}\n\n"
            f"Action: {action}"
        )
    else:
        ai_explanation = None
        risk_level = None
        recommended_scopes = []
        analysis_json = None
        confidence = None
        
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
            expires_at=datetime.utcnow() + timedelta(hours=24),
            # Consent Guardian fields
            openclaw_analysis=analysis_json,
            risk_level=risk_level,
            recommended_scopes=json.dumps(recommended_scopes) if recommended_scopes else None,
            ai_explanation=ai_explanation,
            analysis_confidence=confidence
        )
        db.add(approval)
        db.commit()
        
        logger.info(f"Created approval {approval_id} for tool {tool}, risk_level={risk_level}")
    finally:
        db.close()

    return approval_id, binding_message


def get_pending_approvals(user_context):
    """Get all pending (unapproved) approvals for a user with Consent Guardian data."""
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
                "approved": ap.approved,
                # Consent Guardian fields
                "risk_level": ap.risk_level,
                "ai_explanation": ap.ai_explanation,
                "recommended_scopes": json.loads(ap.recommended_scopes) if ap.recommended_scopes else [],
                "analysis_confidence": float(ap.analysis_confidence) if ap.analysis_confidence else None,
                "has_ai_analysis": ap.openclaw_analysis is not None
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
                "expires_at": ap.expires_at.isoformat(),
                # Consent Guardian fields
                "risk_level": ap.risk_level,
                "ai_explanation": ap.ai_explanation,
                "recommended_scopes": json.loads(ap.recommended_scopes) if ap.recommended_scopes else [],
                "has_ai_analysis": ap.openclaw_analysis is not None
            }
            for ap in approvals
        ]
    finally:
        db.close()


def approve_pending_approval(approval_id, user_context):
    """Mark an approval as approved and track Consent Guardian decision."""
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
        
        # Track Consent Guardian decision metric
        if approval.risk_level:
            try:
                from utils.metrics import track_consent_guardian_decision
                latency = (approval.approved_at - approval.created_at).total_seconds()
                track_consent_guardian_decision(
                    tool=approval.tool,
                    risk_level=approval.risk_level,
                    decision="approved",
                    latency=latency
                )
            except Exception as e:
                logger.warning(f"Failed to track consent guardian decision: {e}")
        
        return {
            "approval_id": approval.approval_id,
            "tool": approval.tool,
            "approved": True,
            "approved_at": approval.approved_at.isoformat(),
            "recommended_scopes": json.loads(approval.recommended_scopes) if approval.recommended_scopes else []
        }
    finally:
        db.close()


def check_approval_status(approval_id, user_context):
    """Check if an approval exists and its status, including recommended scopes."""
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
            "binding_message": approval.binding_message,
            # Consent Guardian fields for Token Vault scope enforcement
            "recommended_scopes": json.loads(approval.recommended_scopes) if approval.recommended_scopes else [],
            "risk_level": approval.risk_level,
            "ai_explanation": approval.ai_explanation
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
