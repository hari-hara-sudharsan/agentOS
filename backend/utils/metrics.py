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
