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


def _run_scope_weaver_analysis(tool: str, params: dict, user_context: dict = None):
    """Run Scope Weaver analysis with OpenClaw to determine minimal scopes."""
    try:
        from agents.scope_weaver import weave_scopes_with_openclaw
        recommendation = weave_scopes_with_openclaw(tool, params, user_context)
        return recommendation
    except Exception as e:
        logger.warning(f"Scope Weaver analysis failed: {e}")
        return None


def _run_shadow_simulation(tool: str, params: dict, user_context: dict = None, graph_state: dict = None):
    """
    Run Shadow Simulator to predict outcomes and identify risks before execution.
    
    Returns simulation result if the tool requires simulation, None otherwise.
    """
    try:
        from agents.shadow_simulator import run_shadow_simulation, requires_shadow_simulation
        
        # Only run simulation for high-stakes tools
        if not requires_shadow_simulation(tool):
            return None
        
        result = run_shadow_simulation(tool, params, user_context, graph_state)
        return result
    except Exception as e:
        logger.warning(f"Shadow Simulator failed: {e}")
        return None


def create_pending_approval(user_context, tool, params, graph_state=None):
    """
    Create a new approval request in the database.
    Enhanced with Consent Guardian, Scope Weaver, and Shadow Simulator analysis
    for intelligent scope optimization, risk prediction, and plain-English explanations.
    """
    _cleanup_expired_approvals()

    approval_id = str(uuid.uuid4())
    user_id = user_context.get("sub")
    
    # Run Consent Guardian analysis
    guardian_analysis = _run_consent_guardian_analysis(tool, params)
    
    # Run Scope Weaver analysis for scope optimization
    scope_weaver_analysis = _run_scope_weaver_analysis(tool, params, user_context)
    
    # Run Shadow Simulator for high-stakes tools
    shadow_simulation = _run_shadow_simulation(tool, params, user_context, graph_state)

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

    # Determine which analysis to use (prefer Scope Weaver for scope info, Guardian for explanation)
    scope_weaver_json = None
    scope_evolution_score = None
    original_scopes_json = None
    
    if scope_weaver_analysis:
        recommended_scopes = scope_weaver_analysis.minimal_scopes
        scope_weaver_json = json.dumps(scope_weaver_analysis.to_dict())
        scope_evolution_score = scope_weaver_analysis.scope_evolution_score
        original_scopes_json = json.dumps(scope_weaver_analysis.original_scopes)
        
        # Use Scope Weaver explanation if Guardian not available
        if not guardian_analysis:
            ai_explanation = scope_weaver_analysis.plain_english_explanation
            risk_level = scope_weaver_analysis.risk_level.value
            confidence = str(scope_weaver_analysis.confidence)
        else:
            ai_explanation = guardian_analysis.plain_english_explanation
            risk_level = guardian_analysis.risk_level.value
            confidence = str(guardian_analysis.analysis_confidence)
    elif guardian_analysis:
        ai_explanation = guardian_analysis.plain_english_explanation
        risk_level = guardian_analysis.risk_level.value
        recommended_scopes = guardian_analysis.minimal_scopes
        confidence = str(guardian_analysis.analysis_confidence)
    else:
        ai_explanation = None
        risk_level = None
        recommended_scopes = []
        confidence = None

    # Build enhanced binding message with Scope Weaver info
    if ai_explanation:
        risk_emoji = {
            "low": "🟢",
            "medium": "🟡", 
            "high": "🟠",
            "critical": "🔴"
        }.get(risk_level, "⚪")
        
        scope_info = ""
        if scope_weaver_analysis and scope_weaver_analysis.scope_evolution_score > 0:
            scope_info = f"\n\n🧵 SCOPE WEAVER: Optimized permissions by {scope_weaver_analysis.scope_evolution_score}%"
        
        shadow_info = ""
        if shadow_simulation:
            shadow_emoji = {
                "success": "✅",
                "caution": "⚠️",
                "warning": "🔶",
                "blocked": "🚫"
            }.get(shadow_simulation.outcome.value, "❔")
            shadow_info = f"\n\n👁️ SHADOW SIMULATOR: {shadow_emoji} {shadow_simulation.outcome.value.upper()} ({shadow_simulation.risk_count} risks)"
        
        binding_message = (
            f"🔐 STEP-UP AUTH REQUIRED\n\n"
            f"🤖 AI ANALYSIS:\n"
            f"{ai_explanation}{scope_info}{shadow_info}\n\n"
            f"Risk Level: {risk_emoji} {risk_level.upper()}\n\n"
            f"Action: {action}"
        )
    else:
        binding_message = (
            f"🔐 STEP-UP AUTH REQUIRED: Agent requests high-stakes action: {action}. "
            "Please review and approve to continue."
        )
    
    analysis_json = json.dumps(guardian_analysis.to_dict()) if guardian_analysis else None
    
    # Prepare shadow simulation data
    shadow_simulation_json = None
    shadow_simulation_id = None
    shadow_outcome = None
    shadow_confidence = None
    shadow_risk_count = None
    
    if shadow_simulation:
        shadow_simulation_json = json.dumps(shadow_simulation.to_dict())
        shadow_simulation_id = shadow_simulation.simulation_id
        shadow_outcome = shadow_simulation.outcome.value
        shadow_confidence = shadow_simulation.confidence_score
        shadow_risk_count = shadow_simulation.risk_count

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
            analysis_confidence=confidence,
            # Scope Weaver fields
            scope_weaver_analysis=scope_weaver_json,
            scope_evolution_score=scope_evolution_score,
            original_scopes=original_scopes_json,
            # Shadow Simulator fields
            shadow_simulation=shadow_simulation_json,
            shadow_simulation_id=shadow_simulation_id,
            shadow_outcome=shadow_outcome,
            shadow_confidence=shadow_confidence,
            shadow_risk_count=shadow_risk_count
        )
        db.add(approval)
        db.commit()
        
        logger.info(f"Created approval {approval_id} for tool {tool}, risk_level={risk_level}, scope_evolution={scope_evolution_score}, shadow_outcome={shadow_outcome}")
    finally:
        db.close()

    return approval_id, binding_message


def get_pending_approvals(user_context):
    """Get all pending (unapproved) approvals for a user with Consent Guardian, Scope Weaver, and Shadow Simulator data."""
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
                "has_ai_analysis": ap.openclaw_analysis is not None,
                # Scope Weaver fields
                "scope_evolution_score": ap.scope_evolution_score,
                "original_scopes": json.loads(ap.original_scopes) if ap.original_scopes else [],
                "has_scope_weaver": ap.scope_weaver_analysis is not None,
                # Shadow Simulator fields
                "shadow_simulation": json.loads(ap.shadow_simulation) if ap.shadow_simulation else None,
                "shadow_simulation_id": ap.shadow_simulation_id,
                "shadow_outcome": ap.shadow_outcome,
                "shadow_confidence": ap.shadow_confidence,
                "shadow_risk_count": ap.shadow_risk_count,
                "has_shadow_simulation": ap.shadow_simulation is not None
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
                "has_ai_analysis": ap.openclaw_analysis is not None,
                # Scope Weaver fields
                "scope_evolution_score": ap.scope_evolution_score,
                "original_scopes": json.loads(ap.original_scopes) if ap.original_scopes else [],
                "has_scope_weaver": ap.scope_weaver_analysis is not None,
                # Shadow Simulator fields
                "shadow_simulation_id": ap.shadow_simulation_id,
                "shadow_outcome": ap.shadow_outcome,
                "shadow_confidence": ap.shadow_confidence,
                "shadow_risk_count": ap.shadow_risk_count,
                "has_shadow_simulation": ap.shadow_simulation is not None
            }
            for ap in approvals
        ]
    finally:
        db.close()


def approve_pending_approval(approval_id, user_context):
    """Mark an approval as approved and track Consent Guardian and Scope Weaver decisions."""
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
                from utils.metrics import track_consent_guardian_decision, track_scope_weaver_approval, track_shadow_simulation_decision
                latency = (approval.approved_at - approval.created_at).total_seconds()
                track_consent_guardian_decision(
                    tool=approval.tool,
                    risk_level=approval.risk_level,
                    decision="approved",
                    latency=latency
                )
                # Also track Scope Weaver approval if it was used
                if approval.scope_weaver_analysis:
                    track_scope_weaver_approval(
                        tool=approval.tool,
                        risk_level=approval.risk_level,
                        decision="approved",
                        latency=latency
                    )
                # Track Shadow Simulator decision if it was used
                if approval.shadow_simulation:
                    track_shadow_simulation_decision(
                        tool=approval.tool,
                        outcome=approval.shadow_outcome or "unknown",
                        decision="executed"
                    )
            except Exception as e:
                logger.warning(f"Failed to track approval decision: {e}")
        
        # Store Shadow Simulation result for analytics
        if approval.shadow_simulation:
            try:
                from agents.shadow_simulator import store_simulation_result, ShadowSimulationResult
                # Parse the simulation data to store
                sim_data = json.loads(approval.shadow_simulation)
                from agents.shadow_simulator import store_simulation_result
                # Store with minimal info (already in DB via approval)
                logger.info(f"Shadow simulation {approval.shadow_simulation_id} completed with decision=executed")
            except Exception as e:
                logger.warning(f"Failed to track shadow simulation: {e}")
        
        # Store Scope Weaver pattern for learning (non-sensitive)
        if approval.scope_weaver_analysis:
            try:
                from agents.scope_weaver import store_scope_pattern
                store_scope_pattern(
                    user_id=approval.user_id,
                    tool_name=approval.tool,
                    action_type="write" if "send" in approval.tool or "create" in approval.tool else "other",
                    recommended_scopes=json.loads(approval.recommended_scopes) if approval.recommended_scopes else [],
                    original_scopes=json.loads(approval.original_scopes) if approval.original_scopes else [],
                    evolution_score=approval.scope_evolution_score or 0
                )
            except Exception as e:
                logger.warning(f"Failed to store scope pattern: {e}")
        
        return {
            "approval_id": approval.approval_id,
            "tool": approval.tool,
            "approved": True,
            "approved_at": approval.approved_at.isoformat(),
            "recommended_scopes": json.loads(approval.recommended_scopes) if approval.recommended_scopes else [],
            # Include Scope Weaver info for Token Vault
            "scope_evolution_score": approval.scope_evolution_score,
            "has_scope_weaver": approval.scope_weaver_analysis is not None,
            # Include Shadow Simulator info
            "shadow_simulation_id": approval.shadow_simulation_id,
            "shadow_outcome": approval.shadow_outcome,
            "has_shadow_simulation": approval.shadow_simulation is not None
        }
    finally:
        db.close()


def check_approval_status(approval_id, user_context):
    """Check if an approval exists and its status, including Scope Weaver recommendations."""
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
            "ai_explanation": approval.ai_explanation,
            # Scope Weaver fields
            "scope_evolution_score": approval.scope_evolution_score,
            "original_scopes": json.loads(approval.original_scopes) if approval.original_scopes else [],
            "has_scope_weaver": approval.scope_weaver_analysis is not None
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

# Tools mapped to their service for token lookup
TOOL_SERVICE_MAP = {
    "create_calendar_event": "calendar",
    "send_slack_message": "slack",
    "upload_to_drive": "drive",
    "send_gmail": "gmail",
    "create_image": "pic_tools",
    "complete_leetcode_daily": "leetcode",
    "post_discord_message": "discord",
    "create_github_issue": "github",
    "list_github_repos": "github",
    "create_salesforce_lead": "salesforce",
    "create_linear_issue": "linear",
    "create_azure_resource": "azure",
    "list_azure_resources": "azure",
    "read_gmail": "gmail",
    "list_drive_files": "drive"
}

# HIGH-STAKES tools that ALWAYS require Human-in-the-Loop approval
# These are write/send/create operations that could have real-world consequences
HIGH_STAKES_TOOLS = {
    "send_gmail",           # Sending emails
    "post_discord_message", # Posting messages
    "send_slack_message",   # Sending messages
    "create_calendar_event",# Creating meetings
    "upload_to_drive",      # Uploading files
    "create_github_issue",  # Creating issues
    "create_salesforce_lead", # Creating CRM records
    "create_linear_issue",  # Creating issues
    "create_azure_resource", # Creating cloud resources
    "complete_leetcode_daily", # Submitting code
    "create_image",         # Generating images (cost)
    "browser_login",        # Logging into websites
    "browser_download_file", # Downloading files
    "pay_electricity_bill"  # Financial transactions
}

# READ-ONLY tools that can bypass approval (safe operations)
SAFE_TOOLS = {
    "read_gmail",           # Reading emails
    "list_github_repos",    # Listing repos
    "list_drive_files",     # Listing files
    "list_azure_resources", # Listing resources
    "browser_search",       # Web searches
    "browser_scrape_url",   # Reading web pages
    "summarize_text",       # Text processing
    "get_leetcode_daily_problem"  # Getting problem info
}


def check_mfa_and_consent(user_context, params, tool=None):
    """
    Job 4: Async Step-up Auth (Human-in-the-loop).
    
    Logic:
    1. If consent already granted (resume flow) → allow
    2. If approval_id exists and approved → allow
    3. If tool is in SAFE_TOOLS → allow (no approval needed for read-only)
    4. If tool is in HIGH_STAKES_TOOLS → ALWAYS require approval
    5. Otherwise → require approval (default to safe)
    """
    approval_id = params.get("approval_id")
    consent_granted = params.get("consent_granted")

    # 1. Consent already granted via resume flow
    if consent_granted:
        return True

    # 2. Check if approval exists and was approved
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
    
    # 3. SAFE tools (read-only) can bypass approval if integration exists
    if tool in SAFE_TOOLS:
        if tool in TOOL_SERVICE_MAP:
            service = TOOL_SERVICE_MAP[tool]
            token = get_integration_token(user_context, service)
            if token:
                return True  # Read-only with valid token = safe
        return True  # Safe tools don't need approval anyway
    
    # 4. HIGH-STAKES tools ALWAYS require approval (Human-in-the-Loop)
    if tool in HIGH_STAKES_TOOLS:
        # First check if integration exists (needed for execution after approval)
        if tool in TOOL_SERVICE_MAP:
            service = TOOL_SERVICE_MAP[tool]
            token = get_integration_token(user_context, service)
            if not token:
                raise ConsentRequiredException(
                    "integration_not_connected",
                    binding_message=f"Cannot execute {tool}: {service} is not connected. Please add it in Integrations."
                )
        # Create approval request
        new_id, message = create_pending_approval(user_context, tool, params)
        raise ConsentRequiredException("pending_approval_required", approval_id=new_id, binding_message=message)

    new_id, message = create_pending_approval(user_context, tool or "policy_action", params)
    raise ConsentRequiredException("pending_approval_required", approval_id=new_id, binding_message=message)
