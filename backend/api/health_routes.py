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