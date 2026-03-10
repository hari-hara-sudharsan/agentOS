import time
from fastapi import APIRouter

router = APIRouter()

START_TIME = time.time()

@router.get("/")
def health():

    uptime = time.time() - START_TIME

    return {
        "status": "healthy",
        "service": "AgentOS",
        "uptime_seconds": round(uptime)
    }

@router.get("/ready")
def readiness():

    return {
        "status": "ready",
        "agents": [
            "planner_agent",
            "api_agent",
            "browser_agent"
        ]
    }

@router.get("/version")
def version():

    return {
        "app": "AgentOS",
        "version": "1.0.0"
    }