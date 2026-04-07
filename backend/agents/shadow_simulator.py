"""
Shadow Simulator - Pre-Execution Safety Layer with OpenClaw AI

This module implements the Shadow Simulator pattern: before any high-stakes
external tool executes, it clones the current graph state and runs a parallel
simulation using OpenClaw to predict outcomes and identify risks.

Key Innovation:
- Runs parallel "what-if" simulation before actual execution
- Returns predicted_actions[], possible_risks[], safer_alternatives[], confidence_score
- Integrates with frontend "What-If Preview" modal
- Only allows Token Vault exchange after user explicitly confirms "Execute for Real"
- Logs all simulations to Prometheus for risk analytics

Security:
- OpenClaw remains sandboxed (local LLM only)
- Never stores raw tokens or secrets
- All simulations are logged for audit (non-sensitive data only)
- Token Vault exchange happens ONLY after explicit user confirmation
"""
import logging
import json
import time
import copy
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from agents.openclaw_bridge import get_openclaw_bridge
from utils.metrics import (
    track_shadow_simulation,
    track_risk_prevented,
    SHADOW_SIMULATION_TOTAL,
    SHADOW_SIMULATION_DURATION
)

logger = logging.getLogger(__name__)


class SimulationOutcome(str, Enum):
    """Possible simulation outcomes"""
    SUCCESS = "success"        # Action likely to succeed with no issues
    CAUTION = "caution"        # Action may have unintended effects
    WARNING = "warning"        # Significant risks detected
    BLOCKED = "blocked"        # Action should not proceed


class RiskCategory(str, Enum):
    """Categories of risks that can be detected"""
    DATA_EXPOSURE = "data_exposure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    IRREVERSIBLE_ACTION = "irreversible_action"
    SCOPE_OVERREACH = "scope_overreach"
    RATE_LIMIT = "rate_limit"
    EXTERNAL_COMMUNICATION = "external_communication"
    FINANCIAL_IMPACT = "financial_impact"
    PRIVACY_VIOLATION = "privacy_violation"


@dataclass
class PredictedAction:
    """A predicted action in the simulation"""
    action_name: str
    description: str
    probability: float  # 0-1 probability of this action occurring
    is_reversible: bool = True
    external_service: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_name": self.action_name,
            "description": self.description,
            "probability": self.probability,
            "is_reversible": self.is_reversible,
            "external_service": self.external_service
        }


@dataclass
class IdentifiedRisk:
    """A risk identified during simulation"""
    risk_category: RiskCategory
    severity: str  # low, medium, high, critical
    description: str
    mitigation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_category": self.risk_category.value,
            "severity": self.severity,
            "description": self.description,
            "mitigation": self.mitigation
        }


@dataclass
class SaferAlternative:
    """A safer alternative to the proposed action"""
    action_name: str
    description: str
    risk_reduction: str  # Brief description of what risks it avoids
    tradeoffs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_name": self.action_name,
            "description": self.description,
            "risk_reduction": self.risk_reduction,
            "tradeoffs": self.tradeoffs
        }


@dataclass
class ShadowSimulationResult:
    """
    Complete result of a shadow simulation.
    
    This is what gets displayed in the frontend "What-If Preview" modal.
    """
    simulation_id: str
    tool_name: str
    outcome: SimulationOutcome
    predicted_actions: List[PredictedAction]
    possible_risks: List[IdentifiedRisk]
    safer_alternatives: List[SaferAlternative]
    confidence_score: float  # 0-100, how confident the simulation is
    explanation: str  # Human-readable explanation of the simulation
    simulation_duration_ms: int = 0
    graph_state_snapshot: Optional[Dict[str, Any]] = None  # Non-sensitive state info
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "tool_name": self.tool_name,
            "outcome": self.outcome.value,
            "predicted_actions": [a.to_dict() for a in self.predicted_actions],
            "possible_risks": [r.to_dict() for r in self.possible_risks],
            "safer_alternatives": [s.to_dict() for s in self.safer_alternatives],
            "confidence_score": self.confidence_score,
            "explanation": self.explanation,
            "simulation_duration_ms": self.simulation_duration_ms
        }
    
    @property
    def has_high_risks(self) -> bool:
        """Check if any high or critical risks were identified"""
        return any(
            r.severity in ("high", "critical") 
            for r in self.possible_risks
        )
    
    @property
    def risk_count(self) -> int:
        return len(self.possible_risks)


# Tools that require shadow simulation (high-stakes)
HIGH_STAKES_TOOLS = {
    "send_gmail",
    "send_slack_message",
    "upload_to_drive",
    "create_calendar_event",
    "delete_file",
    "post_to_social",
    "browser_login",
    "browser_submit_form",
    "complete_leetcode_daily",
    "create_github_issue",
    "merge_pull_request",
    "deploy_application"
}


def _generate_simulation_id() -> str:
    """Generate unique simulation ID"""
    import uuid
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"sim_{timestamp}_{short_uuid}"


def _build_simulation_prompt(
    tool_name: str,
    params: Dict[str, Any],
    graph_state: Optional[Dict[str, Any]] = None
) -> str:
    """Build the simulation prompt for OpenClaw"""
    
    # Sanitize params (remove any sensitive data)
    safe_params = {}
    for key, value in params.items():
        if key in ["password", "token", "secret", "api_key", "auth", "access_token", "refresh_token"]:
            safe_params[key] = "[REDACTED]"
        elif isinstance(value, str) and len(value) > 300:
            safe_params[key] = value[:300] + "..."
        else:
            safe_params[key] = value
    
    params_json = json.dumps(safe_params, indent=2)
    
    # Build context from graph state if available
    context_info = ""
    if graph_state:
        safe_state = {
            "previous_actions": graph_state.get("previous_actions", [])[-5:],  # Last 5 actions
            "current_intent": graph_state.get("current_intent", "unknown"),
            "session_type": graph_state.get("session_type", "interactive")
        }
        context_info = f"\n\nCURRENT CONTEXT:\n{json.dumps(safe_state, indent=2)}"
    
    return f"""You are a security-focused AI that simulates the execution of actions BEFORE they happen. Your job is to predict what will happen and identify any risks.

TOOL TO SIMULATE: {tool_name}
PARAMETERS:
{params_json}
{context_info}

Analyze this action as if it were about to execute. Respond with ONLY a JSON object (no markdown, no other text):

{{
    "predicted_actions": [
        {{
            "action_name": "string - what will happen",
            "description": "1-2 sentences describing this action",
            "probability": 0.0-1.0,
            "is_reversible": true/false,
            "external_service": "name of external service or null"
        }}
    ],
    "possible_risks": [
        {{
            "risk_category": "data_exposure|unauthorized_access|irreversible_action|scope_overreach|rate_limit|external_communication|financial_impact|privacy_violation",
            "severity": "low|medium|high|critical",
            "description": "what could go wrong",
            "mitigation": "how to prevent/fix this"
        }}
    ],
    "safer_alternatives": [
        {{
            "action_name": "alternative action",
            "description": "what this alternative does",
            "risk_reduction": "what risks it avoids",
            "tradeoffs": ["list of tradeoffs"]
        }}
    ],
    "confidence_score": 0-100,
    "outcome": "success|caution|warning|blocked",
    "explanation": "2-3 sentence plain English explanation for a non-technical user about what this action will do and any concerns"
}}

GUIDELINES:
1. predicted_actions: List ALL actions that will occur, including API calls, data access, etc.
2. possible_risks: Be thorough but realistic. Don't invent risks that don't apply.
3. safer_alternatives: Only suggest if genuinely safer options exist.
4. confidence_score: 0-100 based on how certain you are about the prediction.
5. outcome: 
   - "success" = low risk, proceed normally
   - "caution" = minor risks, user should be aware
   - "warning" = significant risks, requires careful consideration
   - "blocked" = should not proceed without changes
6. explanation: Write for a non-technical user who needs to make a decision.

Respond with ONLY the JSON object."""


def _parse_simulation_response(
    response: str,
    tool_name: str,
    simulation_id: str
) -> ShadowSimulationResult:
    """Parse OpenClaw response into ShadowSimulationResult"""
    
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
        
        data = json.loads(response_text)
        
        # Parse predicted actions
        predicted_actions = []
        for action in data.get("predicted_actions", []):
            predicted_actions.append(PredictedAction(
                action_name=action.get("action_name", "Unknown action"),
                description=action.get("description", ""),
                probability=float(action.get("probability", 0.5)),
                is_reversible=action.get("is_reversible", True),
                external_service=action.get("external_service")
            ))
        
        # Parse risks
        possible_risks = []
        for risk in data.get("possible_risks", []):
            try:
                risk_category = RiskCategory(risk.get("risk_category", "scope_overreach"))
            except ValueError:
                risk_category = RiskCategory.SCOPE_OVERREACH
            
            possible_risks.append(IdentifiedRisk(
                risk_category=risk_category,
                severity=risk.get("severity", "medium"),
                description=risk.get("description", ""),
                mitigation=risk.get("mitigation")
            ))
        
        # Parse safer alternatives
        safer_alternatives = []
        for alt in data.get("safer_alternatives", []):
            safer_alternatives.append(SaferAlternative(
                action_name=alt.get("action_name", ""),
                description=alt.get("description", ""),
                risk_reduction=alt.get("risk_reduction", ""),
                tradeoffs=alt.get("tradeoffs", [])
            ))
        
        # Parse outcome
        try:
            outcome = SimulationOutcome(data.get("outcome", "caution"))
        except ValueError:
            outcome = SimulationOutcome.CAUTION
        
        # Parse confidence
        confidence = data.get("confidence_score", 50)
        if not isinstance(confidence, (int, float)):
            try:
                confidence = float(confidence)
            except:
                confidence = 50
        confidence = max(0, min(100, confidence))
        
        return ShadowSimulationResult(
            simulation_id=simulation_id,
            tool_name=tool_name,
            outcome=outcome,
            predicted_actions=predicted_actions,
            possible_risks=possible_risks,
            safer_alternatives=safer_alternatives,
            confidence_score=confidence,
            explanation=data.get("explanation", f"Simulation of '{tool_name}' completed.")
        )
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning(f"Failed to parse simulation response: {e}")
        return _build_fallback_simulation(tool_name, simulation_id)


def _build_fallback_simulation(
    tool_name: str,
    simulation_id: str,
    params: Optional[Dict[str, Any]] = None
) -> ShadowSimulationResult:
    """Build rule-based fallback when OpenClaw is unavailable"""
    
    # Default predictions based on tool type
    predicted_actions = [
        PredictedAction(
            action_name=f"Execute {tool_name}",
            description=f"The {tool_name} tool will be invoked with the provided parameters.",
            probability=1.0,
            is_reversible="delete" not in tool_name.lower(),
            external_service=_get_external_service(tool_name)
        )
    ]
    
    # Default risk assessment based on tool
    risks = []
    outcome = SimulationOutcome.CAUTION
    
    if tool_name in ["send_gmail", "send_slack_message"]:
        risks.append(IdentifiedRisk(
            risk_category=RiskCategory.EXTERNAL_COMMUNICATION,
            severity="high",
            description="This action will send a message to external recipients.",
            mitigation="Review recipient and content before proceeding."
        ))
        outcome = SimulationOutcome.WARNING
    
    if "delete" in tool_name.lower():
        risks.append(IdentifiedRisk(
            risk_category=RiskCategory.IRREVERSIBLE_ACTION,
            severity="critical",
            description="This action cannot be undone.",
            mitigation="Ensure you have backups before proceeding."
        ))
        outcome = SimulationOutcome.WARNING
    
    if tool_name in ["browser_login", "browser_submit_form"]:
        risks.append(IdentifiedRisk(
            risk_category=RiskCategory.UNAUTHORIZED_ACCESS,
            severity="high",
            description="Browser automation will interact with external websites.",
            mitigation="Verify the target URL is correct and trusted."
        ))
        outcome = SimulationOutcome.WARNING
    
    if not risks:
        risks.append(IdentifiedRisk(
            risk_category=RiskCategory.SCOPE_OVERREACH,
            severity="low",
            description="Standard tool execution with normal permissions.",
            mitigation="Review parameters before proceeding."
        ))
    
    return ShadowSimulationResult(
        simulation_id=simulation_id,
        tool_name=tool_name,
        outcome=outcome,
        predicted_actions=predicted_actions,
        possible_risks=risks,
        safer_alternatives=[],
        confidence_score=60,  # Lower confidence for fallback
        explanation=f"Simulation of '{tool_name}' completed using rule-based analysis. Please review the predicted actions and risks before proceeding."
    )


def _get_external_service(tool_name: str) -> Optional[str]:
    """Map tool name to external service"""
    service_map = {
        "send_gmail": "Gmail",
        "read_gmail": "Gmail",
        "upload_to_drive": "Google Drive",
        "list_drive_files": "Google Drive",
        "create_calendar_event": "Google Calendar",
        "send_slack_message": "Slack",
        "create_github_issue": "GitHub",
        "merge_pull_request": "GitHub",
        "browser_login": "Web Browser",
        "browser_submit_form": "Web Browser",
        "complete_leetcode_daily": "LeetCode"
    }
    return service_map.get(tool_name)


def requires_shadow_simulation(tool_name: str) -> bool:
    """Check if a tool requires shadow simulation"""
    return tool_name in HIGH_STAKES_TOOLS


def run_shadow_simulation(
    tool_name: str,
    params: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None,
    graph_state: Optional[Dict[str, Any]] = None
) -> ShadowSimulationResult:
    """
    Main entry point for Shadow Simulator.
    
    Runs a parallel simulation of the proposed action using OpenClaw AI
    to predict outcomes and identify risks before actual execution.
    
    Args:
        tool_name: Name of the tool to simulate
        params: Tool parameters (sensitive data will be redacted)
        user_context: Auth0 user context for audit logging
        graph_state: Current LangGraph state (will be cloned/sanitized)
    
    Returns:
        ShadowSimulationResult with predictions, risks, alternatives, and confidence
    """
    start_time = time.time()
    simulation_id = _generate_simulation_id()
    
    logger.info(f"Shadow Simulator starting: {simulation_id} for tool={tool_name}")
    
    try:
        bridge = get_openclaw_bridge()
        
        # Check OpenClaw availability
        health = bridge.health_check()
        if not health.get("healthy"):
            logger.warning("OpenClaw not available, using rule-based simulation")
            result = _build_fallback_simulation(tool_name, simulation_id, params)
            result.simulation_duration_ms = int((time.time() - start_time) * 1000)
            track_shadow_simulation(tool_name, result.outcome.value, "fallback")
            return result
        
        # Clone and sanitize graph state
        safe_graph_state = None
        if graph_state:
            safe_graph_state = _sanitize_graph_state(graph_state)
        
        # Build and send simulation prompt
        prompt = _build_simulation_prompt(tool_name, params, safe_graph_state)
        
        analysis_context = user_context or {"sub": "shadow_simulator_system"}
        
        result = bridge.generate(
            user_context=analysis_context,
            prompt=prompt,
            model="llama3",
            options={"temperature": 0.3}  # Slightly higher for creative risk analysis
        )
        
        if result.get("success"):
            response_text = result.get("response", "")
            simulation_result = _parse_simulation_response(response_text, tool_name, simulation_id)
        else:
            logger.warning(f"OpenClaw generation failed: {result.get('error')}")
            simulation_result = _build_fallback_simulation(tool_name, simulation_id, params)
        
        duration_ms = int((time.time() - start_time) * 1000)
        simulation_result.simulation_duration_ms = duration_ms
        
        # Track metrics
        track_shadow_simulation(tool_name, simulation_result.outcome.value, "analyzed")
        
        # Track risks prevented if user might not proceed
        if simulation_result.has_high_risks:
            track_risk_prevented(tool_name, simulation_result.risk_count)
        
        logger.info(
            f"Shadow Simulator complete: {simulation_id}, "
            f"tool={tool_name}, outcome={simulation_result.outcome.value}, "
            f"risks={simulation_result.risk_count}, "
            f"confidence={simulation_result.confidence_score}%, "
            f"duration={duration_ms}ms"
        )
        
        return simulation_result
        
    except Exception as e:
        logger.error(f"Shadow Simulator error: {e}")
        result = _build_fallback_simulation(tool_name, simulation_id, params)
        result.simulation_duration_ms = int((time.time() - start_time) * 1000)
        track_shadow_simulation(tool_name, result.outcome.value, "error")
        return result


def _sanitize_graph_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize graph state for simulation.
    
    Removes sensitive data while preserving useful context.
    """
    safe_state = {}
    
    # Copy only non-sensitive fields
    allowed_fields = [
        "previous_actions", "current_intent", "session_type",
        "tool_history", "message_count", "conversation_id"
    ]
    
    for field in allowed_fields:
        if field in state:
            value = state[field]
            # Deep sanitize lists
            if isinstance(value, list):
                safe_state[field] = [
                    _sanitize_dict(item) if isinstance(item, dict) else item
                    for item in value[-10:]  # Keep last 10 items max
                ]
            elif isinstance(value, dict):
                safe_state[field] = _sanitize_dict(value)
            else:
                safe_state[field] = value
    
    return safe_state


def _sanitize_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize a dictionary by removing sensitive keys"""
    sensitive_keys = {
        "password", "token", "secret", "api_key", "auth",
        "access_token", "refresh_token", "credential", "private_key"
    }
    
    return {
        k: "[REDACTED]" if k.lower() in sensitive_keys else v
        for k, v in d.items()
        if not isinstance(v, bytes)  # Skip binary data
    }


def store_simulation_result(
    user_id: str,
    simulation_result: ShadowSimulationResult,
    user_decision: str  # "executed", "cancelled", "modified"
) -> bool:
    """
    Store simulation result for analytics (non-sensitive data only).
    
    SECURITY: Never stores tokens or secrets.
    """
    from database.db import SessionLocal
    from database.models import ShadowSimulation
    
    db = SessionLocal()
    try:
        simulation = ShadowSimulation(
            simulation_id=simulation_result.simulation_id,
            user_id=user_id,
            tool_name=simulation_result.tool_name,
            outcome=simulation_result.outcome.value,
            risk_count=simulation_result.risk_count,
            has_high_risks=simulation_result.has_high_risks,
            confidence_score=simulation_result.confidence_score,
            user_decision=user_decision,
            simulation_duration_ms=simulation_result.simulation_duration_ms,
            explanation=simulation_result.explanation[:500]  # Truncate for storage
        )
        db.add(simulation)
        db.commit()
        logger.info(f"Stored simulation: {simulation_result.simulation_id} decision={user_decision}")
        return True
    except Exception as e:
        logger.error(f"Failed to store simulation: {e}")
        db.rollback()
        return False
    finally:
        db.close()


# Register as a tool for agent use
from registry.tool_registry import tool_registry

def shadow_simulator_tool(user_context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Agent tool wrapper for Shadow Simulator"""
    tool_name = params.get("tool_name", "unknown")
    tool_params = params.get("tool_params", {})
    graph_state = params.get("graph_state", None)
    
    result = run_shadow_simulation(tool_name, tool_params, user_context, graph_state)
    return result.to_dict()

tool_registry.register("run_shadow_simulation", shadow_simulator_tool)
