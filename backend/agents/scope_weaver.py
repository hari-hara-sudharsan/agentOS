"""
Scope Weaver - Intelligent OAuth Scope Optimization via OpenClaw

This module implements the Scope Weaver pattern: before any external tool executes,
it analyzes the proposed action with OpenClaw (local LLM) to determine the minimal
OAuth scopes required, then enforces those through Token Vault.

Key Innovation:
- Receives proposed action details
- Queries OpenClaw for minimal_scopes[], plain_english_explanation, risk_level, scope_evolution_score
- Pauses execution for frontend approval with rich "Scope Weaver Recommendation" modal
- On approval, calls Token Vault exchange with ONLY the recommended scopes
- Stores non-sensitive patterns (action_type → recommended_scopes) for future learning

Security:
- Never stores raw tokens or secrets
- Uses official federated token-exchange grant via Token Vault
- All scope recommendations are audited
"""
import logging
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from agents.openclaw_bridge import get_openclaw_bridge
from utils.metrics import (
    track_scope_weaver_activation,
    track_scope_evolution,
    SCOPE_WEAVER_EVOLUTION_AVG
)

logger = logging.getLogger(__name__)


class ScopeWeaverRiskLevel(str, Enum):
    """Risk levels aligned with Consent Guardian"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ScopeWeaverRecommendation:
    """
    Result of Scope Weaver analysis.
    
    Contains everything needed for the frontend approval modal
    and Token Vault scope enforcement.
    """
    minimal_scopes: List[str]
    plain_english_explanation: str
    risk_level: ScopeWeaverRiskLevel
    scope_evolution_score: int  # 0-100: how much scope was reduced vs default
    tool_name: str
    action_type: str
    original_scopes: List[str]
    scope_reduction_count: int
    analysis_duration_ms: int = 0
    confidence: float = 0.85
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "minimal_scopes": self.minimal_scopes,
            "plain_english_explanation": self.plain_english_explanation,
            "risk_level": self.risk_level.value,
            "scope_evolution_score": self.scope_evolution_score,
            "tool_name": self.tool_name,
            "action_type": self.action_type,
            "original_scopes": self.original_scopes,
            "scope_reduction_count": self.scope_reduction_count,
            "analysis_duration_ms": self.analysis_duration_ms,
            "confidence": self.confidence
        }


# Default scope mappings for common tools
DEFAULT_TOOL_SCOPES = {
    "send_gmail": [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/gmail.readonly"
    ],
    "read_gmail": [
        "https://www.googleapis.com/auth/gmail.readonly"
    ],
    "upload_to_drive": [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file"
    ],
    "list_drive_files": [
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.metadata.readonly"
    ],
    "create_calendar_event": [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events"
    ],
    "send_slack_message": [
        "chat:write",
        "channels:read"
    ],
    "create_github_issue": [
        "repo"
    ],
    "list_github_repos": [
        "repo:read"
    ]
}

# Minimal scopes we know are safe reductions
MINIMAL_SCOPE_ALTERNATIVES = {
    "https://www.googleapis.com/auth/drive": "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/gmail.compose": "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar": "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/drive.readonly": "https://www.googleapis.com/auth/drive.metadata.readonly",
}


def _build_scope_analysis_prompt(tool_name: str, params: Dict[str, Any], default_scopes: List[str]) -> str:
    """Build the analysis prompt for OpenClaw to determine minimal scopes."""
    
    # Sanitize params (remove sensitive data)
    safe_params = {}
    for key, value in params.items():
        if key in ["password", "token", "secret", "api_key", "auth", "access_token"]:
            safe_params[key] = "[REDACTED]"
        elif isinstance(value, str) and len(value) > 200:
            safe_params[key] = value[:200] + "..."
        else:
            safe_params[key] = value
    
    params_json = json.dumps(safe_params, indent=2)
    scopes_json = json.dumps(default_scopes, indent=2)
    
    return f"""You are a security-focused OAuth scope optimizer for an AI agent system. Your task is to determine the MINIMAL OAuth scopes required for a specific action.

TOOL: {tool_name}
PARAMETERS:
{params_json}

DEFAULT SCOPES (potentially over-privileged):
{scopes_json}

Analyze this action and respond with ONLY a JSON object (no other text):
{{
    "minimal_scopes": ["list of minimum scopes needed for THIS SPECIFIC action"],
    "plain_english_explanation": "2-3 sentence explanation of what this action does and why these specific scopes are needed. Write for a non-technical user who needs to approve this.",
    "risk_level": "low|medium|high|critical",
    "scope_evolution_score": 0-100,
    "reasoning": "Brief technical explanation of scope reduction"
}}

GUIDELINES:
1. "minimal_scopes": Only include scopes absolutely required. Examples:
   - For sending email: use gmail.send not gmail.compose if just sending
   - For uploading to Drive: use drive.file not drive (full access)
   - For reading metadata: use .metadata.readonly not full .readonly

2. "scope_evolution_score": Calculate as percentage of scope reduction:
   - 0 = no reduction possible (already minimal)
   - 50 = reduced scope count by half
   - 100 = maximum safe reduction achieved

3. "risk_level":
   - low: Read-only, user's own data
   - medium: Write to personal workspace
   - high: External communication (email, messages)
   - critical: Authentication, financial, irreversible

Respond with ONLY the JSON object."""


def _parse_scope_weaver_response(
    response: str, 
    tool_name: str, 
    params: Dict[str, Any],
    default_scopes: List[str]
) -> ScopeWeaverRecommendation:
    """Parse OpenClaw response into ScopeWeaverRecommendation."""
    
    try:
        response_text = response.strip()
        
        # Handle markdown code blocks
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        
        analysis = json.loads(response_text)
        
        minimal_scopes = analysis.get("minimal_scopes", default_scopes)
        
        # Parse risk level
        risk_str = analysis.get("risk_level", "medium").lower()
        try:
            risk_level = ScopeWeaverRiskLevel(risk_str)
        except ValueError:
            risk_level = ScopeWeaverRiskLevel.MEDIUM
        
        # Calculate scope reduction
        scope_reduction = len(default_scopes) - len(minimal_scopes)
        
        # Get evolution score from analysis or calculate
        evolution_score = analysis.get("scope_evolution_score", 0)
        if not isinstance(evolution_score, int):
            try:
                evolution_score = int(evolution_score)
            except:
                evolution_score = 0
        evolution_score = max(0, min(100, evolution_score))  # Clamp to 0-100
        
        return ScopeWeaverRecommendation(
            minimal_scopes=minimal_scopes,
            plain_english_explanation=analysis.get("plain_english_explanation", 
                f"Execute '{tool_name}' with the specified parameters."),
            risk_level=risk_level,
            scope_evolution_score=evolution_score,
            tool_name=tool_name,
            action_type=_get_action_type(tool_name),
            original_scopes=default_scopes,
            scope_reduction_count=scope_reduction,
            confidence=0.85
        )
        
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Failed to parse Scope Weaver response: {e}")
        return _build_fallback_recommendation(tool_name, params, default_scopes)


def _get_action_type(tool_name: str) -> str:
    """Categorize tool into action type for pattern storage."""
    if "send" in tool_name or "post" in tool_name or "create" in tool_name:
        return "write"
    elif "read" in tool_name or "list" in tool_name or "get" in tool_name:
        return "read"
    elif "upload" in tool_name:
        return "upload"
    elif "delete" in tool_name or "remove" in tool_name:
        return "delete"
    elif "login" in tool_name or "auth" in tool_name:
        return "auth"
    return "other"


def _build_fallback_recommendation(
    tool_name: str, 
    params: Dict[str, Any],
    default_scopes: List[str]
) -> ScopeWeaverRecommendation:
    """Build rule-based fallback when OpenClaw is unavailable."""
    
    # Apply known safe reductions
    minimal_scopes = []
    for scope in default_scopes:
        if scope in MINIMAL_SCOPE_ALTERNATIVES:
            minimal_scopes.append(MINIMAL_SCOPE_ALTERNATIVES[scope])
        else:
            minimal_scopes.append(scope)
    
    # Remove duplicates while preserving order
    minimal_scopes = list(dict.fromkeys(minimal_scopes))
    
    scope_reduction = len(default_scopes) - len(minimal_scopes)
    evolution_score = int((scope_reduction / max(len(default_scopes), 1)) * 100)
    
    # Determine risk level based on tool
    risk_map = {
        "send_gmail": ScopeWeaverRiskLevel.HIGH,
        "read_gmail": ScopeWeaverRiskLevel.LOW,
        "upload_to_drive": ScopeWeaverRiskLevel.HIGH,
        "list_drive_files": ScopeWeaverRiskLevel.LOW,
        "create_calendar_event": ScopeWeaverRiskLevel.MEDIUM,
        "send_slack_message": ScopeWeaverRiskLevel.HIGH,
        "browser_login": ScopeWeaverRiskLevel.CRITICAL,
        "complete_leetcode_daily": ScopeWeaverRiskLevel.HIGH
    }
    risk_level = risk_map.get(tool_name, ScopeWeaverRiskLevel.MEDIUM)
    
    # Build explanation
    explanation = _build_default_explanation(tool_name, params)
    
    return ScopeWeaverRecommendation(
        minimal_scopes=minimal_scopes,
        plain_english_explanation=explanation,
        risk_level=risk_level,
        scope_evolution_score=evolution_score,
        tool_name=tool_name,
        action_type=_get_action_type(tool_name),
        original_scopes=default_scopes,
        scope_reduction_count=scope_reduction,
        confidence=0.6  # Lower confidence for fallback
    )


def _build_default_explanation(tool_name: str, params: Dict[str, Any]) -> str:
    """Build human-readable explanation for common tools."""
    
    explanations = {
        "send_gmail": lambda p: f"Send an email to {p.get('to', 'recipient')} with subject '{p.get('subject', 'No subject')}'. This requires permission to send emails on your behalf.",
        "read_gmail": lambda p: f"Read your {p.get('count', 10)} most recent emails. This is a read-only operation.",
        "upload_to_drive": lambda p: f"Upload a file to Google Drive at '{p.get('file_path', 'your Drive')}'. Only this specific file will be affected.",
        "list_drive_files": lambda p: "List files in your Google Drive. No files will be modified.",
        "create_calendar_event": lambda p: f"Create a calendar event '{p.get('title', 'Untitled')}'. This will add an event to your calendar.",
        "send_slack_message": lambda p: f"Send a message to Slack channel {p.get('channel', '#general')}. The message will be visible to channel members.",
        "browser_login": lambda p: f"Log into {p.get('url', 'a website')} using stored credentials. This is a sensitive operation.",
        "complete_leetcode_daily": lambda p: f"Submit a {p.get('language', 'Python')} solution to today's LeetCode challenge.",
    }
    
    builder = explanations.get(tool_name)
    if builder:
        try:
            return builder(params)
        except:
            pass
    
    return f"Execute '{tool_name}' with the specified parameters. Please review the required permissions."


def weave_scopes_with_openclaw(
    tool_name: str,
    params: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> ScopeWeaverRecommendation:
    """
    Main entry point for Scope Weaver.
    
    Analyzes a proposed action using OpenClaw to determine minimal OAuth scopes,
    then returns a recommendation for the approval modal and Token Vault.
    
    Args:
        tool_name: Name of the tool to execute
        params: Tool parameters (sensitive data will be redacted)
        user_context: Auth0 user context for audit logging
    
    Returns:
        ScopeWeaverRecommendation with minimal_scopes, explanation, risk_level, etc.
    """
    start_time = time.time()
    
    logger.info(f"Scope Weaver analyzing: {tool_name}")
    
    # Get default scopes for this tool
    default_scopes = DEFAULT_TOOL_SCOPES.get(tool_name, [])
    
    # If no scopes needed, return quick recommendation
    if not default_scopes:
        return ScopeWeaverRecommendation(
            minimal_scopes=[],
            plain_english_explanation=_build_default_explanation(tool_name, params),
            risk_level=ScopeWeaverRiskLevel.MEDIUM,
            scope_evolution_score=0,
            tool_name=tool_name,
            action_type=_get_action_type(tool_name),
            original_scopes=[],
            scope_reduction_count=0,
            analysis_duration_ms=0,
            confidence=1.0
        )
    
    try:
        bridge = get_openclaw_bridge()
        
        # Check OpenClaw availability
        health = bridge.health_check()
        if not health.get("healthy"):
            logger.warning("OpenClaw not available, using rule-based Scope Weaver")
            recommendation = _build_fallback_recommendation(tool_name, params, default_scopes)
            duration_ms = int((time.time() - start_time) * 1000)
            recommendation.analysis_duration_ms = duration_ms
            track_scope_weaver_activation(tool_name, recommendation.risk_level.value, "fallback")
            return recommendation
        
        # Build and send analysis prompt
        prompt = _build_scope_analysis_prompt(tool_name, params, default_scopes)
        
        analysis_context = user_context or {"sub": "scope_weaver_system"}
        
        result = bridge.generate(
            user_context=analysis_context,
            prompt=prompt,
            model="llama3",
            options={"temperature": 0.2}  # Low temperature for consistent recommendations
        )
        
        if result.get("success"):
            response_text = result.get("response", "")
            recommendation = _parse_scope_weaver_response(response_text, tool_name, params, default_scopes)
        else:
            logger.warning(f"OpenClaw generation failed: {result.get('error')}")
            recommendation = _build_fallback_recommendation(tool_name, params, default_scopes)
        
        duration_ms = int((time.time() - start_time) * 1000)
        recommendation.analysis_duration_ms = duration_ms
        
        # Track metrics
        track_scope_weaver_activation(tool_name, recommendation.risk_level.value, "analyzed")
        track_scope_evolution(recommendation.scope_evolution_score)
        
        logger.info(
            f"Scope Weaver complete: tool={tool_name}, "
            f"scopes={len(default_scopes)}→{len(recommendation.minimal_scopes)}, "
            f"evolution={recommendation.scope_evolution_score}%, "
            f"duration={duration_ms}ms"
        )
        
        return recommendation
        
    except Exception as e:
        logger.error(f"Scope Weaver error: {e}")
        recommendation = _build_fallback_recommendation(tool_name, params, default_scopes)
        duration_ms = int((time.time() - start_time) * 1000)
        recommendation.analysis_duration_ms = duration_ms
        track_scope_weaver_activation(tool_name, recommendation.risk_level.value, "error")
        return recommendation


def store_scope_pattern(
    user_id: str,
    tool_name: str,
    action_type: str,
    recommended_scopes: List[str],
    original_scopes: List[str],
    evolution_score: int
) -> bool:
    """
    Store non-sensitive scope pattern for future learning.
    
    IMPORTANT: Never stores tokens or secrets - only action patterns and scope recommendations.
    """
    from database.db import SessionLocal
    from database.models import ScopeWeaverPattern
    
    db = SessionLocal()
    try:
        pattern = ScopeWeaverPattern(
            user_id=user_id,
            tool_name=tool_name,
            action_type=action_type,
            recommended_scopes=json.dumps(recommended_scopes),
            original_scopes=json.dumps(original_scopes),
            scope_evolution_score=evolution_score
        )
        db.add(pattern)
        db.commit()
        logger.info(f"Stored scope pattern: {tool_name} → {len(recommended_scopes)} scopes")
        return True
    except Exception as e:
        logger.error(f"Failed to store scope pattern: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def get_learned_scopes(tool_name: str, action_type: str) -> Optional[List[str]]:
    """
    Retrieve previously learned optimal scopes for a tool/action combination.
    
    Returns the most common recommendation based on historical patterns.
    """
    from database.db import SessionLocal
    from database.models import ScopeWeaverPattern
    from sqlalchemy import func
    
    db = SessionLocal()
    try:
        # Get the most common scope recommendation for this tool
        result = db.query(
            ScopeWeaverPattern.recommended_scopes,
            func.count(ScopeWeaverPattern.id).label('count')
        ).filter(
            ScopeWeaverPattern.tool_name == tool_name,
            ScopeWeaverPattern.action_type == action_type
        ).group_by(
            ScopeWeaverPattern.recommended_scopes
        ).order_by(
            func.count(ScopeWeaverPattern.id).desc()
        ).first()
        
        if result:
            return json.loads(result.recommended_scopes)
        return None
    except Exception as e:
        logger.warning(f"Failed to retrieve learned scopes: {e}")
        return None
    finally:
        db.close()


# Register as a tool for agent use
from registry.tool_registry import tool_registry

def scope_weaver_analyze(user_context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Agent tool wrapper for Scope Weaver analysis."""
    tool_name = params.get("tool_name", "unknown")
    tool_params = params.get("tool_params", {})
    
    recommendation = weave_scopes_with_openclaw(tool_name, tool_params, user_context)
    return recommendation.to_dict()

tool_registry.register("scope_weaver_analyze", scope_weaver_analyze)
