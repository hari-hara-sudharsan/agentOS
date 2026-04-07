"""
Prometheus Metrics for AgentOS
Custom metrics for monitoring Token Vault, agent operations, and system health
"""
from prometheus_client import (
    Counter, Histogram, Gauge, Info,
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, multiprocess, REGISTRY
)
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)

# =====================================
# Custom Registry for AgentOS
# =====================================
# Use default registry for simplicity
registry = REGISTRY

# =====================================
# Token Vault Metrics
# =====================================
TOKEN_VAULT_EXCHANGE_TOTAL = Counter(
    'agentos_token_vault_exchange_total',
    'Total number of Token Vault exchange operations',
    ['provider', 'status'],
    registry=registry
)

TOKEN_VAULT_EXCHANGE_DURATION = Histogram(
    'agentos_token_vault_exchange_duration_seconds',
    'Duration of Token Vault exchange operations',
    ['provider'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry
)

TOKEN_VAULT_ERRORS = Counter(
    'agentos_token_vault_errors_total',
    'Total Token Vault errors by type',
    ['provider', 'error_type'],
    registry=registry
)

# =====================================
# Step-Up / CIBA Authentication Metrics
# =====================================
STEPUP_REQUESTS_TOTAL = Counter(
    'agentos_stepup_requests_total',
    'Total step-up authentication requests',
    ['tool', 'status'],
    registry=registry
)

STEPUP_APPROVAL_LATENCY = Histogram(
    'agentos_stepup_approval_latency_seconds',
    'Time from step-up request to user approval',
    ['tool'],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
    registry=registry
)

CIBA_PENDING_APPROVALS = Gauge(
    'agentos_ciba_pending_approvals',
    'Number of pending CIBA approval requests',
    registry=registry
)

# =====================================
# Agent Tool Execution Metrics
# =====================================
TOOL_CALLS_TOTAL = Counter(
    'agentos_tool_calls_total',
    'Total tool calls by tool name and status',
    ['tool', 'provider', 'status'],
    registry=registry
)

TOOL_EXECUTION_DURATION = Histogram(
    'agentos_tool_execution_duration_seconds',
    'Tool execution duration',
    ['tool', 'provider'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
    registry=registry
)

TOOL_ERRORS = Counter(
    'agentos_tool_errors_total',
    'Tool execution errors by type',
    ['tool', 'provider', 'error_type'],
    registry=registry
)

# =====================================
# OpenClaw Bridge Metrics
# =====================================
OPENCLAW_REQUESTS_TOTAL = Counter(
    'agentos_openclaw_requests_total',
    'Total OpenClaw bridge requests',
    ['action', 'status'],
    registry=registry
)

OPENCLAW_LATENCY = Histogram(
    'agentos_openclaw_latency_seconds',
    'OpenClaw request latency',
    ['action'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry
)

OPENCLAW_ACTIVE_SESSIONS = Gauge(
    'agentos_openclaw_active_sessions',
    'Number of active OpenClaw sessions',
    registry=registry
)

# =====================================
# Consent Guardian Metrics
# =====================================
CONSENT_GUARDIAN_ACTIVATIONS = Counter(
    'agentos_consent_guardian_activations_total',
    'Total Consent Guardian activations',
    ['tool', 'risk_level', 'analysis_type'],
    registry=registry
)

CONSENT_GUARDIAN_DECISIONS = Counter(
    'agentos_consent_guardian_decisions_total',
    'User decisions after Consent Guardian analysis',
    ['tool', 'risk_level', 'decision'],
    registry=registry
)

CONSENT_GUARDIAN_LATENCY = Histogram(
    'agentos_consent_guardian_latency_seconds',
    'Consent Guardian analysis latency',
    ['tool'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry
)

CONSENT_GUARDIAN_SCOPE_REDUCTION = Counter(
    'agentos_consent_guardian_scope_reductions_total',
    'Number of times Consent Guardian recommended reduced scopes',
    ['tool', 'service'],
    registry=registry
)

# =====================================
# Scope Weaver Metrics
# =====================================
SCOPE_WEAVER_ACTIVATIONS = Counter(
    'agentos_scope_weaver_activations_total',
    'Total Scope Weaver activations',
    ['tool', 'risk_level', 'analysis_type'],
    registry=registry
)

SCOPE_WEAVER_EVOLUTION_AVG = Gauge(
    'agentos_scope_weaver_evolution_avg',
    'Average scope evolution score (0-100, higher = more scope reduction)',
    registry=registry
)

SCOPE_WEAVER_LATENCY = Histogram(
    'agentos_scope_weaver_latency_seconds',
    'Scope Weaver analysis latency',
    ['tool'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry
)

SCOPE_WEAVER_APPROVALS = Counter(
    'agentos_scope_weaver_approvals_total',
    'User approvals after Scope Weaver recommendation',
    ['tool', 'risk_level', 'decision'],
    registry=registry
)

# Internal state for calculating rolling average
_scope_evolution_values = []
_MAX_EVOLUTION_SAMPLES = 100

# =====================================
# Shadow Simulator Metrics
# =====================================
SHADOW_SIMULATION_TOTAL = Counter(
    'agentos_shadow_simulation_total',
    'Total shadow simulations run',
    ['tool', 'outcome', 'analysis_type'],
    registry=registry
)

SHADOW_SIMULATION_DURATION = Histogram(
    'agentos_shadow_simulation_duration_seconds',
    'Shadow simulation duration',
    ['tool'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry
)

RISK_PREVENTED_TOTAL = Counter(
    'agentos_risk_prevented_total',
    'Total high-risk actions prevented/warned by Shadow Simulator',
    ['tool'],
    registry=registry
)

RISK_PREVENTED_COUNT = Counter(
    'agentos_risk_prevented_count',
    'Count of individual risks identified and potentially prevented',
    ['tool'],
    registry=registry
)

SHADOW_SIMULATION_DECISIONS = Counter(
    'agentos_shadow_simulation_decisions_total',
    'User decisions after shadow simulation',
    ['tool', 'outcome', 'decision'],
    registry=registry
)

SHADOW_SIMULATION_CONFIDENCE_AVG = Gauge(
    'agentos_shadow_simulation_confidence_avg',
    'Average confidence score of shadow simulations (0-100)',
    registry=registry
)

# Internal state for confidence average
_simulation_confidence_values = []
_MAX_CONFIDENCE_SAMPLES = 100

# =====================================
# Browser Automation Metrics
# =====================================
BROWSER_TASKS_TOTAL = Counter(
    'agentos_browser_tasks_total',
    'Total browser automation tasks',
    ['task_type', 'status'],
    registry=registry
)

BROWSER_TASK_DURATION = Histogram(
    'agentos_browser_task_duration_seconds',
    'Browser task duration',
    ['task_type'],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0),
    registry=registry
)

# =====================================
# API Request Metrics
# =====================================
HTTP_REQUESTS_TOTAL = Counter(
    'agentos_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

HTTP_REQUEST_DURATION = Histogram(
    'agentos_http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
    registry=registry
)

# =====================================
# System Health Metrics
# =====================================
SYSTEM_INFO = Info(
    'agentos_system',
    'AgentOS system information',
    registry=registry
)

ACTIVE_EXECUTIONS = Gauge(
    'agentos_active_executions',
    'Number of active agent executions',
    registry=registry
)

# =====================================
# Helper Functions & Decorators
# =====================================

def track_token_vault_exchange(provider: str):
    """Decorator to track Token Vault exchange operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                TOKEN_VAULT_EXCHANGE_TOTAL.labels(provider=provider, status='success').inc()
                return result
            except Exception as e:
                TOKEN_VAULT_EXCHANGE_TOTAL.labels(provider=provider, status='failure').inc()
                TOKEN_VAULT_ERRORS.labels(
                    provider=provider, 
                    error_type=type(e).__name__
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                TOKEN_VAULT_EXCHANGE_DURATION.labels(provider=provider).observe(duration)
        return wrapper
    return decorator


def track_tool_execution(tool: str, provider: str = 'internal'):
    """Decorator to track tool execution metrics"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            ACTIVE_EXECUTIONS.inc()
            try:
                result = func(*args, **kwargs)
                TOOL_CALLS_TOTAL.labels(tool=tool, provider=provider, status='success').inc()
                return result
            except Exception as e:
                TOOL_CALLS_TOTAL.labels(tool=tool, provider=provider, status='failure').inc()
                TOOL_ERRORS.labels(
                    tool=tool,
                    provider=provider,
                    error_type=type(e).__name__
                ).inc()
                raise
            finally:
                ACTIVE_EXECUTIONS.dec()
                duration = time.time() - start_time
                TOOL_EXECUTION_DURATION.labels(tool=tool, provider=provider).observe(duration)
        return wrapper
    return decorator


def track_stepup_request(tool: str):
    """Track step-up authentication request"""
    STEPUP_REQUESTS_TOTAL.labels(tool=tool, status='initiated').inc()


def track_stepup_approval(tool: str, approved: bool, latency_seconds: float):
    """Track step-up approval completion"""
    status = 'approved' if approved else 'denied'
    STEPUP_REQUESTS_TOTAL.labels(tool=tool, status=status).inc()
    STEPUP_APPROVAL_LATENCY.labels(tool=tool).observe(latency_seconds)


def track_openclaw_request(action: str, status: str, duration: float):
    """Track OpenClaw bridge request"""
    OPENCLAW_REQUESTS_TOTAL.labels(action=action, status=status).inc()
    OPENCLAW_LATENCY.labels(action=action).observe(duration)


def track_browser_task(task_type: str, status: str, duration: float):
    """Track browser automation task"""
    BROWSER_TASKS_TOTAL.labels(task_type=task_type, status=status).inc()
    BROWSER_TASK_DURATION.labels(task_type=task_type).observe(duration)


def track_consent_guardian_activation(tool: str, risk_level: str, analysis_type: str):
    """Track Consent Guardian activation"""
    CONSENT_GUARDIAN_ACTIVATIONS.labels(
        tool=tool, 
        risk_level=risk_level, 
        analysis_type=analysis_type
    ).inc()


def track_consent_guardian_decision(tool: str, risk_level: str, decision: str, latency: float = 0):
    """Track user decision after Consent Guardian analysis"""
    CONSENT_GUARDIAN_DECISIONS.labels(
        tool=tool, 
        risk_level=risk_level, 
        decision=decision
    ).inc()
    if latency > 0:
        CONSENT_GUARDIAN_LATENCY.labels(tool=tool).observe(latency)


def track_consent_guardian_scope_reduction(tool: str, service: str):
    """Track when Consent Guardian recommends reduced scopes"""
    CONSENT_GUARDIAN_SCOPE_REDUCTION.labels(tool=tool, service=service).inc()


def track_scope_weaver_activation(tool: str, risk_level: str, analysis_type: str):
    """Track Scope Weaver activation"""
    SCOPE_WEAVER_ACTIVATIONS.labels(
        tool=tool,
        risk_level=risk_level,
        analysis_type=analysis_type
    ).inc()


def track_scope_evolution(evolution_score: int):
    """
    Track scope evolution score and update rolling average.
    
    Args:
        evolution_score: 0-100 representing percentage of scope reduction
    """
    global _scope_evolution_values
    
    _scope_evolution_values.append(evolution_score)
    
    # Keep only last N samples
    if len(_scope_evolution_values) > _MAX_EVOLUTION_SAMPLES:
        _scope_evolution_values = _scope_evolution_values[-_MAX_EVOLUTION_SAMPLES:]
    
    # Update gauge with rolling average
    if _scope_evolution_values:
        avg = sum(_scope_evolution_values) / len(_scope_evolution_values)
        SCOPE_WEAVER_EVOLUTION_AVG.set(avg)


def track_scope_weaver_approval(tool: str, risk_level: str, decision: str, latency: float = 0):
    """Track user decision after Scope Weaver recommendation"""
    SCOPE_WEAVER_APPROVALS.labels(
        tool=tool,
        risk_level=risk_level,
        decision=decision
    ).inc()
    if latency > 0:
        SCOPE_WEAVER_LATENCY.labels(tool=tool).observe(latency)


# =====================================
# Shadow Simulator Tracking Functions
# =====================================
def track_shadow_simulation(tool: str, outcome: str, analysis_type: str):
    """Track Shadow Simulator activation"""
    SHADOW_SIMULATION_TOTAL.labels(
        tool=tool,
        outcome=outcome,
        analysis_type=analysis_type
    ).inc()


def track_shadow_simulation_duration(tool: str, duration_seconds: float):
    """Track Shadow Simulator analysis duration"""
    SHADOW_SIMULATION_DURATION.labels(tool=tool).observe(duration_seconds)


def track_risk_prevented(tool: str, risk_count: int = 1):
    """
    Track when high-risk actions are identified by Shadow Simulator.
    
    This metric helps measure how many potentially dangerous actions
    were caught before execution.
    """
    RISK_PREVENTED_TOTAL.labels(tool=tool).inc()
    RISK_PREVENTED_COUNT.labels(tool=tool).inc(risk_count)


def track_shadow_simulation_decision(tool: str, outcome: str, decision: str):
    """
    Track user decision after seeing shadow simulation results.
    
    Args:
        tool: Name of the tool that was simulated
        outcome: Simulation outcome (success, caution, warning, blocked)
        decision: User decision (executed, cancelled, modified)
    """
    SHADOW_SIMULATION_DECISIONS.labels(
        tool=tool,
        outcome=outcome,
        decision=decision
    ).inc()


def track_simulation_confidence(confidence_score: float):
    """
    Track simulation confidence and update rolling average.
    
    Args:
        confidence_score: 0-100 confidence of the simulation
    """
    global _simulation_confidence_values
    
    _simulation_confidence_values.append(confidence_score)
    
    # Keep only last N samples
    if len(_simulation_confidence_values) > _MAX_CONFIDENCE_SAMPLES:
        _simulation_confidence_values = _simulation_confidence_values[-_MAX_CONFIDENCE_SAMPLES:]
    
    # Update gauge with rolling average
    if _simulation_confidence_values:
        avg = sum(_simulation_confidence_values) / len(_simulation_confidence_values)
        SHADOW_SIMULATION_CONFIDENCE_AVG.set(avg)


def set_pending_approvals(count: int):
    """Set number of pending CIBA approvals"""
    CIBA_PENDING_APPROVALS.set(count)


def set_openclaw_sessions(count: int):
    """Set number of active OpenClaw sessions"""
    OPENCLAW_ACTIVE_SESSIONS.set(count)


def set_system_info(version: str, environment: str):
    """Set system information"""
    SYSTEM_INFO.info({
        'version': version,
        'environment': environment,
        'framework': 'fastapi'
    })


def get_metrics():
    """Generate Prometheus metrics output"""
    return generate_latest(registry)


def get_metrics_content_type():
    """Get Prometheus content type"""
    return CONTENT_TYPE_LATEST


# =====================================
# FastAPI Middleware for HTTP Metrics
# =====================================
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to track HTTP request metrics"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get endpoint path (normalize dynamic segments)
        path = request.url.path
        # Normalize paths like /api/users/123 to /api/users/{id}
        normalized_path = self._normalize_path(path)
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                endpoint=normalized_path,
                status_code=str(status_code)
            ).inc()
            HTTP_REQUEST_DURATION.labels(
                method=request.method,
                endpoint=normalized_path
            ).observe(duration)
        
        return response
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path to reduce cardinality"""
        # Replace UUIDs
        import re
        path = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '{id}',
            path
        )
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        return path


# Initialize system info on module load
set_system_info(version='1.0.0', environment='development')
