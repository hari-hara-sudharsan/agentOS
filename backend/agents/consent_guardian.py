"""
Consent Guardian - AI-Powered Action Analysis with OpenClaw

This module provides intelligent analysis of agent actions before execution,
leveraging local LLM (OpenClaw/Ollama) to:
- Determine minimal required scopes
- Generate plain-English explanations of what actions will do
- Assess risk levels for user decision-making

Integrates with Token Vault to enforce least-privilege principle.
"""
import logging
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from agents.openclaw_bridge import get_openclaw_bridge
from utils.metrics import track_consent_guardian_activation

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk levels for agent actions"""
    LOW = "low"           # Read-only, non-sensitive
    MEDIUM = "medium"     # Read with some sensitivity
    HIGH = "high"         # Write operations, external communications
    CRITICAL = "critical" # Destructive, financial, or irreversible


@dataclass
class ConsentGuardianAnalysis:
    """Result of Consent Guardian analysis"""
    minimal_scopes: List[str]
    plain_english_explanation: str
    risk_level: RiskLevel
    tool_name: str
    action_summary: str
    potential_impacts: List[str]
    recommended_alternatives: Optional[List[str]] = None
    analysis_confidence: float = 0.0
    analysis_duration_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "minimal_scopes": self.minimal_scopes,
            "plain_english_explanation": self.plain_english_explanation,
            "risk_level": self.risk_level.value,
            "tool_name": self.tool_name,
            "action_summary": self.action_summary,
            "potential_impacts": self.potential_impacts,
            "recommended_alternatives": self.recommended_alternatives,
            "analysis_confidence": self.analysis_confidence,
            "analysis_duration_ms": self.analysis_duration_ms
        }


# Scope mappings for tools
TOOL_SCOPE_MAP = {
    "send_gmail": {
        "full_scopes": [
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.compose"
        ],
        "minimal_scopes": ["https://www.googleapis.com/auth/gmail.send"],
        "service": "gmail"
    },
    "read_gmail": {
        "full_scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
        "minimal_scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
        "service": "gmail"
    },
    "upload_to_drive": {
        "full_scopes": ["https://www.googleapis.com/auth/drive"],
        "minimal_scopes": ["https://www.googleapis.com/auth/drive.file"],
        "service": "drive"
    },
    "list_drive_files": {
        "full_scopes": ["https://www.googleapis.com/auth/drive.readonly"],
        "minimal_scopes": ["https://www.googleapis.com/auth/drive.metadata.readonly"],
        "service": "drive"
    },
    "create_calendar_event": {
        "full_scopes": ["https://www.googleapis.com/auth/calendar"],
        "minimal_scopes": ["https://www.googleapis.com/auth/calendar.events"],
        "service": "calendar"
    },
    "send_slack_message": {
        "full_scopes": ["chat:write", "channels:read"],
        "minimal_scopes": ["chat:write"],
        "service": "slack"
    },
    "browser_login": {
        "full_scopes": [],
        "minimal_scopes": [],
        "service": "browser"
    },
    "browser_download_file": {
        "full_scopes": [],
        "minimal_scopes": [],
        "service": "browser"
    },
    "complete_leetcode_daily": {
        "full_scopes": [],
        "minimal_scopes": [],
        "service": "leetcode"
    }
}

# Default risk levels for known tools
TOOL_RISK_LEVELS = {
    "read_gmail": RiskLevel.LOW,
    "list_drive_files": RiskLevel.LOW,
    "summarize_text": RiskLevel.LOW,
    "send_gmail": RiskLevel.HIGH,
    "upload_to_drive": RiskLevel.HIGH,
    "create_calendar_event": RiskLevel.MEDIUM,
    "send_slack_message": RiskLevel.HIGH,
    "browser_login": RiskLevel.CRITICAL,
    "browser_download_file": RiskLevel.HIGH,
    "complete_leetcode_daily": RiskLevel.HIGH,
    "openclaw_generate": RiskLevel.LOW,
    "openclaw_chat": RiskLevel.LOW,
}


def _build_analysis_prompt(tool_name: str, params: Dict[str, Any]) -> str:
    """Build the analysis prompt for OpenClaw"""
    
    # Sanitize params for prompt (remove sensitive data)
    safe_params = {}
    for key, value in params.items():
        if key in ["password", "token", "secret", "api_key", "auth"]:
            safe_params[key] = "[REDACTED]"
        elif isinstance(value, str) and len(value) > 200:
            safe_params[key] = value[:200] + "..."
        else:
            safe_params[key] = value
    
    params_json = json.dumps(safe_params, indent=2)
    
    return f"""You are a security analyst for an AI agent system. Analyze the following action request and provide a security assessment.

TOOL: {tool_name}
PARAMETERS:
{params_json}

Provide your analysis in the following JSON format ONLY (no other text):
{{
    "minimal_scopes": ["list of minimal OAuth scopes needed"],
    "plain_english_explanation": "A clear, non-technical explanation of what this action will do, written for an end-user who needs to approve it. Be specific about what data will be accessed or modified.",
    "risk_level": "low|medium|high|critical",
    "action_summary": "One-line summary of the action",
    "potential_impacts": ["List of potential impacts or side effects"],
    "recommended_alternatives": ["Optional: safer alternatives if risk is high"]
}}

Guidelines:
- For "minimal_scopes": List ONLY the minimum OAuth scopes required. Use exact scope strings.
- For "plain_english_explanation": Write 2-3 sentences explaining what happens when approved. Mention specific recipients, channels, or locations.
- For "risk_level": 
  - "low": Read-only operations on non-sensitive data
  - "medium": Read operations on sensitive data OR creating non-public content
  - "high": Sending messages, uploading files, external communications
  - "critical": Login operations, financial actions, destructive/irreversible operations
- For "potential_impacts": List what could go wrong or what effects this will have
- For "recommended_alternatives": Only include if there's a safer way to accomplish the goal

Respond with ONLY the JSON object, no additional text."""


def _parse_analysis_response(response: str, tool_name: str, params: Dict[str, Any]) -> ConsentGuardianAnalysis:
    """Parse the OpenClaw response into a ConsentGuardianAnalysis object"""
    
    # Get defaults from our mapping
    tool_info = TOOL_SCOPE_MAP.get(tool_name, {"minimal_scopes": [], "full_scopes": []})
    default_risk = TOOL_RISK_LEVELS.get(tool_name, RiskLevel.MEDIUM)
    
    try:
        # Try to extract JSON from response
        response_text = response.strip()
        
        # Handle potential markdown code blocks
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        
        analysis = json.loads(response_text)
        
        # Parse risk level
        risk_str = analysis.get("risk_level", default_risk.value).lower()
        try:
            risk_level = RiskLevel(risk_str)
        except ValueError:
            risk_level = default_risk
        
        return ConsentGuardianAnalysis(
            minimal_scopes=analysis.get("minimal_scopes", tool_info.get("minimal_scopes", [])),
            plain_english_explanation=analysis.get("plain_english_explanation", 
                f"The agent wants to execute '{tool_name}' with the provided parameters."),
            risk_level=risk_level,
            tool_name=tool_name,
            action_summary=analysis.get("action_summary", f"Execute {tool_name}"),
            potential_impacts=analysis.get("potential_impacts", []),
            recommended_alternatives=analysis.get("recommended_alternatives"),
            analysis_confidence=0.85
        )
        
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Failed to parse OpenClaw response: {e}, using defaults")
        
        # Build a reasonable default explanation
        explanation = _build_default_explanation(tool_name, params)
        
        return ConsentGuardianAnalysis(
            minimal_scopes=tool_info.get("minimal_scopes", []),
            plain_english_explanation=explanation,
            risk_level=default_risk,
            tool_name=tool_name,
            action_summary=f"Execute {tool_name}",
            potential_impacts=[f"Action '{tool_name}' will be performed"],
            analysis_confidence=0.5
        )


def _build_default_explanation(tool_name: str, params: Dict[str, Any]) -> str:
    """Build a default explanation when OpenClaw analysis fails"""
    
    explanations = {
        "send_gmail": lambda p: f"Send an email to {p.get('to', 'recipient')} with subject '{p.get('subject', 'No subject')}'",
        "read_gmail": lambda p: f"Read your {p.get('count', 10)} most recent emails",
        "upload_to_drive": lambda p: f"Upload a file to Google Drive at {p.get('file_path', 'specified location')}",
        "list_drive_files": lambda p: "List files in your Google Drive",
        "create_calendar_event": lambda p: f"Create a calendar event '{p.get('title', 'Untitled event')}'",
        "send_slack_message": lambda p: f"Send a message to Slack channel {p.get('channel', '#general')}",
        "browser_login": lambda p: f"Log into website {p.get('url', 'specified URL')} using browser automation",
        "browser_download_file": lambda p: "Download a file using browser automation",
        "complete_leetcode_daily": lambda p: f"Submit a LeetCode solution in {p.get('language', 'Python')}",
    }
    
    builder = explanations.get(tool_name)
    if builder:
        try:
            return builder(params)
        except:
            pass
    
    return f"Execute the '{tool_name}' action with the specified parameters."


def analyze_action_with_openclaw(
    tool_name: str,
    params: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> ConsentGuardianAnalysis:
    """
    Analyze an agent action using OpenClaw for intelligent consent recommendations.
    
    This is the main entry point for the Consent Guardian feature. It:
    1. Builds an analysis prompt with the action details
    2. Calls OpenClaw (local LLM) for security analysis
    3. Parses the response into structured recommendations
    4. Falls back to rule-based defaults if LLM fails
    
    Args:
        tool_name: Name of the tool to be executed
        params: Parameters for the tool execution
        user_context: Optional Auth0 user context for personalization
    
    Returns:
        ConsentGuardianAnalysis with minimal_scopes, explanation, and risk_level
    """
    start_time = time.time()
    
    logger.info(f"Consent Guardian analyzing action: {tool_name}")
    
    try:
        bridge = get_openclaw_bridge()
        
        # Check if OpenClaw is available
        health = bridge.health_check()
        if not health.get("healthy"):
            logger.warning("OpenClaw not available, using rule-based analysis")
            analysis = _build_fallback_analysis(tool_name, params)
            duration_ms = int((time.time() - start_time) * 1000)
            analysis.analysis_duration_ms = duration_ms
            track_consent_guardian_activation(tool_name, analysis.risk_level.value, "fallback")
            return analysis
        
        # Build and send analysis prompt
        prompt = _build_analysis_prompt(tool_name, params)
        
        # Create a minimal user context for OpenClaw if none provided
        analysis_context = user_context or {"sub": "consent_guardian_system"}
        
        result = bridge.generate(
            user_context=analysis_context,
            prompt=prompt,
            model="llama3",  # Use default model
            options={"temperature": 0.3}  # Lower temperature for more consistent analysis
        )
        
        if result.get("success"):
            response_text = result.get("response", "")
            analysis = _parse_analysis_response(response_text, tool_name, params)
        else:
            logger.warning(f"OpenClaw generation failed: {result.get('error')}")
            analysis = _build_fallback_analysis(tool_name, params)
        
        duration_ms = int((time.time() - start_time) * 1000)
        analysis.analysis_duration_ms = duration_ms
        
        # Track metric
        track_consent_guardian_activation(tool_name, analysis.risk_level.value, "analyzed")
        
        logger.info(f"Consent Guardian analysis complete: risk={analysis.risk_level.value}, "
                   f"scopes={len(analysis.minimal_scopes)}, duration={duration_ms}ms")
        
        return analysis
        
    except Exception as e:
        logger.error(f"Consent Guardian error: {e}")
        analysis = _build_fallback_analysis(tool_name, params)
        duration_ms = int((time.time() - start_time) * 1000)
        analysis.analysis_duration_ms = duration_ms
        track_consent_guardian_activation(tool_name, analysis.risk_level.value, "error")
        return analysis


def _build_fallback_analysis(tool_name: str, params: Dict[str, Any]) -> ConsentGuardianAnalysis:
    """Build a rule-based fallback analysis when OpenClaw is unavailable"""
    
    tool_info = TOOL_SCOPE_MAP.get(tool_name, {"minimal_scopes": [], "full_scopes": []})
    risk_level = TOOL_RISK_LEVELS.get(tool_name, RiskLevel.MEDIUM)
    
    explanation = _build_default_explanation(tool_name, params)
    
    # Build impacts based on risk level
    impacts = []
    if risk_level == RiskLevel.LOW:
        impacts = ["Read-only access to specified data"]
    elif risk_level == RiskLevel.MEDIUM:
        impacts = ["Data will be created or modified", "Changes are typically reversible"]
    elif risk_level == RiskLevel.HIGH:
        impacts = ["External communication will be sent", "Action may be visible to others", 
                   "Consider reviewing carefully before approval"]
    else:  # CRITICAL
        impacts = ["This action may have significant consequences", 
                   "Authentication credentials may be used",
                   "Action may be irreversible"]
    
    return ConsentGuardianAnalysis(
        minimal_scopes=tool_info.get("minimal_scopes", []),
        plain_english_explanation=explanation,
        risk_level=risk_level,
        tool_name=tool_name,
        action_summary=f"Execute {tool_name}",
        potential_impacts=impacts,
        analysis_confidence=0.7
    )


def get_minimal_scopes_for_tool(tool_name: str) -> List[str]:
    """Get the minimal required scopes for a tool"""
    tool_info = TOOL_SCOPE_MAP.get(tool_name, {})
    return tool_info.get("minimal_scopes", [])


def is_high_stakes_action(tool_name: str) -> bool:
    """Check if a tool is considered high-stakes requiring approval"""
    risk = TOOL_RISK_LEVELS.get(tool_name, RiskLevel.MEDIUM)
    return risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]


# Register as a tool for potential direct agent use
from registry.tool_registry import tool_registry

def consent_guardian_analyze(user_context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Agent tool wrapper for Consent Guardian analysis"""
    tool_name = params.get("tool_name", "unknown")
    tool_params = params.get("tool_params", {})
    
    analysis = analyze_action_with_openclaw(tool_name, tool_params, user_context)
    return analysis.to_dict()

tool_registry.register("consent_guardian_analyze", consent_guardian_analyze)
